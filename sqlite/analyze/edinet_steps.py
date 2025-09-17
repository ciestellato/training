import os
import time
import requests
import pandas as pd
from datetime import date, timedelta
from pathlib import Path
from tqdm import tqdm
import warnings
from dotenv import load_dotenv

# urllib3のInsecureRequestWarningを非表示にする
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# .envファイルの読み込み（親の親フォルダにある場合）
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# --- 設定項目 ---
class Config:
    """設定を管理するクラス"""
    # ローカル環境の保存先（任意のパスに変更可能）
    BASE_DIR = Path("C:/Users/0602JP/Documents/EDINET_DB/")
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    # サマリーファイル保存先
    SAVE_FOLDER = BASE_DIR / "01_zip_files/"
    SAVE_FOLDER.mkdir(parents=True, exist_ok=True)

    # APIキーの取得
    API_KEY = os.getenv("EDINET_API_KEY")

    # データの信頼性を担保するため、何日分遡ってデータを再取得するか
    RELIABILITY_DAYS = 7
    # 初回実行時に何年分のデータを取得するか
    INITIAL_FETCH_YEARS = 5

    # ダウンロード対象の書類タイプコード
    TARGET_DOC_TYPE_CODES = ['120', '140', '160']



def update_summary_file(base_dir: Path, api_key: str) -> pd.DataFrame:
    """EDINETから日次の書類一覧を取得し、サマリーファイルを更新する。"""
    summary_path = base_dir / "EDINET_Summary_v3.csv"
    print(f"サマリーファイル '{summary_path.name}' の状態を確認・更新します...")

    today = date.today()
    summary = pd.DataFrame()
    start_day = today - timedelta(days=365 * Config.INITIAL_FETCH_YEARS)

    if summary_path.exists():
        try:
            dtype_map = {'secCode': str, 'docTypeCode': str, 'xbrlFlag': str, 'csvFlag': str}
            summary = pd.read_csv(summary_path, encoding='utf_8_sig', dtype=dtype_map)
            summary['submitDateTime'] = pd.to_datetime(summary['submitDateTime'], errors='coerce')

            if not summary.empty and 'submitDateTime' in summary.columns and not summary['submitDateTime'].isnull().all():
                latest_date_in_file = summary['submitDateTime'].max().date()
                start_day = latest_date_in_file - timedelta(days=Config.RELIABILITY_DAYS)
        except Exception as e:
            print(f"サマリーファイルの読み込み中にエラーが発生しました: {e}")

    end_day = today
    day_term = [start_day + timedelta(days=i) for i in range((end_day - start_day).days + 1)]

    new_docs = []
    for day in tqdm(day_term, desc="APIからメタデータ取得"):
        params = {'date': day.strftime('%Y-%m-%d'), 'type': 2, 'Subscription-Key': api_key}
        try:
            response = requests.get(
                "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json",
                params=params,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            res_json = response.json()
            if res_json.get('results'):
                new_docs.extend(res_json['results'])
        except requests.exceptions.RequestException as e:
            tqdm.write(f"エラー: {day} のデータ取得に失敗 - {e}")
        time.sleep(0.1)

    if new_docs:
        temp_df = pd.DataFrame(new_docs)
        summary = pd.concat([summary, temp_df], ignore_index=True)

    summary['submitDateTime'] = pd.to_datetime(summary['submitDateTime'], errors='coerce')
    summary.dropna(subset=['docID'], inplace=True)
    summary = summary.drop_duplicates(subset='docID', keep='last')
    summary = summary.sort_values(by='submitDateTime', ascending=True).reset_index(drop=True)

    summary.to_csv(summary_path, index=False, encoding='utf_8_sig')
    print("\n✅ サマリーファイルの更新が完了しました！")
    return summary

def step1_create_and_summarize():
    """ステップ①: サマリーを作成し、その概要を出力する。"""
    print("--- ステップ① サマリー作成と概要の表示 ---")
    summary_df = update_summary_file(Config.BASE_DIR, Config.API_KEY)

    if summary_df.empty:
        print("⚠️ サマリーデータの作成に失敗したか、データがありませんでした。")
        return pd.DataFrame()

    print(f"  - データ期間: {summary_df['submitDateTime'].min():%Y-%m-%d} ～ {summary_df['submitDateTime'].max():%Y-%m-%d}")
    print(f"  - 総データ数: {len(summary_df)} 件")
    print(f"  - 銘柄数（ユニーク）: {summary_df['secCode'].nunique()} 社")
    print("-" * 40 + "\n")
    return summary_df

def step2_check_download_status(summary_df: pd.DataFrame):
    """
    ステップ②: ダウンロードフォルダの状況を確認し、未ダウンロードの件数などを出力する。
    """
    print("--- ステップ② ダウンロード状況の確認 ---")
    save_folder = Config.SAVE_FOLDER
    save_folder.mkdir(parents=True, exist_ok=True)

    # サブフォルダ内も含めて、既存の全zipファイルを再帰的に検索
    existing_files_path = list(save_folder.rglob('*.zip'))

    print(f"📁 指定フォルダ: {save_folder}")
    if not existing_files_path:
        print("  - 既存のダウンロード済みファイルはありません。")
    else:
        print(f"  - 既存ファイル数: {len(existing_files_path)} 件")

    # --- ▼▼▼ ダウンロード対象の条件を定義 ▼▼▼ ---
    query_str = (
        "csvFlag == '1' and "
        "secCode.notna() and secCode != 'None' and "
        f"docTypeCode in {Config.TARGET_DOC_TYPE_CODES}"
    )
    target_docs = summary_df.query(query_str)
    # --- ▲▲▲ ダウンロード対象の条件を定義 ▲▲▲ ---

    # 既存ファイル名（docID）のセットを作成
    existing_file_stems = {f.stem for f in existing_files_path}

    # ダウンロード対象のうち、まだダウンロードされていないものを抽出
    docs_to_download = target_docs[~target_docs['docID'].isin(existing_file_stems)]

    print("\n📊 サマリーと照合した結果:")
    print(f"  - ダウンロード対象の総書類数（CSV提供あり）: {len(target_docs)} 件")
    print(f"  - ダウンロードが必要な（未取得の）書類数: {len(docs_to_download)} 件")
    print("-" * 40 + "\n")

    return docs_to_download

def step3_execute_download(docs_to_download: pd.DataFrame):
    """
    ステップ③: 実際にファイルのダウンロードを実行し、年/四半期フォルダに保存する。
    """
    print("--- ステップ③ ダウンロードの実行 ---")
    if docs_to_download.empty:
        print("✅ ダウンロード対象の新しいファイルはありません。処理を完了します。")
        print("-" * 40 + "\n")
        return

    print(f"{len(docs_to_download)}件のファイルのダウンロードを開始します。")

    for _, row in tqdm(docs_to_download.iterrows(), total=len(docs_to_download), desc="ZIPダウンロード進捗"):
        doc_id = row['docID']
        submit_date = row['submitDateTime']

        # --- ファイル整理のロジック ---
        if pd.isna(submit_date):
            target_folder = Config.SAVE_FOLDER / "unknown_date"
        else:
            year = submit_date.year
            quarter = (submit_date.month - 1) // 3 + 1
            target_folder = Config.SAVE_FOLDER / str(year) / f"Q{quarter}"

        target_folder.mkdir(parents=True, exist_ok=True)
        zip_path = target_folder / f"{doc_id}.zip"

        # EDINET API v2 のファイル取得エンドポイント
        url_zip = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{doc_id}"
        params_zip = {"type": 5, 'Subscription-Key': Config.API_KEY}

        try:
            r = requests.get(url_zip, params=params_zip, stream=True, verify=False, timeout=60)
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.exceptions.RequestException as e:
            tqdm.write(f"ダウンロード失敗: {doc_id}, エラー: {e}")
            if zip_path.exists():
                zip_path.unlink()
        time.sleep(0.1)

    print("\n✅ ダウンロード処理が完了しました。")
    print("-" * 40 + "\n")