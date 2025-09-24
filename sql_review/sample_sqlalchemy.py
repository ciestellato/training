# SQLAlchemyの基本機能をインポート（DB接続、カラム定義など）
from sqlalchemy import create_engine, Column, Integer, String

# ORM機能を使うためのベースクラスとセッション管理をインポート
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite用のエンジンを作成（alchemydbというファイルに接続）
# echo=True にすると、実行されるSQL文がコンソールに表示される（学習者向けに有効）
engine = create_engine("sqlite:///alchemydb", echo=True)

# ORMのベースクラスを定義（すべてのテーブルクラスはこれを継承する）
Base = declarative_base()

# productsテーブルのモデルクラスを定義（Pythonクラス ⇔ SQLテーブルの対応）
class Product(Base):
    # テーブル名を指定（SQL上のテーブル名）
    __tablename__ = "products"

    # 商品ID（主キー、自動採番）
    product_id = Column(Integer, primary_key=True, autoincrement=True)

    # 商品名（NULL不可）
    name = Column(String, nullable=False)

    # 税抜価格（整数、NULL不可）
    price_excl_tax = Column(Integer, nullable=False)

# モデル定義に基づいて、テーブルをデータベースに作成（CREATE TABLEと同等）
Base.metadata.create_all(engine)

# セッション管理クラスを作成（エンジンに接続）
Session = sessionmaker(bind=engine)

# セッションインスタンスを生成（トランザクション開始）
session = Session()

# 登録する商品インスタンスを作成（INSERT対象のデータ）
# new_product = Product(name="ベジタブルピザ(M)", price_excl_tax=1200)

my_product = Product(name="BBQピザ(XL)", price_excl_tax=5000)

# 商品データをセッションに追加（まだDBには反映されていない）
# session.add(new_product)
session.add(my_product)

# トランザクションをコミット（DBに変更を確定）
session.commit()

# 登録された商品を全件取得（SELECT * FROM products）
for product in session.query(Product).all():
    # 各商品の情報を1行ずつ表示（ID、名前、価格）
    print(product.product_id, product.name, product.price_excl_tax)
