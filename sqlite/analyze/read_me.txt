ディレクトリ構造メモ

/edinet_analysis_project
├── config.py             # ① 全体の設定ファイル
├── edinet_main.py        # ② メインのエントリーポイント
├── requirements.txt      # 必要なライブラリの一覧（pip install -r 用）
│
├── /edinet_pipeline/     # ③ ソースコード本体 (Pythonパッケージ)
│   ├── __init__.py       # パッケージとして機能させるためのファイル
│   ├── base.py           # SQLAlchemy ORMのベース定義
│   ├── models.py         # ORMモデル (edinet_document_summariesなど)
│   ├── database.py       # DB接続、Engine/Session、初期化ロジック
│   ├── edinet_steps.py   # 高レベルの処理フロー制御 (step1〜step7)
│   ├── storage_repo.py   # DB永続化 (データ保存、読み出し) 処理
│   ├── file_processor.py # ファイルI/O、CSV抽出、解析ロジック
│   └── zip_utils.py      # ZIP操作など汎用的なユーティリティ
│
├── /data/                # ④ 実行時に生成されるデータ (永続化データ)
│   ├── edinet_data.db    # SQLiteデータベースファイル (Config.DB_PATH)
│   ├── /downloaded_zips/ # EDINET APIからダウンロードしたZIPファイルの保存先
│   └── /extracted_csvs/  # ZIPから抽出されたCSVデータの一時/永続保存先
│
└── /logs/                # ⑤ 実行ログファイル
    └── application.log   # ロギング出力先