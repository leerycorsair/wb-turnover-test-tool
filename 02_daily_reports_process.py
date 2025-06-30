import os
from typing import List
import zipfile
import pandas as pd
from tqdm import tqdm
from config import logger

BASE_DIR = os.path.dirname(__file__)
ZIP_DIR = os.path.join(BASE_DIR, "data/01-daily-reports-downloads")
MERGED_FILE = os.path.join(BASE_DIR, "data/02_01_daily_reports_merged.xlsx")
FILTERED_FILE = os.path.join(BASE_DIR, "data/02_02_daily_reports_filtered.xlsx")
TARGET_DAY = "2025-06-05"


def extract_excel_from_zip(zip_path: str) -> pd.DataFrame:
    dfs: List[pd.DataFrame] = []

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for inner_file in zip_ref.namelist():
            if inner_file.endswith((".xlsx", ".xls")):
                with zip_ref.open(inner_file) as excel_file:
                    df = pd.read_excel(excel_file)
                    df["source_zip"] = os.path.basename(zip_path)
                    dfs.append(df)

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def merge_daily_reports(zip_dir: str) -> pd.DataFrame:
    daily_reports = []
    zip_files = [f for f in os.listdir(zip_dir) if f.endswith(".zip")]

    for filename in tqdm(zip_files, desc="Merging ZIPs"):
        zip_path = os.path.join(zip_dir, filename)

        try:
            current_report = extract_excel_from_zip(zip_path)
            if not current_report.empty:
                daily_reports.append(current_report)
        except Exception as e:
            logger.error("Failed to process {filename}: {e}")

    return (
        pd.concat(daily_reports, ignore_index=True) if daily_reports else pd.DataFrame()
    )


def filter_daily_reports(src: pd.DataFrame, target_day: str) -> pd.DataFrame:
    dst = src[
        (src["Дата продажи"] == target_day)
        & (
            (
                (src["Тип документа"] == "Продажа")
                | (src["Обоснование для оплаты"] == "Продажа")
            )
            | (
                (src["Тип документа"] == "Возврат")
                | (src["Обоснование для оплаты"] == "Возврат")
            )
        )
        & (~src["Склад"].str.contains("Склад поставщика", na=False))
    ]

    return dst


def run_reports_process() -> None:
    merged_daily_reports_df = merge_daily_reports(ZIP_DIR)
    if not merged_daily_reports_df.empty:
        merged_daily_reports_df.to_excel(MERGED_FILE, index=False)
    else:
        logger.info("Merged data is empty!")

    filtered_daily_reports_df = filter_daily_reports(
        merged_daily_reports_df, TARGET_DAY
    )
    if not filtered_daily_reports_df.empty:
        filtered_daily_reports_df.to_excel(FILTERED_FILE, index=False)
    else:
        logger.info("Filtered data is empty!")


def main() -> None:
    logger.info("Starting report process script...")
    run_reports_process()


if __name__ == "__main__":
    main()
