import pytest
from pathlib import Path
from zip_utils import inspect_zip_contents, extract_xbrl_from_zip
import zipfile

@pytest.fixture
def sample_zip(tmp_path):
    """一時的なZIPファイルを作成して返す"""
    zip_path = tmp_path / "test_sample.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.writestr("XBRL/PublicDoc/sample.xbrl", "<xbrl>...</xbrl>")
        zipf.writestr("README.txt", "This is a test file.")
    return zip_path

def test_inspect_zip_contents_valid(sample_zip):
    """正常なZIPファイルの中身を確認"""
    contents = inspect_zip_contents(sample_zip)
    assert "XBRL/PublicDoc/sample.xbrl" in contents
    assert "README.txt" in contents
    assert len(contents) == 2

def test_inspect_zip_contents_missing():
    """存在しないZIPファイルを指定した場合"""
    fake_path = Path("non_existent.zip")
    contents = inspect_zip_contents(fake_path)
    assert contents == []

def test_inspect_zip_contents_corrupt(tmp_path):
    """壊れたZIPファイルを指定した場合"""
    corrupt_zip = tmp_path / "corrupt.zip"
    corrupt_zip.write_text("これはZIPではありません")
    contents = inspect_zip_contents(corrupt_zip)
    assert contents == []

def test_extract_xbrl_from_zip_valid(sample_zip, tmp_path):
    """正常なZIPからXBRLファイルを抽出できるか"""
    extract_dir = tmp_path / "extracted"
    extracted_files = extract_xbrl_from_zip(sample_zip, extract_dir)

    assert len(extracted_files) == 1
    assert extracted_files[0].name == "sample.xbrl"
    assert extracted_files[0].exists()
    assert extracted_files[0].read_text().startswith("<xbrl>")

def test_extract_xbrl_from_zip_no_xbrl(tmp_path):
    """XBRLファイルが含まれていないZIPの処理"""
    zip_path = tmp_path / "no_xbrl.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.writestr("README.txt", "No XBRL here.")
    extract_dir = tmp_path / "extracted"
    extracted_files = extract_xbrl_from_zip(zip_path, extract_dir)

    assert extracted_files == []

def test_extract_xbrl_from_zip_corrupt(tmp_path):
    """壊れたZIPファイルの処理"""
    corrupt_zip = tmp_path / "corrupt.zip"
    corrupt_zip.write_text("Not a zip file")
    extract_dir = tmp_path / "extracted"
    extracted_files = extract_xbrl_from_zip(corrupt_zip, extract_dir)

    assert extracted_files == []