import pandas as pd
import logging
import sqlite3
from sqlalchemy import text, Float
from sqlalchemy.orm import Session
from datetime import date

from .database_setup import Engine # 初期化されたEngineをインポート
from edinet_config import Config # ConfigはDB_PATHなどに必要
from .edinet_models import EdinetExtractedCsvDetails, EdinetFinancialData

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

def index_extracted_csv_path(docID: str, csv_path: str, db: Session):
    """
    抽出されたCSVパスをデータベースに記録します。
    :param docID: EDINET書類ID
    :param csv_path: 抽出されたCSVファイルのパス
    :param db: SQLAlchemy Sessionオブジェクト (依存性注入されることを想定)
    """
    # 最後にリフレッシュするオブジェクトを保持する変数
    entry_to_refresh = None

    # 既存のレコードがあるか確認（更新が必要な場合）
    existing_entry = db.query(EdinetExtractedCsvDetails).filter_by(docID=docID).first()

    if existing_entry:
        # 更新
        existing_entry.csv_path = csv_path
        existing_entry.extracted_at = date.today()
        entry_to_refresh = existing_entry
        
    else:
        # 新規挿入
        new_entry = EdinetExtractedCsvDetails(
            docID=docID,
            csv_path=csv_path,
            extracted_at=date.today()
        )
        db.add(new_entry)
        entry_to_refresh = new_entry
    
    # 変更を確定
    db.commit()
    
    if entry_to_refresh:
        # 最後にオブジェクトをリフレッシュ
        db.refresh(entry_to_refresh)
        
    return True

# --- 3. 財務データの保管 (旧 step7 のコアロジック) ---

def store_financial_data(df_financial_data: pd.DataFrame, engine=Engine):
    """
    Pandas DataFrameの財務データをSQLAlchemy Engineを介して格納します。
    （元の実装のように、一時テーブルを使ってUpsertを行う想定）
    """
    temp_table_name = 'edinet_financial_data_temp'
    target_table_name = EdinetFinancialData.__tablename__ # 'edinet_financial_data'

    # 1. SQLAlchemy Engineを使ってトランザクションを開始
    with engine.begin() as connection:
        
        # 2. データのロード (Pandas to_sqlにSQLAlchemyのConnectionを使用)
        # to_sqlはデフォルトで生のコネクションではなくSQLAlchemyのコネクションを使用可能
        df_financial_data.to_sql(
            temp_table_name,
            con=connection, # SQLAlchemyの接続オブジェクトを使用
            if_exists='replace',
            index=False,
            dtype={
                'value': Float  # データ型を明示的に指定可能
            }
        )

        # 3. UPSERT/MERGE操作 (生のSQLをSQLAlchemy Coreのtext()でラップ)
        # SQLiteでは標準のUPSERT(ON CONFLICT)を使用するか、またはMERGEの代わりとなるINSERT OR REPLACEを使用
        
        # 簡易的なMERGE/UPSERT操作 (SQLiteのINSERT OR IGNOREやREPLACEを使用する)
        # ここでは、データ量が多いため、既存データが衝突しない前提で速度優先でINSERTを行うか、
        # または、複雑なWHERE句を伴うMERGE操作が必要であれば、SQLAlchemy CoreのDELETE+INSERTを使用します。
        
        # 例: 既存データとの衝突を考慮した挿入（ここではシンプルに一時テーブルから移動）
        # ※実際のUpsertロジックは元の実装に合わせて記述してください。

        connection.execute(text(f"""
            INSERT OR REPLACE INTO {target_table_name} 
            (docID, element_id, context_ref, unit_ref, value)
            SELECT docID, element_id, context_ref, unit_ref, value
            FROM {temp_table_name};
        """))

        # 4. 一時テーブルの削除
        connection.execute(text(f"DROP TABLE IF EXISTS {temp_table_name};"))

    # トランザクションが成功すれば自動でコミットされます。
    return True
