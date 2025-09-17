from edinet_steps import (
    step1_create_and_summarize,
    step2_check_download_status,
    step3_execute_download
)
import logging
import traceback
from edinet_config import Config
from pathlib import Path

# ログファイルの保存先を指定
log_path = Config.BASE_DIR / "edinet_log.txt"

# ログ設定：INFO以上を表示、ファイルとコンソール両方に出力
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def main() -> bool:
    """EDINETデータの取得とダウンロード処理"""
    try:
        logging.info("処理を開始します。")

        summary_data = step1_create_and_summarize()

        if summary_data.empty:
            logging.warning("サマリーデータが空です。ダウンロード処理はスキップされます。")
            return False

        files_to_download = step2_check_download_status(summary_data)

        if files_to_download.empty:
            logging.info("新規ダウンロード対象はありません。")
        else:
            step3_execute_download(files_to_download)

        logging.info("全ての処理が完了しました。🎉")
        return True

    except Exception as e:
        logging.error(f"エラーが発生しました: {e}")
        logging.debug(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        logging.warning("一部の処理が正常に完了しませんでした。")