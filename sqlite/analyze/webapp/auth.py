from flask import session, redirect, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from edinet_config import Config

# 認証情報
VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'adminpass',
    'user': 'userpass'
}

# 1. ユーザーモデルの定義
class User(UserMixin):
    def __init__(self, username):
        self.id = username

# 2. LoginManagerの初期化と設定
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    """ユーザーIDからUserオブジェクトをロードする関数"""
    if user_id in VALID_USERNAME_PASSWORD_PAIRS:
        return User(user_id)
    return None

def configure_auth(app):
    """DashアプリのサーバーにFlask-Loginを設定する"""
    login_manager.init_app(app.server)
    login_manager.login_view = '/login'
    
    # Flask-Loginを用いたログインルートの定義
    @app.server.route('/login', methods=['GET', 'POST'])
    def login_route():
        # ... ログイン認証ロジック ...
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            # 認証チェック
            if username in VALID_USERNAME_PASSWORD_PAIRS and VALID_USERNAME_PASSWORD_PAIRS[username] == password:
                user = load_user(username)
                login_user(user)
                return redirect('/')
            else:
                error = 'Invalid credentials. Please try again.'
        
        # ログインフォームの表示 (ここでは簡易HTMLで例示)
        return '''
            <!DOCTYPE html>
            <html>
            <head><title>Login</title></head>
            <body>
                <h1>EDINET Data Dashboard Login</h1>
                <p style="color:red;">{}</p>
                <form method="POST">
                    <input type="text" name="username" placeholder="Username" required><br>
                    <input type="password" name="password" placeholder="Password" required><br>
                    <input type="submit" value="Log In">
                </form>
            </body>
            </html>
        '''.format(error if 'error' in locals() else '')
    # 注: 実際のDashアプリケーションでは、この/loginページ全体をDashコンポーネント（HTML/DCC/Bootstrapなど）で構築することが一般的です。ここでは認証ロジックを示すため、Flaskの簡易HTMLで記述しています。

    # Flask-Loginを用いたログアウトルートの定義
    @app.server.route('/logout')
    def logout_route():
        # Flask-Loginの機能を使って現在のセッションを破棄
        logout_user()
        if 'username' in session: # 念のためのセッションクリア
            del session['username']
        # ユーザーをログインページにリダイレクト
        return redirect('/login')

    # メインルートの保護
    @app.server.route('/')
    @login_required 
    def serve_dash_app():
        return app.index()