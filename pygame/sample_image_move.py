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

# ●宇宙船の移動速度（ピクセル単位）
move_speed = 5

# ★クロックオブジェクトを作成（FPS制御用）------------------------
clock = pygame.time.Clock()

# メインループの制御フラグ
running = True

# メインループ開始
while running:
    # イベント処理（ウィンドウを閉じる操作など）
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # 矢印キーに応じてRectの位置を変更（境界制限なし）
    if keys[pygame.K_LEFT]:
        ship_rect.x -= move_speed  # 左へ移動
    if keys[pygame.K_RIGHT]:
        ship_rect.x += move_speed  # 右へ移動
    if keys[pygame.K_UP]:
        ship_rect.y -= move_speed  # 上へ移動
    if keys[pygame.K_DOWN]:
        ship_rect.y += move_speed  # 下へ移動

    # 画面を宇宙船の画像の背景色とほぼ同じ色にする
    screen.fill((229, 229, 229))

    # 画像Surfaceを画面に描画（blit = 貼り付け）
    screen.blit(ship_image, ship_rect)

    # 描画内容を画面に反映（更新）
    pygame.display.update()

    # ★FPSを制限（1秒間に30フレームに設定）---------------------
    clock.tick(30)  # 数値を小さくすると動きがゆっくりに見える

# Pygameの終了処理（リソース解放）
pygame.quit()
