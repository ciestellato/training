from edinet_config import Config
from edinet_steps import (
    step1_create_and_summarize,
    step2_check_download_status,
    step3_execute_download
)

def main():
    """メイン処理を実行する関数"""
    summary_data = step1_create_and_summarize()

    if not summary_data.empty:
        files_to_download = step2_check_download_status(summary_data)
        step3_execute_download(files_to_download)

    print("全ての処理が完了しました。🎉")

if __name__ == '__main__':
    main()