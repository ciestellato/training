import io
import pandas as pd
from pathlib import Path
import logging
import csv
import sqlite3
from sqlalchemy.orm import Session
from tqdm import tqdm
from typing import Optional

from edinet_config import Config
from .edinet_models import EdinetExtractedCsvDetails
from .database_setup import Base  # Baseは既存のファイルからインポート
from .zip_utils import extract_csv_from_zip # 既存のZIP抽出ユーティリティを利用

"""責任範囲：ローカルでのファイル操作やデータ解析。"""

# --- 1. ZIPからCSVを抽出する (旧 step6 のファイル操作ロジック) ---

def extract_and_index_all_csvs(zip_base_folder: Path, repo, db: Session):
    """
    指定されたフォルダ内の全てのZIPからCSVを抽出し、パスをリポジトリ (DB) に記録する。
    repo は storage_repo.py モジュールを指すことを想定。
    """
    logging.info("--- CSV抽出処理を開始 ---")
    
    extract_temp_folder = Config.EXTRACTED_CSV_TEMP_FOLDER
    extract_temp_folder.mkdir(parents=True, exist_ok=True)

    all_zip_files = list(zip_base_folder.rglob('*.zip'))

    if not all_zip_files:
        logging.info("処理対象のZIPファイルが見つかりません。")
        return

    inserted_path_count = 0 
    
    for zip_file_path in tqdm(all_zip_files, desc="CSV抽出とDB記録"):
        doc_id = zip_file_path.stem 
        
        try:
            # 抽出を実行 [9]
            current_extract_folder = extract_temp_folder / doc_id
            extracted_csv_paths = extract_csv_from_zip(zip_file_path, current_extract_folder)

            if extracted_csv_paths:
                for csv_path in extracted_csv_paths:
                    # DBへの記録はセッションを渡して実行
                    # repoはここではstorage_repoモジュールを指す
                    repo.index_extracted_csv_path(doc_id, csv_path.name, db) # <= db セッションを渡す
                    inserted_path_count += 1

        except Exception as e:
            logging.error(f"ZIPファイル '{zip_file_path.name}' のCSV抽出中にエラーが発生しました: {e}")
        
    logging.info(f"✅ CSV抽出とパス記録が完了しました。合計 {inserted_path_count} 件のCSVパスを記録。")


# --- 2. データベースから解析対象のCSVパスを読み込む ---

def get_csv_paths_from_repo(docID: str, db: Session) -> list[str]:
    """
    指定されたdocIDに関連するCSVパスを取得します。
    """
    results = db.query(EdinetExtractedCsvDetails.csv_path)\
                .filter(EdinetExtractedCsvDetails.docID == docID)\
                .all()
    
    # 結果がタプルのリストで返されるため、文字列のリストに変換
    return [path for path in results]

# --- 3. CSVファイルを解析し、財務データDataFrameを生成する (旧 step7 の解析ロジック) ---

