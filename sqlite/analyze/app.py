import os
import dash
from dash import html
import logging
import io
import logging_setup 
from datetime import timedelta
from flask_login import LoginManager,current_user

# Dashアプリのインスタンス化
app = dash.Dash(__name__)

# 未ログイン時に /login へリダイレクト
login_manager = LoginManager()
login_manager.init_app(app.server)  # app.server は Flask インスタンス
login_manager.login_view = '/login'

# 外部モジュールのインポート
from webapp.auth import configure_auth
from webapp.layout import get_main_layout
from webapp.callbacks_auth import register_auth_callbacks
from webapp.callbacks_config import register_config_callbacks
from webapp.callbacks_financial import register_financial_callbacks
from webapp.callbacks_processing import register_processing_callbacks
from edinet_config import Config

# ログバッファの定義
log_buffer = io.StringIO()
# app.pyでDashLogHandlerとlog_bufferを定義していた既存のコードを削除し、
# logging_setup を実行することで初期化されるようにします。

# ✅ Flask-Login認証の設定
configure_auth(app)

# セッションの恒久化
app.server.config['SESSION_PERMANENT'] = True
# セッションの有効期間（例: 7日）
app.server.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# ✅ Flaskセッションのための secret_key を設定
app.server.secret_key = Config.FLASK_SECRET_KEY

# Dashにレイアウトを渡す
from dash import dcc
app.layout = html.Div([
    dcc.Location(id='url'),
    dcc.Store(id='login-status-store', storage_type='session'),
    html.Div(id='page-content')
])

# ✅ コールバックの登録
register_auth_callbacks(app)
register_config_callbacks(app)
register_financial_callbacks(app)
register_processing_callbacks(app, log_buffer)

if __name__ == '__main__':
    # 依存関係は app.py 自体には残るが、メインロジックからは分離された
    from edinet_config import Config 
    from edinet_pipeline.database_setup import initialize_database
    
    # データベース初期化 (メイン処理の前に一度だけ実行するのが安全)
    initialize_database() 
    
    app.run(debug=True, port=8050)