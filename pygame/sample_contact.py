# pygameモジュールをインポート
import pygame

# Pygameの初期化
pygame.init()

# ウィンドウサイズを定義
screen_width = 640
screen_height = 480

# ウィンドウSurfaceを作成
screen = pygame.display.set_mode((screen_width, screen_height))

# ウィンドウのタイトルを設定
pygame.display.set_caption("四角形と円の接触検知")

# 色を定義
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# --- 四角形（Sprite）クラスの定義 ---


class Square(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # 描画するSurfaceを作成（四角形のサイズ）
        self.image = pygame.Surface([50, 50])
        # Surfaceを赤色で塗りつぶす
        self.image.fill(RED)

        # Rectを取得
        self.rect = self.image.get_rect()

        # 初期位置を画面下部の中央に設定
        self.rect.midbottom = (screen_width // 2, screen_height)

    def update(self):
        # キー入力の取得
        keys = pygame.key.get_pressed()

        # 速度を設定
        speed = 5

        # キー入力に応じて位置を更新
        if keys[pygame.K_LEFT]:
            self.rect.x -= speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += speed
        if keys[pygame.K_UP]:
            self.rect.y -= speed
        if keys[pygame.K_DOWN]:
            self.rect.y += speed

        # 画面外に出ないように制限
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, screen_width)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, screen_height)

# --- 円を描画するクラス（Spriteではない） ---


# 円を表現するクラスを定義
class Circle:
    def __init__(self, color, radius, center_pos):
        # 円の色（RGBタプル）を保持
        self.color = color

        # 円の半径（ピクセル単位）を保持
        self.radius = radius

        # 円の中心座標（x, y）を保持
        self.center_pos = center_pos

        # 円の当たり判定用のRectを作成
        # Rectは左上座標と幅・高さで定義されるため、中心から半径分ずらして設定
        self.rect = pygame.Rect(
            center_pos[0] - radius,  # 左上x座標
            center_pos[1] - radius,  # 左上y座標
            radius * 2,              # 幅（直径）
            radius * 2               # 高さ（直径）
        )

    # 円を描画するメソッド
    def draw(self, surface):
        # 指定されたSurface（画面など）に円を描画
        # 引数：描画先Surface, 色, 中心座標, 半径
        pygame.draw.circle(surface, self.color, self.center_pos, self.radius)


# --- オブジェクトのインスタンスを作成 ---
square_sprite = Square()
circle = Circle(BLUE, 50, (screen_width // 2, screen_height // 2))

# --- Spriteを描画・管理するためのGroupを作成 ---
all_sprites = pygame.sprite.Group()
all_sprites.add(square_sprite)


# タイマー
clock = pygame.time.Clock()

# メインループの制御フラグ
running = True

# メインループ開始
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Spriteグループを更新
    all_sprites.update()

    # --- ★ 接触判定 ---
    # PygameのRect.colliderect()メソッドで2つのRectが重なっているか判定
    if square_sprite.rect.colliderect(circle.rect):
        print("四角形と円が接触")

    # 背景色を淡い灰色に設定
    screen.fill((229, 229, 229))

    # 円を描画
    circle.draw(screen)

    # Spriteグループを描画
    all_sprites.draw(screen)

    # 描画内容を画面に反映
    pygame.display.update()

    clock.tick(60)

# Pygameの終了処理
pygame.quit()