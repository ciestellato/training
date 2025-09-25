from sqlalchemy import Column, Integer, Text, DateTime, String, Date, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base 

class EdinetDocumentSummary(Base):
    """EDINET書類サマリーテーブルのSQLAlchemyモデル"""
    __tablename__ = 'edinet_document_summaries'
    
    # 主キー
    docID = Column(Text, primary_key=True) 
    
    # 基本情報
    seqNumber = Column(Integer)             # 連番
    edinetCode = Column(Text)              # 提出者EDINETコード
    secCode = Column(Text)                 # 提出者証券コード
    JCN = Column(Text)                     # 提出者法人番号 (エラーの原因)
    filerName = Column(Text)               # 提出者名
    fundCode = Column(Text)                # ファンドコード
    ordinanceCode = Column(Text)           # 府令コード
    formCode = Column(Text)                # 様式コード
    docTypeCode = Column(Text)             # 書類種別コード
    
    # 期間・日時
    periodStart = Column(Text)             # 期間（自）
    periodEnd = Column(Text)               # 期間（至）
    submitDateTime = Column(DateTime)      # 提出日時
    docDescription = Column(Text)          # 提出書類概要
    
    # 関連情報
    issuerEdinetCode = Column(Text)        # 発行会社EDINETコード
    subjectEdinetCode = Column(Text)       # 対象EDINETコード
    subsidiaryEdinetCode = Column(Text)    # 子会社EDINETコード
    currentReportReason = Column(Text)     # 臨報提出事由
    parentDocID = Column(Text)             # 親書類管理番号
    opeDateTime = Column(DateTime)         # 操作日時
    
    # ステータス・フラグ
    withdrawalStatus = Column(Text)        # 取下区分
    docInfoEditStatus = Column(Text)       # 書類情報修正区分
    disclosureStatus = Column(Text)        # 開示不開示区分
    xbrlFlag = Column(Text)                # XBRL有無フラグ
    pdfFlag = Column(Text)                 # PDF有無フラグ
    attachDocFlag = Column(Text)           # 代替書面・添付文書有無フラグ
    englishDocFlag = Column(Text)          # 英文ファイル有無フラグ
    csvFlag = Column(Text)                 # CSV有無フラグ
    legalStatus = Column(Text)             # 縦覧区分 (API仕様書№40)

    # 関連付けるリレーションシップ名を定義
    extracted_details = relationship("EdinetExtractedCsvDetails", back_populates="summary") # <- これも追加 (モデル定義にはありませんでしたが、リレーションシップのために必要)

class EdinetExtractedCsvDetails(Base):
    """CSV抽出詳細テーブルのモデル"""
    __tablename__ = 'edinet_extracted_csv_details'
    
    # 既存のテーブル構造に合わせてカラムを定義
    id = Column(Integer, primary_key=True, index=True)
    docID = Column(String, ForeignKey('edinet_document_summaries.docID'), nullable=False)
    csv_path = Column(String, unique=True, nullable=False)
    extracted_at = Column(Date)

    # リレーションシップ（オプション）
    summary = relationship("EdinetDocumentSummary", back_populates="extracted_details")

class EdinetFinancialData(Base):
    """財務データテーブルのモデル"""
    __tablename__ = 'edinet_financial_data'
    
    # 財務データの要素（例：element_id, value, context, unitなど）を定義
    id = Column(Integer, primary_key=True, index=True)
    docID = Column(String, nullable=False, index=True)
    element_id = Column(String, nullable=False)
    context_ref = Column(String)
    unit_ref = Column(String)
    value = Column(Float)
    
    # 必要に応じてインデックスを追加
    __table_args__ = (Index('idx_financial_data_lookup', 'docID', 'element_id'),) 