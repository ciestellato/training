from pathlib import Path
import zipfile
import logging

def inspect_zip_contents(zip_path: Path) -> list[str]:
    """
    指定されたZIPファイルの中身（ファイル名一覧）を返す。
    """
    if not zip_path.exists():
        logging.warning(f"ZIPファイルが存在しません: {zip_path}")
        return []

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            logging.info(f"{zip_path.name} の内容:")
            for f in file_list:
                logging.info(f"  - {f}")
            return file_list
    except zipfile.BadZipFile:
        logging.error(f"ZIPファイルが壊れている可能性があります: {zip_path}")
        return []

def extract_xbrl_from_zip(zip_path: Path, extract_to: Path) -> list[Path]:
    """
    ZIPファイルからXBRLファイルを抽出し、指定フォルダに保存。
    抽出されたファイルのパス一覧を返す。
    """
    extracted_files = []
    if not zip_path.exists():
        logging.warning(f"ZIPファイルが存在しません: {zip_path}")
        return []

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.lower().endswith(".xbrl"):
                    zip_ref.extract(file_name, path=extract_to)
                    extracted_files.append(extract_to / file_name)
        logging.info(f"{len(extracted_files)} 件のXBRLファイルを抽出しました。")
        return extracted_files
    except zipfile.BadZipFile:
        logging.error(f"ZIPファイルが壊れている可能性があります: {zip_path}")
        return []

def extract_csv_from_zip(zip_path: Path, extract_to: Path) -> list[Path]:
    """ZIPファイルからCSVファイルを抽出し、保存先を返す"""
    extracted_files = []
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.lower().endswith(".csv"):
                zip_ref.extract(file_name, path=extract_to)
                extracted_files.append(extract_to / file_name)
    return extracted_files