import os
import dash
import logging
import io
import logging_setup 

# Dashアプリのインスタンス化
app = dash.Dash(__name__)

# 外部モジュールのインポート
from webapp.auth import configure_auth
from webapp.layout import get_main_layout
from webapp.callbacks import register_callbacks

# ログバッファの定義
log_buffer = io.StringIO()
# app.pyでDashLogHandlerとlog_bufferを定義していた既存のコードを削除し、
# logging_setup を実行することで初期化されるようにします。

# ✅ Flask-Login認証の設定
configure_auth(app)

# ✅ Flaskセッションのための secret_key を設定
app.server.secret_key = os.urandom(24)  # 任意の安全な文字列

# ✅ レイアウトの設定
app.layout = get_main_layout()

# ✅ コールバックの登録
register_callbacks(app, log_buffer)

if __name__ == '__main__':
    # 依存関係は app.py 自体には残るが、メインロジックからは分離された
    from edinet_config import Config 
    from edinet_pipeline.database_setup import initialize_database
    
    # データベース初期化 (メイン処理の前に一度だけ実行するのが安全)
    initialize_database() 
    
    app.run(debug=True, port=8050)