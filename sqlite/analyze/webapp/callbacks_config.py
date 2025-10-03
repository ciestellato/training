from dash import Output, Input, State, callback
from dash import html
from edinet_config import Config

def register_config_callbacks(app):
    """設定適用コールバック"""
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
