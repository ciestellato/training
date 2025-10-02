import os
from typing import List, Tuple
from pathlib import Path

# --- 必要なモジュールのインポート（ソースコードの構成を想定） ---
# 実際のプロジェクト構造に合わせてインポートパスを調整してください。
# ここでは、edinet_models, database_setup, edinet_config が利用可能と仮定します。

# モデルと設定クラス
from edinet_config import Config
from .edinet_models import EdinetDocumentSummary, EdinetExtractedCsvDetails
from .database_setup import get_db

# 仮のインポートとクラス定義（実行可能なダミーとして）
class DummyConfig:
    # ベースディレクトリの例 (ソースに基づきC:/EDINET_DB/02_extracted_csv_temp/を想定) [4]
    BASE_DIR = Config.BASE_DIR
    EXTRACTED_CSV_TEMP_FOLDER = Config.EXTRACTED_CSV_TEMP_FOLDER

# 実際のORMモデルを使用するため、ここでは概念的にインポートとして扱います。
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import Column, Text, String, Integer, ForeignKey

# 以下のクラスは、ソース [1, 3, 5] に基づく構造を再現しています
Base = declarative_base()
class EdinetDocumentSummary(Base):
    __tablename__ = 'edinet_document_summaries'
    docID = Column(Text, primary_key=True)
    filerName = Column(Text)
    docTypeCode = Column(Text)
    # リレーションシップの定義 (EdinetExtractedCsvDetails側で定義されている想定)
    extracted_details = relationship("EdinetExtractedCsvDetails", back_populates="summary")
class EdinetExtractedCsvDetails(Base):
    __tablename__ = 'edinet_extracted_csv_details'
    id = Column(Integer, primary_key=True)
    docID = Column(String, ForeignKey('edinet_document_summaries.docID'), nullable=False)
    csv_path = Column(String)
    summary = relationship("EdinetDocumentSummary", back_populates="extracted_details")


# データベース接続のヘルパー関数 (ソースの get_db() の動作をシミュレート)
# 実際のアプリケーションでは、database_setup.pyからget_db()を利用してください [7, 8]
TEMP_DB_PATH = Path(DummyConfig.BASE_DIR / "temp_edinet_search.db")
engine = create_engine(f"sqlite:///{TEMP_DB_PATH}", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# ---------------------------------------------------------------------------------


def search_and_return_csv_paths(company_name: str, doc_type_code: str) -> List[Path]:
    """
    会社名と書類種別コードに基づき、対応するCSVファイルの絶対パスを検索して返却する。
    """
    absolute_paths: List[Path] = []
    
    # SQLAlchemyのセッションを使用 (get_db() はトランザクション管理を行うヘルパー関数)
    try:
        # DB接続とクエリ実行 (get_db()はイテレータなのでnext()でSessionを取得する代わりに、
        # 実際のプロジェクト構成に合わせてwith文を使用します)
        with SessionLocal() as db: # ここではSessionLocal()を直接使用
            
            # ORM結合クエリ
            results = db.query(
                EdinetDocumentSummary.docID,
                EdinetExtractedCsvDetails.csv_path
            ).join(
                EdinetExtractedCsvDetails,
                EdinetDocumentSummary.docID == EdinetExtractedCsvDetails.docID
            ).filter(
                # 会社名（filerName）の部分一致検索
                EdinetDocumentSummary.filerName.like(f"%{company_name}%"),
                # 書類種別コード（docTypeCode）での厳密なフィルタリング
                EdinetDocumentSummary.docTypeCode == doc_type_code
            ).all()

    except Exception as e:
        # エラー処理
        print(f"データベース検索中にエラーが発生しました: {e}")
        return []

    # 取得結果に基づいて絶対パスを構築
    for doc_id, relative_path in results:
        # 絶対パスの構造：BASE_FOLDER / docID / XBRL_TO_CSV / relative_path
        # file_processor.py のロジックに基づき、パスを構築します [9]。
        base_path = DummyConfig.EXTRACTED_CSV_TEMP_FOLDER
        
        # 中間パス: docID / "XBRL_TO_CSV"
        intermediate_path = Path(doc_id) / "XBRL_TO_CSV"
        
        # 絶対パスの完成
        absolute_path = base_path / intermediate_path / relative_path
        absolute_paths.append(absolute_path)
        
    return absolute_paths

# --- 実行例 (ダミーデータの準備が必要なため、ここでは概念的な結果のみ) ---
# 実際のデータベースとファイルシステムが構築されていれば、上記関数が機能します。

# ダミーデータの挿入 (テスト用)
if not TEMP_DB_PATH.exists():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        # サマリーデータ
        summary1 = EdinetDocumentSummary(docID='S1000001', filerName='エディネット株式会社', docTypeCode='120')
        # CSV詳細データ
        csv_detail1 = EdinetExtractedCsvDetails(docID='S1000001', csv_path='jpfr-001_S1000001-000_2024-03-31_01.csv')
        db.add_all([summary1, csv_detail1])
        db.commit()

# 検索条件の例 (有価証券報告書: '120')
# company_to_search = "エディネ"
# doc_type = "120"

# # 検索実行
# found_paths = search_and_return_csv_paths(company_to_search, doc_type)

# print("\n--- 検索結果 (SQLAlchemy & パス構築) ---")
# for path in found_paths:
#     print(path)