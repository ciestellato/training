import pandas as pd
import logging
import sqlite3
from sqlalchemy import text

from .database_setup import Engine # 初期化されたEngineをインポート
from edinet_config import Config # ConfigはDB_PATHなどに必要

"""責任範囲：データベースへのアクセス（永続化）処理。"""

# --- 1. サマリーデータの保管 ---

def store_document_summaries(summary_df: pd.DataFrame):
    """
    サマリーDataFrameをデータベースにUpsertする。
    テーブル: edinet_document_summaries
    """
    if summary_df.empty:
        logging.warning("保管するサマリーデータがありません。")
        return

    try:
        logging.info(f"💾 SQLAlchemy Engineを介してデータ保管を開始します。")
        # Pandasのto_sql機能を活用し、SQLAlchemy Engine経由で一時テーブルに書き込む
        summary_df.to_sql(
            "temp_edinet_document_summaries",
            con=Engine, 
            if_exists='replace',
            index=False
        )

        with Engine.begin() as connection:
            # INSERT OR REPLACE (Upsert) を実行
            columns = ', '.join(summary_df.columns)
            upsert_sql = text(f"""
                INSERT OR REPLACE INTO edinet_document_summaries ({columns})
                SELECT {columns} FROM temp_edinet_document_summaries
            """)
            connection.execute(upsert_sql)
            connection.execute(text("DROP TABLE temp_edinet_document_summaries"))

        logging.info(f"✅ サマリーデータ ({len(summary_df)} 件) をDBに保管しました。")

    except Exception as e:
        logging.error(f"サマリーデータのDB保管中にエラーが発生しました: {e}")
        raise # フロー制御のためにエラーを再スロー

# --- 2. CSV抽出パスのインデックス作成 (旧 step6 のDB記録ロジック) ---

def index_extracted_csv_path(doc_id: str, csv_filename: str, extracted_path: str):
    """
    抽出されたCSVファイルのパスをデータベースに記録する。
    テーブル: edinet_extracted_csv_details
    """
    # NOTE: SQLite接続を都度行うか、SessionLocalを使うか、Engineの接続を使うかは設計によるが、
    # ここでは既存のstep6のロジック [6] に倣い、生のsqlite3接続を使用する（またはEngine.connect()を使う）。
    # ここでは簡潔のため、sqlite3を直接使用するパターンを維持します。
    conn = None
    try:
        conn = sqlite3.connect(Config.DB_PATH)
        # テーブル作成ロジック（initialize_dbで既に実行済みだが、念のため）
        conn.execute("""
            CREATE TABLE IF NOT EXISTS edinet_extracted_csv_details (
                docID TEXT NOT NULL,
                csv_filename TEXT NOT NULL,
                extracted_path TEXT PRIMARY KEY,
                extraction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(docID) REFERENCES edinet_document_summaries(docID)
            )
        """)
        
        # INSERT OR REPLACE でパスを記録
        conn.execute(
            "INSERT OR REPLACE INTO edinet_extracted_csv_details (docID, csv_filename, extracted_path) VALUES (?, ?, ?)",
            (doc_id, csv_filename, extracted_path)
        )
        conn.commit()

    except sqlite3.Error as e:
        logging.error(f"CSVパスのDB記録中にSQLiteエラーが発生しました: {e}")
        raise
    finally:
        if conn:
            conn.close()

# --- 3. 財務データの保管 (旧 step7 のコアロジック) ---

def store_financial_data(financial_df: pd.DataFrame):
    """
    解析済みの財務データDataFrameをデータベースにUpsertする。
    テーブル: edinet_financial_data
    """
    if financial_df.empty:
        logging.info("保管する財務データがありません。")
        return

    # Engineではなく、直接SQLite接続を使用してUpsertを実行する (既存のstep7 [4] のロジックを移植)
    conn = None
    try:
        conn = sqlite3.connect(Config.DB_PATH)
        
        # 財務データテーブルの定義 (PKはdocID, accountName, fiscalYear, termの組み合わせ)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS edinet_financial_data (
                docID TEXT NOT NULL,
                secCode TEXT,
                fiscalYear INTEGER,
                term TEXT,
                accountName TEXT NOT NULL,
                amount REAL,
                unit TEXT,
                currency TEXT,
                PRIMARY KEY (docID, accountName, fiscalYear, term),
                FOREIGN KEY(docID) REFERENCES edinet_document_summaries(docID)
            )
        """)
        
        # 一時テーブル経由で INSERT OR REPLACE を実行
        financial_df.to_sql("temp_edinet_financial_data", conn, if_exists='replace', index=False)

        columns = ', '.join(financial_df.columns)
        conn.execute(f"""
            INSERT OR REPLACE INTO edinet_financial_data ({columns})
            SELECT {columns} FROM temp_edinet_financial_data
        """)
        conn.execute("DROP TABLE temp_edinet_financial_data")
        conn.commit()

        logging.info(f"✅ {len(financial_df)} 件の財務数値をDBに保管しました。")

    except sqlite3.Error as e:
        logging.error(f"財務データのDB保管中にSQLiteエラーが発生しました: {e}")
        raise
    finally:
        if conn:
            conn.close()