import time
import pandas as pd
import logging
import traceback
import requests
from tqdm import tqdm
from pathlib import Path
from datetime import date, timedelta, datetime

from edinet_config import Config

"""責任範囲：EDINET APIとの直接的な通信処理。"""

def update_summary_file(base_dir: Path, api_key: str) -> pd.DataFrame:
    """EDINETから日次の書類一覧を取得し、サマリーファイルを更新する。"""
    summary_path = base_dir / "EDINET_Summary_v3.csv"
    logging.info(f"サマリーファイル '{summary_path.name}' の状態を確認・更新します...")

    today = date.today()
    summary = pd.DataFrame()

    # Config.INITIAL_FETCH_YEARS から Config.RELIABILITY_DAYS を考慮して start_day を設定
    # 既存のサマリーファイルが存在しない場合は INITIAL_FETCH_YEARS 分遡る
    start_day = today - timedelta(days=365 * Config.INITIAL_FETCH_YEARS)

    if summary_path.exists():
        try:
            dtype_map = {'secCode': str, 'docTypeCode': str, 'xbrlFlag': str, 'csvFlag': str}
            summary = pd.read_csv(summary_path, encoding='utf_8_sig', dtype=dtype_map)
            summary['submitDateTime'] = pd.to_datetime(summary['submitDateTime'], errors='coerce')

            if not summary.empty and 'submitDateTime' in summary.columns and not summary['submitDateTime'].isnull().all():
                latest_date_in_file = summary['submitDateTime'].max().date()
                # 信頼性確保のため、最新日付からRELIABILITY_DAYS分遡って再取得開始
                start_day = latest_date_in_file - timedelta(days=Config.RELIABILITY_DAYS)
        except Exception as e:
            logging.warning(f"サマリーファイルの読み込み中にエラーが発生しました: {e}")
            logging.debug(traceback.format_exc())

    end_day = today
    day_term = [start_day + timedelta(days=i) for i in range((end_day - start_day).days + 1)]

    new_docs = []
    for day in tqdm(day_term, desc="APIからメタデータ取得"):
        # EDINET API仕様書 [32, 34] に基づくリクエストパラメータ
        params = {'date': day.strftime('%Y-%m-%d'), 'type': 2, 'Subscription-Key': api_key}
        try:
            response = requests.get(
                Config.API_BASE_URL + "/documents.json",
                params=params,
                verify=False, # 本番環境ではTrueを検討
                timeout=Config.REQUEST_TIMEOUT
            )
            # HTTPステータスコードが4xx/5xxの場合はここでRequestExceptionを発生させる
            # ただし、EDINET APIはエラー時もHTTP 200を返す場合があるため、JSONレスポンスの解析も必要 [1]
            response.raise_for_status()
            res_json = response.json()
            logging.debug(f"APIレスポンス (日: {day.strftime('%Y-%m-%d')}): {res_json}") # デバッグ用にレスポンス全体を出力

            status = None
            message = None

            # EDINET APIのエラーレスポンス構造を考慮してstatusとmessageを取得 [2, 3]
            if isinstance(res_json, dict):
                if 'metadata' in res_json and isinstance(res_json['metadata'], dict):
                    metadata = res_json['metadata']
                    status = metadata.get('status')
                    message = metadata.get('message')
                elif 'StatusCode' in res_json: # 401 Access denied の場合など [3]
                    status = res_json.get('StatusCode')
                    message = res_json.get('message')
            
            # ステータスコードに応じた処理 [1]
            if status == '404' or status == 404: 
                logging.info(f"情報なし: {day.strftime('%Y-%m-%d')} の書類一覧は見つかりませんでした。")
            elif status and (str(status) != '200'): # ステータスが200以外の場合
                log_msg = f"APIエラー: {day.strftime('%Y-%m-%d')} - Status: {status}, Message: {message if message else '詳細不明'}"
                logging.warning(log_msg)
            elif res_json.get('results'): # 正常レスポンスで'results'がある場合 [6]
                new_docs.extend(res_json['results'])
            elif status == '200' and not res_json.get('results'): # **👈 ここに新しい elif ブロックを追加します**
                # APIは正常応答 (status: 200, message: OK) だが、resultsが空の場合
                logging.info(f"情報なし: {day.strftime('%Y-%m-%d')} の提出書類はありませんでした。")
                logging.debug(f"APIレスポンス (日: {day.strftime('%Y-%m-%d')}): {res_json}") # デバッグ用にレスポンス全体を出力
            else: # その他の予期せぬレスポンスの場合 (これに入ることは稀になるはず)
                logging.warning(f"予期せぬAPIレスポンス形式またはデータなし: {day.strftime('%Y-%m-%d')}. レスポンス: {res_json}")

        except requests.exceptions.RequestException as e:
            # ネットワークエラーやHTTPステータスコードが4xx/5xxだった場合
            logging.warning(f"エラー: {day.strftime('%Y-%m-%d')} のデータ取得に失敗 (ネットワークまたはHTTPステータスエラー) - {e}")
            logging.debug(traceback.format_exc())
        except ValueError as e: # response.json()がJSONとしてパースできない場合
            logging.error(f"エラー: {day.strftime('%Y-%m-%d')} のAPIレスポンスがJSONとして解析できませんでした。エラー: {e}, レスポンス内容: {response.text[:500]}...")
            logging.debug(traceback.format_exc())
        except Exception as e: # その他の予期せぬエラー
            logging.error(f"エラー: {day.strftime('%Y-%m-%d')} のデータ取得中に予期せぬエラーが発生しました: {e}")
            logging.debug(traceback.format_exc())
        time.sleep(0.1) # APIへの負荷軽減のため
        
    if new_docs:
        temp_df = pd.DataFrame(new_docs)
        # 既存のサマリーデータと新しいデータを結合し、重複を排除
        # docIDは提出書類ごとに付与される一意の番号 [40, 102]
        summary = pd.concat([summary, temp_df], ignore_index=True) 
        summary['submitDateTime'] = pd.to_datetime(summary['submitDateTime'], errors='coerce')
        summary.dropna(subset=['docID'], inplace=True)
        summary = summary.drop_duplicates(subset='docID', keep='last')
        summary = summary.sort_values(by='submitDateTime', ascending=True).reset_index(drop=True)

        try:
            summary.to_csv(summary_path, index=False, encoding='utf_8_sig')
            logging.info("✅ サマリーファイルの更新が完了しました！")
        except Exception as e:
            logging.error(f"サマリーファイルの保存に失敗しました: {e}")
            logging.debug(traceback.format_exc())
    else:
        logging.info("新規に取得されたサマリーデータはありません。")

    return summary

