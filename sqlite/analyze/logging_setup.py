import logging
import io
from dash import dcc, html # Dashコンポーネントが不要なら除外可能

# ロギング出力をキャプチャするためのカスタムハンドラ
class DashLogHandler(logging.Handler):
    def __init__(self, output_buffer):
        super().__init__()
        self.output_buffer = output_buffer
        self.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    def emit(self, record):
        msg = self.format(record)
        self.output_buffer.write(msg + '\n')

# ロギングバッファとハンドラの初期化
log_buffer = io.StringIO()
dash_handler = DashLogHandler(log_buffer)

# ロギング設定の適用（app.pyから移動）
logging.getLogger().addHandler(dash_handler)

def get_log_buffer():
    return log_buffer

def get_dash_log_handler():
    return dash_handler
