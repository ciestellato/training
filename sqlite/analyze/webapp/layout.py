from dash import dcc, html
from edinet_config import Config # 設定値の参照用
# ロギングバッファを参照するため、log_bufferをインポート（または config に移動）
from logging_setup import DashLogHandler, log_buffer 
# ロギング設定をインポート
import logging_setup

def get_main_layout():
    """アプリケーションの全体レイアウトを返す"""
    return html.Div([
        # ユーザーのログイン状態とロールを保持するためのStore
        dcc.Store(id='login-status-store', storage_type='session'),
        
        # ページ遷移をトリガーするためのLocationコンポーネント
        dcc.Location(id='url', refresh=True), 
        
        # ユーザー情報とログアウトボタンを表示するエリア
        html.Div(id='auth-header', className='auth-header', children=[
            html.Span(id='current-username'),
            html.Button("ログアウト", id='logout-button', n_clicks=0, className='logout-button')
        ]),

        html.H1("EDINET Data Dashboard"),
        html.Hr(),

        # 管理者用パネル (初期は非表示)
        html.Div(id='admin-sections', style={'display': 'none'}, children=[
            # --- 設定パネル ---
            html.Div([
                html.H2("設定"),
                html.Div([
                    html.Label("APIキー:"),
                    dcc.Input(id='api-key-input', type='password', placeholder='EDINET APIキーを入力',
                            value=Config.API_KEY),
                    html.Small("APIキーは .env ファイルから読み込まれていますが、一時的に変更できます。"),
                ]),
                html.Div([
                    html.Label("初回取得年数:"),
                    dcc.Input(id='initial-fetch-years-input', type='number', value=Config.INITIAL_FETCH_YEARS),
                ]),
                html.Div([
                    html.Label("信頼性確保日数:"),
                    dcc.Input(id='reliability-days-input', type='number', value=Config.RELIABILITY_DAYS),
                ]),
                html.Div([
                    html.Label("対象書類タイプコード (カンマ区切り):"),
                    dcc.Input(id='target-doc-types-input', type='text',
                            value=','.join(Config.TARGET_DOC_TYPE_CODES)),
                    html.Small("例: 120, 140, 160 （有価証券報告書、四半期報告書、半期報告書）"),
                ]),
                html.Button("設定を適用", id='apply-config-button', n_clicks=0),
                html.Div(id='config-status')
            ], className='panel'),

            # --- データ取得・更新パネル ---
            html.Div([
                html.H2("データ取得・更新"),
                html.Div([
                    html.Button("全処理を実行 (main)", id='run-all-button', n_clicks=0),
                    html.Button("サマリー更新とDB保管のみ", id='update-summary-button', n_clicks=0),
                    html.Button("CSVダウンロード・解析のみ", id='download-parse-button', n_clicks=0),
                ]),
                html.Div(id='processing-status'),
                html.H3("処理ログ"),
                dcc.Loading(
                    id="loading-log", type="circle",
                    children=html.Pre(id='log-output')
                )
            ], className='panel'),
        ]),

        # ユーザー用パネル (初期は非表示)
        html.Div(id='user-sections', style={'display': 'none'}, children=[
            # --- データベース閲覧・可視化パネル ---
            html.Div([
                html.H2("財務データ可視化"),
                # 会社名入力
                html.Div([
                    html.Label("会社名または証券コード:"),
                    dcc.Input(id='company-search-input', type='text', placeholder='例: 株式会社○○ または 1234'),
                ]),
                # 🔽 会社名候補表示用のドロップダウン
                dcc.Dropdown(id='company-dropdown', placeholder='会社を選択'),
                # 会計期間入力
                html.Div([
                    html.Label("会計期間終了日 (YYYY-MM-DD):"),
                    dcc.Input(id='period-end-input', type='text', placeholder='例: 2024-03-31'),
                    html.Small("未入力の場合、指定会社/コードで最新の期を取得します。"),
                ]),
                html.Button("BS/PL概要を表示", id='fetch-financial-data-button', n_clicks=0),
                # 📊 財務データのタブ表示領域
                html.Div(id='financial-tabs-container'),
                dcc.Loading(
                    id="loading-financial-data", type="circle",
                    children=[
                        html.Div(id='financial-data-output'),
                        dcc.Graph(id='financial-data-graph')
                    ]
                )
            ], className='panel'),
        ]),

            # ログ出力更新用のインターバルコンポーネント (これは管理者/ユーザー関係なく機能させるため、メインレイアウト直下)
            dcc.Interval(
                id='interval-component',
                # interval=1*1000, # 1秒ごとに更新
                n_intervals=0
            )
        ])

def get_login_required_layout():
    """未ログイン時に表示する簡易レイアウト"""
    return html.Div([
        html.H2("ログインが必要です"),
        html.A("ログインページへ", href="/login")
    ])