def download_single_file(doc_id: str, submit_date, save_folder: Path) -> bool:
    """1件のEDINETファイルをダウンロードし、保存。成功ならTrue、失敗ならFalse"""
    if pd.isna(submit_date):
        target_folder = save_folder / "unknown_date"
    else:
        year = submit_date.year
        quarter = (submit_date.month - 1) // 3 + 1
        target_folder = save_folder / str(year) / f"Q{quarter}"

    target_folder.mkdir(parents=True, exist_ok=True)
    zip_path = target_folder / f"{doc_id}.zip"

    # EDINET API のファイル取得エンドポイント [89]
    url_zip = f"{Config.API_BASE_URL}/documents/{doc_id}"
    # 必要書類タイプ '5' はCSV形式のZIPファイル [90, 93]
    params_zip = {"type": 5, 'Subscription-Key': Config.API_KEY}

    try:
        r = requests.get(url_zip, params=params_zip, stream=True, verify=False, timeout=Config.DOWNLOAD_TIMEOUT)
        r.raise_for_status()

        # Content-Typeをチェックして、ZIPファイルであることを確認 [92, 99]
        content_type = r.headers.get('Content-Type', '')
        if 'application/octet-stream' not in content_type: # ZIP形式の場合
            # エラーレスポンスがJSON形式で返ってくる可能性も考慮 [92]
            if 'application/json' in content_type:
                error_json = r.json()
                status = error_json.get('metadata', {}).get('status', 'N/A')
                message = error_json.get('metadata', {}).get('message', 'N/A')
                logging.warning(f"ダウンロード失敗: {doc_id}. APIがエラーJSONを返却。Status: {status}, Message: {message}")
            else:
                logging.warning(f"ダウンロード失敗: {doc_id}. 予期せぬContent-Type: {content_type}")
            if zip_path.exists():
                zip_path.unlink() # 不完全なファイルを削除
            return False

        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True

    except requests.exceptions.RequestException as e:
        logging.warning(f"ダウンロード失敗: {doc_id}, エラー: {e}")
        logging.debug(traceback.format_exc())
        if zip_path.exists():
            zip_path.unlink() # 失敗した場合はファイルを削除
        return False
    except Exception as e:
        logging.error(f"ファイル {doc_id} ダウンロード中に予期せぬエラー: {e}")
        logging.debug(traceback.format_exc())
        if zip_path.exists():
            zip_path.unlink()
        return False
