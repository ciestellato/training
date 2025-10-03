import dash
from dash import Output, Input, callback, no_update
from flask_login import current_user
from webapp.layout import get_main_layout, get_login_required_layout

def register_auth_callbacks(app):
    """ユーザー認証に関するコールバックを登録する関数"""

    # 未ログインの場合ログイン画面にリダイレクト
    @callback(
        # 出力は URL コンポーネントの pathname
        Output('url', 'pathname', allow_duplicate=True), 
        Input('login-status-store', 'data'),
        prevent_initial_call='initial_duplicate'
    )
    def enforce_login_redirect(login_data):
        # login_dataが None または username が設定されていない場合
        if login_data is None or login_data.get('username') is None:
            # ユーザーがすでにログインページにいる場合は何もしない（無限ループ防止）
            # このチェックには dcc.Location の pathname State が必要になる
            # 簡単な方法として、常に /login にリダイレクトさせ、Flask-Login側で既に /login にいた場合は何もしないという挙動に頼る
            
            # ログアウト状態の場合、/login にリダイレクトを指示
            return '/login' 
            
        return dash.no_update # ログイン中の場合は何もしない

    # --- ログイン状態の設定 ---
    # @callback(
    #     Output('login-status-store', 'data'),
    #     Input('interval-component', 'n_intervals'),
    #     prevent_initial_call=True
    # )
    # def update_login_status(_):
    #     # Flask-Loginのcurrent_userの状態に基づいてログイン状態を更新する
    #     if current_user.is_authenticated:
    #         # 認証が通っている場合、セッションの 'username' を更新（古い Basic Auth の名残だが、Dash側に状態を渡す）
    #         session['username'] = current_user.id 
    #         role = 'admin' if current_user.id == 'admin' else 'user'
    #         return {'username': current_user.id, 'role': role}
    #     else:
    #         if 'username' in session: # ログアウト処理が行われた場合
    #             del session['username']
    #         return {'username': None, 'role': None}

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
    
    # --- ログイン状態によって page-content を切り替えるコールバック ---
    @callback(
        Output('page-content', 'children'),
        Input('login-status-store', 'data')
    )
    def display_page(login_data):
        if login_data and login_data.get('username'):
            return get_main_layout()
        else:
            return get_login_required_layout()
