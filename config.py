from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
import time

USER_DATA_DIR = "SOME PATH"
TARGET_PERIOD_START = "01-06-2025"
TARGET_PERIOD_END = "29-06-2025"


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def init_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument(f"user-data-dir={USER_DATA_DIR}")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


def main() -> None:
    logger.info("Starting configuring profile script...")
    driver = init_driver()
    time.sleep(300)


if __name__ == "__main__":
    main()
