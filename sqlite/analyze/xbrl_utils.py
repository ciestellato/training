import xml.etree.ElementTree as ET
from pathlib import Path

def preview_xbrl_structure(xbrl_path: Path, max_elements: int = 30):
    """XBRLファイルの構造をざっくり表示する（最初の max_elements 件）"""
    tree = ET.parse(xbrl_path)
    root = tree.getroot()

    print(f"🔎 ファイル: {xbrl_path.name}")
    print(f"ルートタグ: {root.tag}")
    print("主要タグ一覧（先頭から最大30件）:")
    for i, elem in enumerate(root.iter()):
        if i >= max_elements:
            print("...（省略）")
            break
        print(f"  - {elem.tag} : {elem.text.strip() if elem.text else ''}")