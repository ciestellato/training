from sqlalchemy import Column, Integer, Text, DateTime
from base import Base 

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