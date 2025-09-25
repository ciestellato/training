import pandas as pd
from pathlib import Path
import logging
import io
import csv
from typing import Optional

# --- 既存のプロジェクト構成から必要な要素を定義 (Config, robust_read_edinet_csvのモック) ---

# ConfigオブジェクトのBASE_DIRとEXTRACTED_CSV_TEMP_FOLDERは実際のパスに合わせてください
class Config:
    # 実際の環境パスに合わせて修正してください
    BASE_DIR = Path("C:/Users/0602JP/Documents/EDINET_DB/")
    EXTRACTED_CSV_TEMP_FOLDER = BASE_DIR / "02_extracted_csv_temp"
    pass

# file_processor.py に存在する堅牢な読み込み関数を再現 (簡略版)
# 既存の robust_read_edinet_csv [5, 6] のロジックを使用します
def robust_read_edinet_csv_sample(cleaned_data: str, file_path: str) -> Optional[pd.DataFrame]:
    """
    EDINET CSVファイルを堅牢に読み込むロジックをシミュレート
    """

    # 読み込みオプション
    common_options = {
        'engine': 'python',      # Pythonエンジンを使用することで、より柔軟な解析を可能にする
        'on_bad_lines': 'warn'   # 不良行を検出した場合に処理を続行しつつ警告を出す [1]
    }
    
    # 試行パターンを定義
    # 1. タブ区切り + 引用符処理あり
    trials = [
        {'sep': '\t', 'quoting': csv.QUOTE_ALL, 'comment': 'タブ区切り + 引用符あり'},
        {'sep': '\t', 'quoting': csv.QUOTE_NONE, 'comment': 'タブ区切り + 引用符無視'},
        # 以前警告が出ていたカンマ区切りは後に回す
        {'sep': ',', 'quoting': csv.QUOTE_ALL, 'comment': 'カンマ区切り + 引用符あり'},
        {'sep': ',', 'quoting': csv.QUOTE_NONE, 'comment': 'カンマ区切り + 引用符無視'},
    ]

    df = None
    
    for trial in trials:
        try:
            options = {**common_options, **trial}
            
            # quoting オプションを個別に取得・削除
            quoting = options.pop('quoting')
            comment = options.pop('comment')

            df = pd.read_csv(io.StringIO(cleaned_data), quoting=quoting, **options)

            # カラム名の空白除去（EDINETデータではよく発生する）
            df.columns = df.columns.str.strip()
            
            logging.debug(f"成功: {file_path} を {comment} で読み込みました。")
            break # 成功したらループを抜ける
            
        except pd.errors.ParserError as e:
            logging.debug(f"失敗: {file_path} ({comment}) - ParserError: {e}")
            df = None
        except Exception:
            # その他のエラー処理
            df = None
    
    # 最終チェック
    if df is not None and '要素ID' in df.columns:
        return df
    
    # 要素IDがない場合、または全ての試行が失敗した場合
    logging.warning(f"CSVファイル '{file_path}' は「要素ID」を含まないか、読み込みに失敗したため、解析をスキップします。")
    return None


# --- 実際の確認コード ---

def confirm_csv_content(doc_id: str, file_name: str):
    """
    指定された書類IDとファイル名のCSVを読み込み、内容を表示する。
    """
    # ログに表示されていたパス構造を再構築 [8]
    # 例: C:\Users\0602JP\Documents\EDINET_DB\02_extracted_csv_temp\S100WR05\XBRL_TO_CSV\file_name
    csv_path = Config.EXTRACTED_CSV_TEMP_FOLDER / doc_id / "XBRL_TO_CSV" / file_name

    if not csv_path.exists():
        print(f"エラー: 指定されたパスにファイルが存在しません: {csv_path}")
        return

    print(f"\n--- CSVファイル内容確認: {csv_path.name} ---")

    try:
        # EDINET CSVの読み込み処理 [4]
        with open(csv_path, 'rb') as f:
            # UTF-16 LEでデコード
            decoded_data = f.read().decode('utf-16-le', errors='ignore')
            # ヌル文字（\x00）を強制的に削除 [4]
            cleaned_data = decoded_data.replace('\x00', '')

        # 堅牢な読み込み関数を使用
        df_csv = robust_read_edinet_csv_sample(cleaned_data, csv_path.name)

        if df_csv is not None:
            print(f"✅ ファイル読み込み成功。要素数: {len(df_csv)} 行, {len(df_csv.columns)} 列")
            
            # --- 主な内容の表示 ---
            
            # 1. ヘッダー（カラム名）を確認
            print("\n[ヘッダー情報 (要素IDの有無が重要)]")
            print(df_csv.columns.tolist())

            # 2. 最初の数行のデータを確認
            print("\n[データサンプル (先頭 5行)]")
            # 財務データCSVの場合、要素IDや値、単位がある [3, 9]
            print(df_csv[['要素ID', '項目名', '値', '単位']].head())
            
        else:
            print("❌ 堅牢な読み込みロジックで読み込みに失敗するか、財務データとしてスキップされました。")

    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        
# --- 実行例 ---

# 1. あなたのログに表示されていた具体的なファイルパスから情報を抽出
# 例: C:\Users\0602JP\Documents\EDINET_DB\02_extracted_csv_temp\S100WR05\XBRL_TO_CSV\jpcrp030000-asr-001_E03280-000_2025-06-30_01_2025-09-25.csv
ZIP_DOC_ID = 'S100WR05' # 親フォルダ名（書類ID）を想定
TARGET_CSV_NAME = 'jpcrp030000-asr-001_E03280-000_2025-06-30_01_2025-09-25.csv'

# 2. 確認実行
# ※実行前に、Config.BASE_DIRが正しいパスを指しており、対象ファイルがそのパスに存在することを確認してください。
confirm_csv_content(ZIP_DOC_ID, TARGET_CSV_NAME) 

# --- 提供ソースに含まれるサンプルデータの内容を確認するための実行例 ---

# 提供ソース [3] に含まれる実際の財務数値データ（経営指標等のサマリー）の構造確認
# doc_id は含まれていないが、データ構造は要素ID、項目名、値、単位を持つ
SAMPLE_DATA_DOC_ID = 'S9999999' # 仮の書類ID
SAMPLE_DATA_CSV_NAME = 'jpcrp030000-asr-001_E31573-000_2024-06-30_01_2024-09-27.csv'
# このサンプルコードを実行するには、上記のCSVファイルが指定されたパスに存在している必要があります。

# confirm_csv_content(SAMPLE_DATA_DOC_ID, SAMPLE_DATA_CSV_NAME)