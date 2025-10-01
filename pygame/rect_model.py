import pygame

# --- クラス定義 ---
# 「動く四角形」という概念を表現するクラスを定義します。
class MovableRectangle:
    """
    自身で移動アニメーションを行う四角形を表現するクラス。
    """
    # このメソッドは、クラスの新しいインスタンス（実体）が作られるときに自動で呼び出されます。
    def __init__(self, screen, x, y, width, height, color, speed_x, speed_y):
        # 属性の初期化
        # 描画先のscreenオブジェクトを、このクラスのインスタンス変数に格納します。
        self.screen = screen
        # 四角形の位置とサイズを管理するRectオブジェクトを初期化します。
        self.rect = pygame.Rect(x, y, width, height)
        # 四角形の色をインスタンス変数に格納します。
        self.color = color
        # X方向の移動速度をインスタンス変数に格納します。
        self.speed_x = speed_x
        # Y方向の移動速度をインスタンス変数に格納します。
        self.speed_y = speed_y

    # このメソッドは、オブジェクトの状態（位置）を更新する役割を持ちます。
    def update(self):
        """
        四角形の位置を更新し、壁にぶつかったら跳ね返る処理。
        """
        # x座標とy座標にそれぞれの速度を足して、四角形を移動させます。
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # 左右の壁に衝突したかを判定します。
        # rectの左端が画面の左端(0)より小さいか、または右端が画面の幅より大きい場合、
        if self.rect.left < 0 or self.rect.right > self.screen.get_width():
            # X方向の速度を反転させ、逆方向に移動するようにします。
            self.speed_x = -self.speed_x

        # 上下の壁に衝突したかを判定します。
        # rectの上端が画面の上端(0)より小さいか、または底辺が画面の高さより大きい場合、
        if self.rect.top < 0 or self.rect.bottom > self.screen.get_height():
            # Y方向の速度を反転させ、逆方向に移動するようにします。
            self.speed_y = -self.speed_y

    # このメソッドは、オブジェクトを画面に描画する役割を持ちます。
    def draw(self):
        """
        四角形を画面に描画する処理。
        """
        # pygame.draw.rect()を使って、指定された画面に、指定された色とrect情報で四角形を描画します。
        pygame.draw.rect(self.screen, self.color, self.rect)
