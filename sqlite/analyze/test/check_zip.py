from pathlib import Path
import zipfile

def preview_zip_contents(zip_path: Path, max_files: int = 50):
    """ZIPファイルの中身を表示する"""
    if not zip_path.exists():
        print(f"❌ ファイルが見つかりません: {zip_path}")
        return

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            print(f"📦 ZIPファイル: {zip_path.name}")
            print(f"📁 含まれるファイル数: {len(file_list)}")
            print("🔍 ファイル一覧:")
            for i, f in enumerate(file_list):
                if i >= max_files:
                    print("...（省略）")
                    break
                print(f"  - {f}")
    except zipfile.BadZipFile:
        print(f"⚠️ ZIPファイルが壊れている可能性があります: {zip_path}")

def extract_csv_from_zip(zip_path: str, extract_to: str = "./extracted_csv"):
    """ZIPファイルからCSVファイルのみを抽出する"""
    zip_path = Path(zip_path)
    extract_to = Path(extract_to)
    extract_to.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
            zip_ref.extractall(path=extract_to, members=csv_files)
            return [str(extract_to / f) for f in csv_files]
    except zipfile.BadZipFile:
        print(f"⚠️ ZIPファイルが壊れている可能性があります: {zip_path}")
        return []