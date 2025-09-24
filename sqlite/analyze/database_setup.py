from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from edinet_models import Base
from edinet_config import Config

# Config.DB_PATH は既存ソースのConfigクラスに定義されていると想定
DATABASE_URL = f"sqlite:///{Config.DB_PATH}"

# エンジンの定義 (データベースへの接続インターフェース)
Engine = create_engine(DATABASE_URL)

def initialize_database():
    """データベーススキーマ（テーブル）が存在しなければ作成する"""
    import logging
    logging.info("🛠️ データベーススキーマの初期化を開始します。")
    # Base.metadata に登録されている全てのテーブルをデータベースに作成
    Base.metadata.create_all(Engine)
    logging.info("✅ データベーススキーマの初期化が完了しました。")

# セッションファクトリの定義 (操作単位のコンテナ)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

# 依存性注入（DI）のためのセッション取得ヘルパー関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()