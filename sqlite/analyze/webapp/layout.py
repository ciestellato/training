from dash import dcc, html
from edinet_config import Config # 設定値の参照用
from logging_setup import DashLogHandler, log_buffer # ロギングバッファを参照するため、log_bufferをインポート（または config に移動）
# ロギング設定をインポート
import logging_setup

# DashLogHandlerとlog_bufferの定義/設定も、可能であれば別のロギング設定ファイルに分離することを検討すべきです。
# ただし、現状のapp.py [6, 7] の定義に依存するため、ここでは簡略化のため、app.pyに一時的に残します。
# ログ出力エリア（html.Pre(id='log-output')）が layout に含まれるためです。

def get_main_layout():
    """アプリケーションの全体レイアウトを返す"""
    return html.Div([
        # ユーザーのログイン状態とロールを保持するためのStore
        dcc.Store(id='login-status-store', storage_type='session'),
        
        # ページ遷移をトリガーするためのLocationコンポーネント
        dcc.Location(id='url', refresh=True), 
        
        # ユーザー情報とログアウトボタンを表示するエリア
        html.Div(id='auth-header', style={'textAlign': 'right', 'padding': '10px'}, children=[
            html.Span(id='current-username', style={'marginRight': '10px', 'fontWeight': 'bold'}),
            html.Button("ログアウト", id='logout-button', n_clicks=0, 
                        style={'backgroundColor': '#DC3545', 'color': 'white', 'padding': '5px 10px', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'marginLeft': '10px'})
        ]),

        html.H1("EDINET Data Dashboard", style={'textAlign': 'center', 'color': '#2C3E50', 'padding': '20px 0'}),
        html.Hr(style={'borderColor': '#EAECEE'}),

        # 管理者用パネル (初期は非表示)
        html.Div(id='admin-sections', style={'display': 'none'}, children=[
            # --- 設定パネル ---
            html.Div([
                html.H2("設定", style={'borderBottom': '1px solid #ccc', 'paddingBottom': '10px', 'color': '#34495E'}),
                html.Div([
                    html.Label("APIキー:", style={'fontWeight': 'bold'}),
                    dcc.Input(id='api-key-input', type='password', placeholder='EDINET APIキーを入力',
                            value=Config.API_KEY, style={'width': '100%', 'padding': '8px', 'borderRadius': '4px', 'border': '1px solid #ddd'}),
                    html.Small("APIキーは .env ファイルから読み込まれていますが、一時的に変更できます。", style={'color': '#888'}),
                ], style={'marginBottom': '15px'}),
                html.Div([
                    html.Label("初回取得年数:", style={'fontWeight': 'bold'}),
                    dcc.Input(id='initial-fetch-years-input', type='number', value=Config.INITIAL_FETCH_YEARS,
                            style={'width': 'calc(100% - 10px)', 'padding': '8px', 'borderRadius': '4px', 'border': '1px solid #ddd'}),
                ], style={'marginBottom': '15px'}),
                html.Div([
                    html.Label("信頼性確保日数:", style={'fontWeight': 'bold'}),
                    dcc.Input(id='reliability-days-input', type='number', value=Config.RELIABILITY_DAYS,
                            style={'width': 'calc(100% - 10px)', 'padding': '8px', 'borderRadius': '4px', 'border': '1px solid #ddd'}),
                ], style={'marginBottom': '15px'}),
                html.Div([
                    html.Label("対象書類タイプコード (カンマ区切り):", style={'fontWeight': 'bold'}),
                    dcc.Input(id='target-doc-types-input', type='text',
                            value=','.join(Config.TARGET_DOC_TYPE_CODES), style={'width': '100%', 'padding': '8px', 'borderRadius': '4px', 'border': '1px solid #ddd'}),
                    html.Small("例: 120, 140, 160 （有価証券報告書、四半期報告書、半期報告書）", style={'color': '#888'}),
                ], style={'marginBottom': '20px'}),
                html.Button("設定を適用", id='apply-config-button', n_clicks=0,
                            style={'backgroundColor': '#28A745', 'color': 'white', 'padding': '10px 15px', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}),
                html.Div(id='config-status', style={'marginTop': '10px', 'color': 'green', 'fontWeight': 'bold'})
            ], style={'padding': '20px', 'border': '1px solid #eee', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '30px', 'backgroundColor': '#FFFFFF'}),

            # --- データ取得・更新パネル ---
            html.Div([
                html.H2("データ取得・更新", style={'borderBottom': '1px solid #ccc', 'paddingBottom': '10px', 'color': '#34495E'}),
                html.Div([
                    html.Button("全処理を実行 (main)", id='run-all-button', n_clicks=0,
                                style={'marginRight': '10px', 'backgroundColor': '#007BFF', 'color': 'white', 'padding': '10px 15px', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}),
                    html.Button("サマリー更新とDB保管のみ", id='update-summary-button', n_clicks=0,
                                style={'marginRight': '10px', 'backgroundColor': '#FFC107', 'color': 'black', 'padding': '10px 15px', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}),
                    html.Button("CSVダウンロード・解析のみ", id='download-parse-button', n_clicks=0,
                                style={'backgroundColor': '#17A2B8', 'color': 'white', 'padding': '10px 15px', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}),
                ], style={'marginBottom': '20px'}),
                html.Div(id='processing-status', style={'marginTop': '10px', 'color': 'blue', 'fontWeight': 'bold'}),
                html.H3("処理ログ", style={'marginTop': '20px', 'color': '#34495E'}),
                dcc.Loading(
                    id="loading-log", type="circle",
                    children=html.Pre(id='log-output', style={'backgroundColor': '#f9f9f9', 'padding': '10px', 'height': '300px', 'overflowY': 'scroll', 'border': '1px solid #ddd', 'borderRadius': '4px', 'fontFamily': 'monospace', 'whiteSpace': 'pre-wrap'})
                )
            ], style={'padding': '20px', 'border': '1px solid #eee', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '30px', 'backgroundColor': '#FFFFFF'}),
        ]),

        # ユーザー用パネル (初期は非表示)
        html.Div(id='user-sections', style={'display': 'none'}, children=[
            # --- データベース閲覧・可視化パネル ---
            html.Div([
                html.H2("財務データ可視化", style={'borderBottom': '1px solid #ccc', 'paddingBottom': '10px', 'color': '#34495E'}),
                # 会社名入力
                html.Div([
                    html.Label("会社名または証券コード:", style={'fontWeight': 'bold'}),
                    dcc.Input(id='company-search-input', type='text', placeholder='例: 株式会社○○ または 1234',
                            style={'width': '100%', 'padding': '8px', 'borderRadius': '4px', 'border': '1px solid #ddd'}),
                ], style={'marginBottom': '15px'}),
                # 🔽 会社名候補表示用のドロップダウン
                dcc.Dropdown(id='company-dropdown', placeholder='会社を選択', style={'marginBottom': '20px'}),
                # 会計期間入力
                html.Div([
                    html.Label("会計期間終了日 (YYYY-MM-DD):", style={'fontWeight': 'bold'}),
                    dcc.Input(id='period-end-input', type='text', placeholder='例: 2024-03-31',
                            style={'width': '100%', 'padding': '8px', 'borderRadius': '4px', 'border': '1px solid #ddd'}),
                    html.Small("未入力の場合、指定会社/コードで最新の期を取得します。", style={'color': '#888'}),
                ], style={'marginBottom': '20px'}),
                html.Button("BS/PL概要を表示", id='fetch-financial-data-button', n_clicks=0,
                            style={'backgroundColor': '#6C757D', 'color': 'white', 'padding': '10px 15px', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}),
                # 📊 財務データのタブ表示領域
                html.Div(id='financial-tabs-container', style={'marginTop': '20px'}),
                dcc.Loading(
                    id="loading-financial-data", type="circle",
                    children=[
                        html.Div(id='financial-data-output', style={'marginTop': '20px'}),
                        dcc.Graph(id='financial-data-graph', style={'marginTop': '20px'})
                    ]
                )
            ], style={'padding': '20px', 'border': '1px solid #eee', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '30px', 'backgroundColor': '#FFFFFF'}),
        ]),

            # ログ出力更新用のインターバルコンポーネント (これは管理者/ユーザー関係なく機能させるため、メインレイアウト直下)
            dcc.Interval(
                id='interval-component',
                interval=1*1000, # 1秒ごとに更新
                n_intervals=0
            )
        ], style={'fontFamily': 'Arial, sans-serif', 'maxWidth': '1000px', 'margin': 'auto', 'padding': '20px', 'backgroundColor': '#F8F9FA'})
