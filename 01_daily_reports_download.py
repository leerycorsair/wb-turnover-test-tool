import time
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import USER_DATA_DIR, logger

TARGET_PERIOD_START = "01-06-2025"
TARGET_PERIOD_END = "29-06-2025"


BASE_URL = "https://seller.wildberries.ru/suppliers-mutual-settlements/reports-implementations/reports-daily"
LOAD_MORE_BUTTON = "button.button__WxukyZSSBr.m__WSfuD3QEjL.circle__HIpDhc3nT5"
TABLE_ROWS = ".Reports-table-body__Xh5u-EhEHC > *"
REPORT_NUMBER_CELL = "div[class^='Chips__text__']"
DOWNLOAD_BUTTON = "//button[.//span[text()='Скачать Excel']]"
CALENDAR_PRELOADER = "Preloader__o36toMBkqQ"
CALENDAR_BUTTON = "Date-input__icon-button__To06OLP0uu"


def init_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument(f"user-data-dir={USER_DATA_DIR}")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


def build_report_url(report_id: str) -> str:
    return f"{BASE_URL}/report/{report_id}?isGlobalBalance=false"


def set_date_filter(
    driver: webdriver.Chrome,
    wait: WebDriverWait,
    start_date: str,
    end_date: str,
) -> None:
    logger.info(f"Setting date range: {start_date} to {end_date}")
    time.sleep(2)

    try:
        WebDriverWait(driver, 20).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, CALENDAR_PRELOADER))
        )

        calendar_button = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, CALENDAR_BUTTON))
        )
        calendar_button.click()
        time.sleep(1)

        start_input = wait.until(EC.presence_of_element_located((By.ID, "startDate")))
        end_input = wait.until(EC.presence_of_element_located((By.ID, "endDate")))

        start_input.clear()
        start_input.send_keys(start_date)
        time.sleep(0.5)

        end_input.clear()
        end_input.send_keys(end_date)
        time.sleep(0.5)

        end_input.send_keys("\n")
        time.sleep(3)

    except Exception as e:
        logger.error(f"Failed to set date range: {e}")


def load_all_report_rows(
    driver: webdriver.Chrome,
    wait: WebDriverWait,
    start_date: str,
    end_date: str,
) -> None:
    driver.get(BASE_URL)
    set_date_filter(driver, wait, start_date, end_date)

    while True:
        rows = driver.find_elements(By.CSS_SELECTOR, TABLE_ROWS)
        logger.info(f"Rows loaded: {len(rows)}")

        try:
            load_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, LOAD_MORE_BUTTON))
            )
            if load_button.is_displayed() and load_button.is_enabled():
                load_button.click()
                time.sleep(3)
        except Exception as e:
            logger.warning(f"Load more failed or button missing: {e}")
            break


def get_report_ids(driver: webdriver.Chrome) -> List[str]:
    elements = driver.find_elements(By.CSS_SELECTOR, REPORT_NUMBER_CELL)
    ids = [
        el.text.strip()
        for el in elements
        if el.text.isdigit() and len(el.text.strip()) == 12
    ]

    return ids


def download_report_excel(driver: webdriver.Chrome, report_url: str) -> None:
    logger.info(f"Opening report: {report_url}")
    driver.get(report_url)
    wait = WebDriverWait(driver, 10)

    try:
        download_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, DOWNLOAD_BUTTON))
        )
        download_button.click()
        logger.info("Triggered Excel download.")
        time.sleep(3)
    except Exception as e:
        logger.error(f"Download failed: {e}")


def run_report_downloads(
    driver: webdriver.Chrome, start_date: str, end_date: str
) -> None:
    wait = WebDriverWait(driver, 20)
    load_all_report_rows(driver, wait, start_date, end_date)
    report_numbers = get_report_ids(driver)

    for report_id in report_numbers:
        report_url = build_report_url(report_id)
        download_report_excel(driver, report_url)


def main() -> None:
    logger.info("Starting report download script...")
    driver = init_driver()

    try:
        run_report_downloads(driver, TARGET_PERIOD_START, TARGET_PERIOD_END)
    finally:
        driver.quit()
        logger.info("Script complete. Browser closed.")


if __name__ == "__main__":
    main()
