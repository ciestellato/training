# pygameモジュールをインポート
import pygame

# Pygameの初期化（内部モジュールの準備）
pygame.init()

# ウィンドウサイズを定義（幅640、高さ480）
screen_width = 640
screen_height = 480

# ウィンドウSurface（描画対象）を作成
screen = pygame.display.set_mode((screen_width, screen_height))

# ウィンドウのタイトルを設定
pygame.display.set_caption("画像を表示するサンプル")

# 画像ファイルを読み込む（Surfaceとして取得）
# ファイルパスは "images/ship.bmp"。相対パスなので、実行ファイルと同じ階層に images フォルダが必要
ship_image = pygame.image.load("images/ship.bmp")

# 画像の位置を指定するRectを作成（画面中央に配置）
ship_rect = ship_image.get_rect()
ship_rect.center = (screen_width // 2, screen_height // 2)

# メインループの制御フラグ
running = True

# 画面更新速度を制御するタイマー
clock = pygame.time.Clock()

# メインループ開始
while running:
    # イベント処理（ウィンドウを閉じる操作など）
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    ship_rect.x -= 10

    # 画面を宇宙船の画像の背景色とほぼ同じ色にする
    screen.fill((229, 229, 229))

    # 画像Surfaceを画面に描画（blit = 貼り付け）
    screen.blit(ship_image, ship_rect)

    # 描画内容を画面に反映（更新）
    pygame.display.update()

    clock.tick(30)

# Pygameの終了処理（リソース解放）
pygame.quit()