def robust_read_edinet_csv(cleaned_data: str, file_path: str) -> Optional[pd.DataFrame]: 
    """
    EDINET CSV/TSVファイルを、カンマ区切り、タブ区切り、引用符緩和の順で
    堅牢に読み込む関数。
    """
    # 読み込みオプション
    base_options = {
        'engine': 'python',
        'on_bad_lines': 'warn'  # 不良行を検出した場合に警告を出す
    }
    df = []

    # 1. カンマ区切り (デフォルトのCSV) として試行
    try:
        df = pd.read_csv(io.StringIO(cleaned_data), sep=',', **base_options)
        logging.debug(f"成功: {file_path} をカンマ区切りで読み込みました。")
    except pd.errors.ParserError:
        logging.warning(f"警告: {file_path} のカンマ区切り解析に失敗しました。")
        pass # 失敗したら次に進む

    # 2. タブ区切り (TSV) として試行
    if df is None:
        try:
            df = pd.read_csv(io.StringIO(cleaned_data), sep='\t', **base_options)
            logging.debug(f"成功: {file_path} をタブ区切りで読み込みました。")
        except pd.errors.ParserError:
            logging.warning(f"警告: {file_path} のタブ区切り解析に失敗しました。")
            pass # 失敗したら次に進む

    # 3. 最終手段: タブ区切り + 引用符処理を無効化 (QUOTE_NONE) して試行
    # 注: データ内にカンマやタブが含まれていた場合、列が崩れるリスクがあります。
    if df is None:
        try:
            options_no_quote = base_options.copy()
            options_no_quote['quoting'] = csv.QUOTE_NONE
            df = pd.read_csv(io.StringIO(cleaned_data), sep='\t', **options_no_quote)
            logging.warning(f"成功: {file_path} をタブ区切り、引用符無効化で読み込みました。データ品質を確認してください。")
        except pd.errors.ParserError as e:
            logging.warning(f"警告: {file_path} のタブ区切り+QUOTE_NONE解析に失敗しました。")
            pass # 失敗したら次に進む

    # 4. カンマ区切り + 引用符処理を無効化 (QUOTE_NONE) して試行
    # カンマ区切りだが、引用符が不規則で通常解析に失敗するケースに対応
    if df is None:
        try:
            options_no_quote = base_options.copy()
            options_no_quote['quoting'] = csv.QUOTE_NONE
            df = pd.read_csv(io.StringIO(cleaned_data), sep=',', **options_no_quote)
            logging.warning(f"成功: {file_path} をカンマ区切り、引用符無効化で読み込みました。データ品質を確認してください。")
        except pd.errors.ParserError as e:
            logging.error(f"致命的エラー: {file_path} の解析がすべての試行で失敗しました: {e}")
            return None
        
    # 読み込みが一度でも成功した場合、要素IDチェックに進む
    if df is not None:
        
        # 5. カラム名（ヘッダー）の前後にある空白を削除する (前回の修正点)
        df.columns = df.columns.str.strip() 

        # 6. 「要素ID」カラムが存在するか確認し、存在しなければスキップ (ご要望の追加ロジック)
        if '要素ID' not in df.columns:
            # 要素IDがない場合、これは財務数値CSVとして処理すべきでないファイルであると判断し、Noneを返す
            logging.warning(f"CSVファイル '{file_path}' は「要素ID」を含まないため、財務データ解析をスキップします。")
            return None # Noneを返してスキップさせる

        return df

    return None # 読み込み試行全体が失敗した場合

