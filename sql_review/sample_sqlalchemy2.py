# SQLiteデータベースとの接続を行うためのエンジンを作成
from sqlalchemy import create_engine

# テーブルのカラム定義に使用する型や属性をインポート
from sqlalchemy import Column, Integer, Text

# モデルクラスのベースとなるクラスを定義（全モデル共通の親クラス）
from sqlalchemy.orm import declarative_base

# モデル定義のベースクラスを生成（このクラスを継承して各テーブルを定義）
Base = declarative_base()

# 顧客テーブルに対応するモデルクラスを定義
class Customer(Base):
    __tablename__ = "customers"  # このクラスが対応するSQLテーブル名

    # 顧客ID：主キー（PRIMARY KEY）、自動採番（AUTOINCREMENT）
    customer_id = Column(Integer, primary_key=True, autoincrement=True)

    # 電話番号：NULL不可（必須項目）
    phone = Column(Text, nullable=False)

    # 名前（カナ表記）：NULL不可（必須項目）
    name_kana = Column(Text, nullable=False)

    # 住所：NULL可（任意項目）
    address = Column(Text)

    # 備考：NULL可（任意項目）
    notes = Column(Text)

# SQLiteデータベースに接続するエンジンを作成（ファイル名は "alchemydb"）
# echo=True にすると、SQL実行ログがコンソールに表示される（学習・デバッグに便利）
engine = create_engine("sqlite:///alchemydb", echo=True)

# 顧客モデル（Customer）に対応するテーブルだけをデータベースに作成
# 全モデルではなく、特定のモデルのみを明示的に作成する方法
Customer.__table__.create(bind=engine)

# 作成されたテーブルのカラム情報を1つずつ表示
# 各カラムの名前・型・NULL許可の有無を確認できる（Safe設計の検証にも有効）
for column in Customer.__table__.columns:
    print(f"カラム名: {column.name}, 型: {column.type}, NULL許可: {column.nullable}")
