from flask import session, redirect, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
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
    print(f"入力されたユーザー名:{user_id}")
    if user_id in VALID_USERNAME_PASSWORD_PAIRS:
        user = User(user_id)
        
        # ユーザーがロードされたら、セッションを有効として更新
        # セッションが変更されたことを明示的に示し、クッキーの更新を保証
        from flask import session 
        session.modified = True 
        
        return user
    print("ユーザー名が一致しません")
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
                user = User(username)
                # 永続化
                login_user(user, remember=True)
                # セッションへの書き込みを確実にする
                from flask import session
                session.permanent = True  # セッションを永続化
                session.modified = True   # セッションの変更を明示
                from flask import url_for
                return redirect(url_for('serve_dash_app')) # serve_dash_app は '/' ルートの関数名
            else:
                error = 'Invalid credentials. Please try again.'
        
        # ログインフォームの表示 (ここでは簡易HTMLで例示)
        html = '''
            <!DOCTYPE html>
            <html>
            <head><title>Login</title></head>
            <body>
                <h1>EDINET Data Dashboard Login</h1>
                <p style="color:red;">{}</p>
                <form method="POST">
                    <input type="text" name="username" placeholder="Username" required value="user"><br>
                    <input type="password" name="password" placeholder="Password" required value="userpass"><br>
                    <input type="submit" value="Log In">
                </form>
            </body>
            </html>
        '''
        return html.format(error if 'error' in locals() else '')
    # 注: 実際のDashアプリケーションでは、この/loginページ全体をDashコンポーネント（HTML/DCC/Bootstrapなど）で構築することが一般的です。ここでは認証ロジックを示すため、Flaskの簡易HTMLで記述しています。

    # Flask-Loginを用いたログアウトルートの定義
    @app.server.route('/logout')
    def logout_route():
        print(f"ログアウトしました")
        # Flask-Loginの機能を使って現在のセッションを破棄
        logout_user()
        # ユーザーをログインページにリダイレクト
        return redirect('/login')

    # メインルートの保護
    @app.server.route('/')
    @login_required 
    def serve_dash_app():
        return app.index()