def parse_all_financial_csvs(csv_paths_df: pd.DataFrame) -> pd.DataFrame:
    """
    CSVパスリストに基づき、各CSVを解析して統合された財務データDataFrameを返す。
    """
    logging.info("--- CSV解析処理を開始 ---")

    if csv_paths_df.empty:
        logging.info("解析対象のCSVファイルパスが見つかりません。")
        return pd.DataFrame()

    all_financial_data = []
    
    # DBからsecCodeを事前に取得するための準備 (edinet_document_summariesテーブルから)
    conn = sqlite3.connect(Config.DB_PATH)
    summary_lookup_df = pd.read_sql_query("SELECT docID, secCode FROM edinet_document_summaries", conn)
    conn.close()
    
    summary_lookup = summary_lookup_df.set_index('docID')['secCode'].to_dict()

    for _, row in tqdm(csv_paths_df.iterrows(), total=len(csv_paths_df), desc="CSVファイル解析"):
        doc_id = row['docID']
        csv_path = Path(row['extracted_path'])
        df_csv = None
        
        if not csv_path.exists():
            logging.warning(f"CSVファイルが存在しません: {csv_path}。スキップします。")
            continue

        try:
            # --- 分岐ロジック (1/2)---
            # 1. 監査報告書など、財務数値でないCSVファイルの除外 (または専用処理)
            # CSVファイル名には、XBRLタクソノミに基づき接頭辞が付与されていることが多い
            if csv_path.name.startswith("jpaud-"):
                # 監査報告書なので、財務数値抽出の対象外とする
                logging.debug(f"監査報告書ファイルを除外しました: {csv_path.name}")
                continue
                

            # 実際のEDINET CSVの構造に合わせて解析処理を実装
            
            # EDINETのCSVファイルは、XBRLから変換された形式（例: [11] のような要素IDベース）
            # または特定のレイアウトを持つもの [12] が存在します。
            
            # ここでは、外部ソースのXBRLデータ [11] の構造を参考に、
            # 必要な勘定科目（例: 売上高、資産合計）を抽出し、DataFrameを整形するロジックを実装する前提で、
            # サンプルデータの抽出処理を記述します。
            
            # まずファイルをバイナリモードで開き、UTF-16でデコード
            with open(csv_path, 'rb') as f:
                # 1. バイナリを読み込み、UTF-16 LEを試す (EDINET CSVはLE形式が多い傾向がある)
                # UTF-16 の代わりに 'utf-16-le' を明示的に指定することで、BOMがない場合の処理を安定させる
                decoded_data = f.read().decode('utf-16-le', errors='ignore') 
            
            # 2. ヌル文字（\x00）を強制的に削除する
            # UTF-16ファイルを間違ったエンコーディングで扱うと発生しやすい問題に対処
            cleaned_data = decoded_data.replace('\x00', '')
            
            # 3. 堅牢な読み込み関数を使用してDataFrameを取得
            df_csv = robust_read_edinet_csv(cleaned_data, csv_path.name)
            
            # 4. 読み込みが失敗した場合は、次のファイルに進む
            if df_csv is None:
                continue

            # --- 分岐ロジック (2/2)---
            # 2. 財務数値CSVを処理
            if '要素ID' not in df_csv.columns:
                # 財務数値CSVだが、ヘッダーが想定外
                logging.warning(f"CSVファイル '{csv_path.name}' に '要素ID' カラムが見つかりません。")
                continue

            # --- 解析ダミーロジック ---
            # 実際のXBRL_TO_CSVは複雑なため、ここでは概念的なフィルタリングを示す
            # 外部ソースのデータ例 [11, 13] に基づき、勘定科目名と値、単位を抽出する
            
            # 抽出対象の要素IDのリスト (例: jppfs_cor:NetSales, jppfs_cor:Assets)
            target_element_ids = ['jpcrp_cor:NetSalesSummaryOfBusinessResults', 'jppfs_cor:Assets']
            
            extracted_records = df_csv[df_csv['要素ID'].isin(target_element_ids)].copy()
            
            if not extracted_records.empty:
                temp_data = extracted_records.rename(columns={
                    '項目名': 'accountName',
                    '値': 'amount',
                    '単位': 'unit'
                })
                # その他のメタ情報を付与
                temp_data['docID'] = doc_id
                temp_data['secCode'] = summary_lookup.get(doc_id)
                # 注: 期間の特定 (fiscalYear, term) は 'コンテキストID' や '期間・時点' 列から複雑なロジックで導出する必要があります。
                temp_data['fiscalYear'] = 9999 # 仮
                temp_data['term'] = 'Annual' # 仮
                temp_data['currency'] = temp_data['ユニットID'].apply(lambda x: 'JPY' if x == 'JPY' else None)
                
                # 必要なカラムのみに絞り込み
                final_cols = ['docID', 'secCode', 'fiscalYear', 'term', 'accountName', 'amount', 'unit', 'currency']
                all_financial_data.append(temp_data[final_cols])
            
            # --- 解析ダミーロジック 終了 ---

        except Exception as e:
            logging.error(f"CSVファイル '{csv_path.name}' の解析中にエラーが発生しました: {e}")
            logging.debug(e)
            continue
            
    if all_financial_data:
        return pd.concat(all_financial_data, ignore_index=True)
    else:
        return pd.DataFrame()