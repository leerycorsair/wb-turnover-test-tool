from typing import Tuple
from config import logger
import pandas as pd
from tqdm import tqdm

DAILY_REPORTS_FILE = "data/02_02_daily_reports_filtered.xlsx"
STOCK_HISTORY_FILE = "data/03_stock_history.xlsx"
STOCK_HISTORY_SHEET = "Остатки по дням"
RESULTS_FILE = "data/03_turnover_all.xlsx"


def process_stock_history(target_nm: int) -> Tuple[int, bool]:
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
    is_found = False
    if not filtered_df.empty:
        stocks_sum = (
            filtered_df[stocks_cols].select_dtypes(include="number").sum(axis=1).iloc[0]
        )
        is_found = True

    return stocks_sum, is_found


def process_daily_reports(df: pd.DataFrame, target_nm: int) -> Tuple[int, int]:
    filtered_df = df[df["Код номенклатуры"] == target_nm]
    counts = filtered_df["Тип документа"].value_counts()
    sales, refunds = counts.get("Продажа", 0), counts.get("Возврат", 0)

    return sales, refunds


def run_calc_turnover_all() -> None:
    df = pd.read_excel(DAILY_REPORTS_FILE)
    unique_nms = df["Код номенклатуры"].dropna().unique()

    results = []
    for target_nm in tqdm(unique_nms, "Processing NMs"):
        try:
            stocks, is_found = process_stock_history(target_nm)
            sales, refunds = process_daily_reports(df, target_nm)
            turnover = stocks / (sales - refunds) if (sales - refunds) != 0 else None

            results.append(
                {
                    "nm_id": target_nm,
                    "is_found": is_found,
                    "stocks": stocks,
                    "sales": sales,
                    "refunds": refunds,
                    "turnover": turnover,
                }
            )
        except Exception as e:
            logger.error(f"Error processing nm = {target_nm}: {e}")

    results_df = pd.DataFrame(results)
    results_df.to_excel(RESULTS_FILE, index=False)


def main() -> None:
    logger.info("Starting calc turnover script...")
    run_calc_turnover_all()


if __name__ == "__main__":
    main()
