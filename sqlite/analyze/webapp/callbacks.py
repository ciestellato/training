from dash import dcc, html, Input, Output, State, callback, no_update
import dash
from flask_login import current_user
import sqlite3
import pandas as pd
import logging
import plotly.express as px
from flask import session, redirect, url_for
import io

# 内部モジュールのインポート
from edinet_config import Config
from edinet_pipeline.edinet_steps import (
    step1_create_and_summarize, step2_check_download_status, step3_execute_download, 
    step5_store_summary_to_db, step6_extract_and_index_csv, 
    step7_parse_and_store_csv_data_to_db, retry_failed_downloads
)

def register_callbacks(app, log_buffer):
    """全てのDashコールバックを登録する関数"""

    # --- ログイン状態の設定 ---
    @callback(
        Output('login-status-store', 'data'),
        Input('interval-component', 'n_intervals'),
        prevent_initial_call=True
    )
    def update_login_status(_):
        # Flask-Loginのcurrent_userの状態に基づいてログイン状態を更新する
        if current_user.is_authenticated:
            # 認証が通っている場合、セッションの 'username' を更新（古い Basic Auth の名残だが、Dash側に状態を渡す）
            session['username'] = current_user.id 
            role = 'admin' if current_user.id == 'admin' else 'user'
            return {'username': current_user.id, 'role': role}
        else:
            if 'username' in session: # ログアウト処理が行われた場合
                del session['username']
            return {'username': None, 'role': None}

    # --- ユーザー状態表示コールバック (ログイン中のみユーザー名とボタンを表示) --- [19]
    @callback(
        Output('auth-header', 'style'),
        Output('current-username', 'children'),
        [Input('login-status-store', 'data')]
    )
    def update_user_status_display(login_data):
        # login_dataがNoneでないことを確認する
        if login_data is None:
            login_data = {} # Noneの場合は空の辞書として扱うことで .get() の呼び出しを安全にする
        
        username = login_data.get('username')
        if username:
            # ログイン中の場合: ユーザー名を表示し、ヘッダーを表示状態にする
            return {'textAlign': 'right', 'padding': '10px', 'display': 'block'}, f"ログイン中: {username}"
        # ログアウト状態の場合、ヘッダーを非表示にする
        return {'display': 'none'}, ""

    # --- ログアウト処理コールバック ---
    @callback(
        Output('url', 'pathname'),
        Input('logout-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def perform_logout_and_redirect(n_clicks):
        if n_clicks and n_clicks > 0:
            # Flask-Loginを使用したクリーンなログアウトルートにリダイレクトさせる
            return '/logout'
        return dash.no_update

    # --- ロールに応じた表示切り替えコールバック ---
    @callback(
        Output('admin-sections', 'style'),
        Output('user-sections', 'style'),
        Input('login-status-store', 'data'),
        prevent_initial_call=True
    )
    def toggle_sections(login_data):
        # login_data が None の場合、空の辞書として扱う
        if login_data is None:
            login_data = {}

        role = login_data.get('role')
        if role == 'admin':
            return {'display': 'block'}, {'display': 'none'}
        elif role == 'user':
            return {'display': 'none'}, {'display': 'block'}
        # ログイン状態が確立していない、または無効なロールの場合は両方非表示
        return {'display': 'none'}, {'display': 'none'}

    # 会社名のあいまい検索と候補表示
    @callback(
        Output('company-dropdown', 'options'),
        Input('company-search-input', 'value'),
        prevent_initial_call=True
    )
    def search_company_candidates(search_text):
        if not search_text:
            raise dash.exceptions.PreventUpdate

        conn = sqlite3.connect(Config.DB_PATH)

        if search_text.isdigit() and len(search_text) == 4:
            # 証券コードによる検索
            query = """
                SELECT DISTINCT filerName, secCode
                FROM edinet_document_summaries
                WHERE secCode = ?
            """
            df = pd.read_sql_query(query, conn, params=[search_text])
        else:
            # 会社名によるあいまい検索
            query = """
                SELECT DISTINCT filerName, secCode
                FROM edinet_document_summaries
                WHERE filerName LIKE ?
                ORDER BY filerName
            """
            df = pd.read_sql_query(query, conn, params=[f"%{search_text}%"])

        conn.close()

        return [
        {'label': f"{row['filerName']} ({row['secCode']})", 'value': row['secCode']}
        for _, row in df.iterrows()
        if pd.notnull(row['secCode'])
        ]

    # 選択された会社の財務データ取得
    @callback(
        Output('financial-tabs-container', 'children'),
        Input('company-dropdown', 'value'),
        prevent_initial_call=True
    )
    def display_financial_tabs(sec_code):
        if not sec_code:
            raise dash.exceptions.PreventUpdate

        conn = sqlite3.connect(Config.DB_PATH)
        query = """
            SELECT fd.*, s.periodEnd
            FROM edinet_financial_data fd
            JOIN edinet_document_summaries s ON fd.docID = s.docID
            WHERE s.secCode = ?
            ORDER BY s.periodEnd DESC
        """
        df = pd.read_sql_query(query, conn, params=[sec_code])
        conn.close()

        if df.empty:
            return html.Div("財務データが見つかりませんでした。")

        tabs = []
        for period_end, group in df.groupby('periodEnd'):
            tab_label = f"{pd.to_datetime(period_end).year}年{pd.to_datetime(period_end).month}月期"
            table = dash.dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in group.columns],
                data=group.to_dict('records'),
                page_size=15
            )
            tabs.append(dcc.Tab(label=tab_label, children=[table]))

        return dcc.Tabs(children=tabs)

    # 設定適用コールバック
    @callback(
        Output('config-status', 'children'),
        Input('apply-config-button', 'n_clicks'),
        State('api-key-input', 'value'),
        State('initial-fetch-years-input', 'value'),
        State('reliability-days-input', 'value'),
        State('target-doc-types-input', 'value'),
        prevent_initial_call=True
    )
    def apply_config(n_clicks, api_key, initial_fetch_years, reliability_days, target_doc_types_str):
        if n_clicks > 0:
            try:
                Config.API_KEY = api_key
                Config.INITIAL_FETCH_YEARS = int(initial_fetch_years)
                Config.RELIABILITY_DAYS = int(reliability_days)
                Config.TARGET_DOC_TYPE_CODES = [code.strip() for code in target_doc_types_str.split(',') if code.strip()]
                return html.Span(f"設定が適用されました。APIキー: {'*' * (len(api_key) - 4) + api_key[-4:] if api_key else '未設定'}, 初期取得年数: {Config.INITIAL_FETCH_YEARS}, 信頼性日数: {Config.RELIABILITY_DAYS}, 対象書類タイプ: {Config.TARGET_DOC_TYPE_CODES}", style={'color': 'green'})
            except Exception as e:
                return html.Span(f"設定の適用中にエラーが発生しました: {e}", style={'color': 'red'})
        return ""

    # 処理実行コールバック (各ボタンに対応)
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


    # 財務データ表示コールバック
    @callback(
        Output('financial-data-output', 'children'),
        Output('financial-data-graph', 'figure'),
        Input('fetch-financial-data-button', 'n_clicks'),
        State('company-search-input', 'value'),
        State('period-end-input', 'value'),
        prevent_initial_call=True
    )
    def fetch_and_display_financial_data(n_clicks, company_search, period_end):
        if n_clicks > 0:
            if not company_search and not period_end:
                return html.Div("会社名または証券コード、会計期間終了日のいずれかを入力してください。", style={'color': 'red'}), {}

            conn = None
            try:
                conn = sqlite3.connect(Config.DB_PATH)
                # 検索条件に基づいてSQLクエリを構築
                sql_query = """
                    SELECT
                        s.filerName AS 会社名,
                        s.secCode AS 証券コード,
                        s.docDescription AS 書類概要,
                        s.periodStart AS 会計期間_開始日,
                        s.periodEnd AS 会計期間_終了日,
                        fd.accountName AS 勘定科目名,
                        fd.amount AS 金額,
                        fd.unit AS 単位,
                        fd.currency AS 通貨
                    FROM
                        edinet_financial_data AS fd
                    JOIN
                        edinet_document_summaries AS s
                    ON
                        fd.docID = s.docID
                    WHERE 1=1
                """
                params = []

                if company_search:
                    if company_search.isdigit() and len(company_search) == 4: # 証券コードを想定
                        sql_query += " AND s.secCode = ?"
                        params.append(company_search)
                    else: # 会社名を想定
                        sql_query += " AND s.filerName LIKE ?"
                        params.append(f"%{company_search}%")
                
                if period_end:
                    sql_query += " AND s.periodEnd = ?"
                    params.append(period_end)
                
                sql_query += """
                    AND fd.accountName IN (
                        '売上高', '営業利益', '経常利益', '当期純利益',
                        '流動資産合計', '固定資産合計', '資産合計',
                        '流動負債合計', '固定負債合計', '負債合計',
                        '純資産合計', '負債純資産合計'
                    )
                    ORDER BY s.periodEnd DESC, fd.accountName
                """
                
                df = pd.read_sql_query(sql_query, conn, params=params)

                if df.empty:
                    return html.Div("指定された条件の財務データは見つかりませんでした。", style={'color': 'orange'}), {}

                # データフレーム表示
                table = dash.dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict('records'),
                    page_size=15,
                    style_table={'overflowX': 'auto'}
                )

                # グラフ表示（例: 棒グラフ）
                # 複数行のデータがある場合を考慮
                fig = px.bar(
                    df,
                    x="勘定科目名",
                    y="金額",
                    color="会社名",
                    barmode="group",
                    title=f"{df['会社名'].iloc[0]} のBS/PL概要 ({df['会計期間_終了日'].iloc[0]})",
                    text="金額" # 金額を棒グラフの上に表示
                )
                # 金額が大きい場合に単位を調整するなどの整形は別途必要
                fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

                return html.Div([
                    html.H3("取得結果"),
                    table
                ]), fig

            except sqlite3.Error as e:
                return html.Div(f"データベースエラー: {e}", style={'color': 'red'}), {}
            except Exception as e:
                return html.Div(f"データの取得・表示中にエラーが発生しました: {e}", style={'color': 'red'}), {}
            finally:
                if conn:
                    conn.close()
        return "", {}

    if __name__ == '__main__':
        app.run(debug=True, port=8050)
