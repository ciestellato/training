import dash
from dash import Output, Input, callback
import logging
import pandas as pd
import sqlite3
from dash import html
from edinet_config import Config
from edinet_pipeline.edinet_steps import (
    step1_create_and_summarize, step2_check_download_status, step3_execute_download,
    step5_store_summary_to_db, step6_extract_and_index_csv, step7_parse_and_store_csv_data_to_db,
    retry_failed_downloads
)

def register_processing_callbacks(app, log_buffer):
    """処理実行コールバック（各ボタンに対応）"""
    @callback(
        Output('processing-status', 'children'),
        Output('log-output', 'children'),
        Input('run-all-button', 'n_clicks'),
        Input('update-summary-button', 'n_clicks'),
        Input('download-parse-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def run_processing_steps(run_all_clicks, update_summary_clicks, download_parse_clicks):
        # n_clicks を確認してどのボタンが押されたかを判定
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        log_buffer.seek(0)
        log_buffer.truncate(0) # ログバッファをクリア

        status_message = ""
        try:
            if button_id == 'run-all-button':
                logging.info("--- 全処理実行を開始します ---")
                # main() 関数を呼び出す代わりに、各ステップを順番に呼び出す
                # または edinet_main.py の main 関数を呼び出すことも可能
                retry_failed_downloads()
                summary_df = step1_create_and_summarize()
                if not summary_df.empty:
                    files_to_download = step2_check_download_status(summary_df)
                    if not files_to_download.empty:
                        step3_execute_download(files_to_download)
                    retry_failed_downloads()
                    step5_store_summary_to_db(summary_df)
                    step6_extract_and_index_csv(Config.SAVE_FOLDER)
                    step7_parse_and_store_csv_data_to_db() # 財務データ解析ステップ
                status_message = "✅ 全処理が完了しました。"

            elif button_id == 'update-summary-button':
                logging.info("--- サマリー更新処理を開始します ---")
                summary_df = step1_create_and_summarize()
                if not summary_df.empty:
                    step5_store_summary_to_db(summary_df)
                status_message = "✅ サマリー更新が完了しました。"

            elif button_id == 'download-parse-button':
                logging.info("--- ダウンロード・CSV解析処理を開始します ---")
                # サマリーデータはDBから取得するか、Config.BASE_DIR / "EDINET_Summary_v3.csv"から読み込む
                # ここでは簡単のため、現在のConfigに基づいたsummary_dfを想定
                # 実際には、最新のsummary_dfをDBから読み込むか、再度step1を呼び出す方が確実
                
                # データベースから最新のサマリーデータを取得してダウンロード対象をチェック
                conn = sqlite3.connect(Config.DB_PATH)
                summary_df_from_db = pd.read_sql_query("SELECT * FROM edinet_document_summaries", conn)
                conn.close()

                files_to_download = step2_check_download_status(summary_df_from_db)
                if not files_to_download.empty:
                    step3_execute_download(files_to_download)
                retry_failed_downloads()
                step6_extract_and_index_csv(Config.SAVE_FOLDER)
                step7_parse_and_store_csv_data_to_db() # 財務データ解析ステップ
                status_message = "✅ ダウンロード・CSV解析が完了しました。"

        except Exception as e:
            logging.error(f"処理中にエラーが発生しました: {e}", exc_info=True)
            status_message = f"❌ 処理中にエラーが発生しました: {e}"
        
        return status_message, html.Pre(log_buffer.getvalue())
