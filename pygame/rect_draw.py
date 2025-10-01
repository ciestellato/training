import pygame
from rect_model import MovableRectangle

# 1. Pygameの初期化
pygame.init()

# 2. 画面とオブジェクトの設定
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("クラス化した四角形（screenを引数で渡す）")

# 画面更新速度を制御するタイマー
clock = pygame.time.Clock()

# --- オブジェクトの作成 ---
# MovableRectangleクラスのインスタンス（実体）を作成
# screenオブジェクトを引数として渡す
my_rectangle = MovableRectangle(
    screen=screen,
    x=screen_width // 2 - 50,
    y=screen_height // 2 - 50,
    width=100,
    height=100,
    color=(255, 100, 0),
    speed_x=3,
    speed_y=2
)
my_rectangle2 = MovableRectangle(
    screen=screen,
    x=screen_width // 2 - 50,
    y=screen_height // 2 - 50,
    width=30,
    height=30,
    color=(55, 100, 40),
    speed_x=3,
    speed_y=2
)
# --- メインループ ---
running = True
while running:
    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 描画のクリア
    screen.fill((0, 0, 0))

    # オブジェクトの振る舞いを実行
    my_rectangle.update()
    my_rectangle.draw()
    my_rectangle2.update()
    my_rectangle2.draw()

    # 画面の更新
    pygame.display.update()

    # FPSの制御
    clock.tick(60)

# Pygameの終了処理
pygame.quit()