from typing import Tuple
from config import logger
import pandas as pd

TARGET_NM = 391624100
DAILY_REPORTS_FILE = "data/02_02_daily_reports_filtered.xlsx"
STOCK_HISTORY_FILE = "data/03_stock_history.xlsx"
STOCK_HISTORY_SHEET = "Остатки по дням"


def process_stock_history(target_nm: int) -> int:
    df = pd.read_excel(STOCK_HISTORY_FILE, STOCK_HISTORY_SHEET, header=1)

    filtered_df = df[df["Артикул WB"] == target_nm]
    exclude_cols = {
        "Артикул продавца",
        "Название",
        "Артикул WB",
        "Предмет",
        "Бренд",
        "Размер",
    }

    stocks_cols = [col for col in filtered_df.columns if col not in exclude_cols]

    stocks_sum = 0
    if not filtered_df.empty:
        stocks_sum = (
            filtered_df[stocks_cols].select_dtypes(include="number").sum(axis=1).iloc[0]
        )
        logger.info(f"Total stocks for nm = {target_nm}: {stocks_sum}")
    else:
        logger.info(f"No data for nm = {target_nm}")

    return stocks_sum


def process_daily_reports(target_nm: int) -> Tuple[int, int]:
    df = pd.read_excel(DAILY_REPORTS_FILE)

    filtered_df = df[df["Код номенклатуры"] == target_nm]
    counts = filtered_df["Тип документа"].value_counts()
    sales, refunds = counts.get("Продажа", 0), counts.get("Возврат", 0)

    logger.info(f"Total sales, refunds for nm = {target_nm}: {sales}, {refunds}")

    return sales, refunds


def run_calc_turnover() -> None:
    stocks = process_stock_history(TARGET_NM)
    sales, refunds = process_daily_reports(TARGET_NM)

    turnover = stocks / (sales - refunds)
    logger.info(f"Turnover for nm = {TARGET_NM}: {turnover}")


def main() -> None:
    logger.info("Starting calc turnover script...")
    run_calc_turnover()


if __name__ == "__main__":
    main()
