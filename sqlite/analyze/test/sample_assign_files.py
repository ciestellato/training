import sqlite3
import pandas as pd
import logging
from pathlib import Path

# --- 設定とマッピング ---
# Config.DB_PATH は、データベースファイルのパスを指すものと想定 [1]
DB_PATH = "edinet_data.db" # 例として定義

# 1. 書類タイプとターゲットテーブル名のマッピングを定義
# (書類種別コード 'docTypeCode' をキーに使用)
DOC_TYPE_TABLE_MAP = {
    "120": "financial_data_YukaShokenHoukokusho", # 有価証券報告書
    "140": "financial_data_ShihankiHoukokusho",   # 四半期報告書
    "160": "financial_data_HankiHoukokusho",          # 半期報告書
    # 必要に応じて他のコードを追加
}

# 2. ターゲットテーブルのスキーマ定義
# 既存の 'edinet_financial_data' テーブルの構造を流用することを想定 [1]
FINANCIAL_TABLE_SCHEMA = """
(
    docID TEXT NOT NULL,
    accountName TEXT,
    amount REAL,
    unit TEXT,
    currency TEXT,
    PRIMARY KEY (docID, accountName)
)
"""

def get_doc_type_code_from_summary(conn: sqlite3.Connection, doc_id: str) -> str | None:
    """
    書類管理番号(docID)から書類種別コード(docTypeCode)を取得する。
    
    [1]のクエリ構造（edinet_document_summariesテーブルの利用）に基づき、この情報を取得。
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT docTypeCode FROM edinet_document_summaries WHERE docID = '?'", (doc_id,))
        result = cursor.fetchone()
        if result:
            return result
        return None
    except sqlite3.Error as e:
        logging.error(f"書類タイプ取得中にエラー: {e}")
        return None

def create_table_if_not_exists(conn: sqlite3.Connection, table_name: str):
    """
    動的に決定されたテーブル名でテーブルを作成する。
    """
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} {FINANCIAL_TABLE_SCHEMA}"
    try:
        conn.execute(sql)
        conn.commit()
        logging.debug(f"テーブル '{table_name}' が存在しないため作成しました。")
    except sqlite3.Error as e:
        logging.error(f"テーブル作成エラー ({table_name}): {e}")
        raise

def step7_parse_and_store_csv_data_to_db_by_doc_type(doc_id: str, financial_df: pd.DataFrame):
    """
    書類種別コードに基づいて財務データを適切なテーブルに格納するロジック。
    """
    logging.info(f"--- DocID: {doc_id} の財務データ格納処理を開始 ---")

    if financial_df.empty:
        logging.warning(f"DocID: {doc_id} に格納すべき財務データがありません。")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # 1. docTypeCodeを取得
        doc_type_code = get_doc_type_code_from_summary(conn, doc_id)
        
        if doc_type_code is None:
            logging.warning(f"DocID: {doc_id} の書類種別コードが見つかりませんでした。")
            return

        # 2. 格納先のテーブル名を決定
        target_table = DOC_TYPE_TABLE_MAP.get(doc_type_code)

        if target_table:
            # 3. テーブルが存在しなければ作成
            create_table_if_not_exists(conn, target_table)
            
            # 4. データをDataFrameからSQLiteに挿入
            # SQLiteへの格納では、既存のレコードを更新/置換するために 'INSERT OR REPLACE' が望ましい 
            # (Pandas to_sqlはデフォルトではそれができないため、ここでは append のみを使用) [2]
            
            # 実際の環境では、データ重複を防ぐため、一度削除してから挿入するか、
            # INSERT OR REPLACE文を構築する必要があります。
            financial_df.to_sql(target_table, conn, if_exists='append', index=False)
            logging.info(f"DocID: {doc_id} のデータをテーブル '{target_table}' (コード: {doc_type_code}) に格納しました。")
            
        else:
            logging.warning(f"DocID: {doc_id} の書類種別コード '{doc_type_code}' に対応するテーブルマッピングが定義されていません。格納をスキップします。")

    except Exception as e:
        logging.error(f"書類タイプ別格納中に予期せぬエラー: {e}")
    finally:
        if conn:
            conn.close()

# --- 使用例 (ダミーデータを利用) ---
# DocID: S1000001 が書類種別コード "120" (有価証券報告書) に紐づいていると仮定
# (実際には事前に edinet_document_summaries に格納されている必要がある)

if __name__ == '__main__':
#     # データベースにサマリー情報が存在する前提として、ここでは省略
#     
#     # ダミーの財務データを作成 (実際にはCSV解析から得られる) [2]
    dummy_df = pd.DataFrame([
        {'docID': 'S100NS9Y', 'accountName': 'NetSales', 'amount': 1000000000, 'unit': '千円', 'currency': 'JPY'},
        {'docID': 'S100NS9Y', 'accountName': 'OperatingIncome', 'amount': 50000000, 'unit': '千円', 'currency': 'JPY'}
    ])
# 
#     # このロジックを実行するためには、まず docID がサマリーテーブルに存在し、
#     # docTypeCodeが取得できる状態を確立する必要があります。
    step7_parse_and_store_csv_data_to_db_by_doc_type('S100NS9Y', dummy_df)
#     pass
