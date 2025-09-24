import pytest
from pathlib import Path
from xbrl_utils import preview_xbrl_structure

@pytest.fixture
def sample_xbrl(tmp_path):
    """簡単なXBRLファイルを作成して返す"""
    xbrl_path = tmp_path / "sample.xbrl"
    xbrl_content = """<?xml version="1.0" encoding="UTF-8"?>
    <xbrl xmlns="http://www.xbrl.org/2003/instance">
        <jpcrp_cor:CompanyName xmlns:jpcrp_cor="http://disclosure.edinet-fsa.go.jp/namespace/jpcrp_cor">テスト株式会社</jpcrp_cor:CompanyName>
        <jpcrp_cor:NetSales xmlns:jpcrp_cor="http://disclosure.edinet-fsa.go.jp/namespace/jpcrp_cor">123456789</jpcrp_cor:NetSales>
    </xbrl>
    """
    xbrl_path.write_text(xbrl_content, encoding="utf-8")
    return xbrl_path

def test_preview_xbrl_structure_output(sample_xbrl, capsys):
    """XBRL構造の表示が正しく出力されるかを確認"""
    preview_xbrl_structure(sample_xbrl, max_elements=10)
    captured = capsys.readouterr()
    assert "sample.xbrl の内容" in captured.out or "ファイル: sample.xbrl" in captured.out
    assert "CompanyName" in captured.out
    assert "NetSales" in captured.out
    assert "テスト株式会社" in captured.out
    assert "123456789" in captured.out