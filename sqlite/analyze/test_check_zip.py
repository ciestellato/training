import pytest
from pathlib import Path
from edinet_config import Config
from check_zip import extract_csv_from_zip

def get_latest_zip_file() -> Path:
    zip_files = sorted(Config.SAVE_FOLDER.rglob("*.zip"))
    if not zip_files:
        raise FileNotFoundError(f"No ZIP files found in {Config.SAVE_FOLDER}")
    return zip_files[-1]

def test_extract_csv_from_zip():
    zip_path = get_latest_zip_file()
    extract_to = Path("./test_output")
    extract_to.mkdir(exist_ok=True)

    extracted_files = extract_csv_from_zip(str(zip_path), extract_to=str(extract_to))

    assert len(extracted_files) > 0, "CSVファイルが抽出されませんでした"
    for file in extracted_files:
        assert file.endswith(".csv")
        print(f"✅ 抽出されたCSV: {file}")