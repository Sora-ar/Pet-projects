import time
import csv
import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(
    filename='scraper_selenium.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


def initialize_driver():
    # Вкажіть шлях до Edge WebDriver
    service = Service(
        'C:/Users/Admin/Downloads/edgedriver_win64/msedgedriver.exe')  # Змініть на ваш реальний шлях до Edge WebDriver

    options = Options()
    options.add_argument('--headless')  # Запуск у фоновому режимі
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    driver = webdriver.Edge(service=service, options=options)
    logging.info("Ініціалізовано веб-драйвер Microsoft Edge.")
    return driver


def load_all_companies(driver, url):
    try:
        driver.get(url)
        logging.info(f"Відкрито URL: {url}")
        time.sleep(2)  # Зачекайте, поки сторінка завантажиться

        # Отримуємо початковий список компаній
        existing_companies = set()
        existing_companies.update(
            company.text.strip() for company in driver.find_elements(By.CSS_SELECTOR, 'div.company a.cn-a'))

        while True:
            try:
                # Знайдіть кнопку "більше інформації" за її текстом
                button = driver.find_element(By.XPATH, "//a[contains(text(), 'Більше компаній')]")
                driver.execute_script("arguments[0].click();", button)
                logging.info("Натиснута кнопка 'Більше компаній'")

                # Явне очікування на нові компанії
                WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.company a.cn-a'))
                )

                # Отримуємо новий список компаній
                new_companies = set()
                new_companies.update(
                    company.text.strip() for company in driver.find_elements(By.CSS_SELECTOR, 'div.company a.cn-a'))

                # Перевіряємо, чи з'явилися нові компанії
                if new_companies != existing_companies:
                    existing_companies.update(new_companies)
                    logging.info("Завантажено нові компанії.")
                else:
                    logging.info("Не знайдено нових компаній.")
                    break

            except NoSuchElementException:
                logging.info("Всі компанії завантажені.")
                break
            except ElementClickInterceptedException:
                logging.warning("Не вдалося натиснути кнопку 'Більше компаній'. Можливо, вона вже недоступна.")
                break
    except Exception as e:
        logging.exception(f"Виникла помилка при завантаженні сторінки: {e}")


def extract_companies(driver):
    companies_data = []
    try:
        companies = driver.find_elements(By.CSS_SELECTOR, 'div.company')  # Перевір актуальний селектор
        logging.info(f"Знайдено {len(companies)} компаній для парсингу.")

        for company in companies:
            try:
                name_element = company.find_element(By.CSS_SELECTOR, 'a.cn-a')  # Перевір актуальний селектор
                location_element = company.find_element(By.CSS_SELECTOR,
                                                        'span.city.bi.bi-geo-alt-fill')  # Перевір актуальний селектор

                name = name_element.text.strip()
                location = location_element.text.strip()

                if 'Харків' in location:
                    companies_data.append([name, location])
                    logging.info(f"Знайдена компанія: {name} | Локація: {location}")
            except NoSuchElementException:
                logging.warning("Не вдалося знайти назву або локацію для однієї з компаній.")
                continue
            except Exception as e:
                logging.exception(f"Виникла помилка при парсингу компанії: {e}")
                continue
    except Exception as e:
        logging.exception(f"Виникла помилка при знаходженні компаній на сторінці: {e}")

    return companies_data


def save_to_csv(data, filename='companies_harkiv.csv'):
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Назва компанії', 'Локація'])
            writer.writerows(data)
        logging.info(f"Дані успішно збережено у файлі {filename}")
    except Exception as e:
        logging.exception(f"Виникла помилка при збереженні CSV-файлу: {e}")


def main():
    driver = initialize_driver()
    try:
        url = 'https://jobs.dou.ua/companies/?name=Харків'
        load_all_companies(driver, url)
        companies = extract_companies(driver)
        if companies:
            save_to_csv(companies)
        else:
            logging.info("Не знайдено жодної компанії з Харковом у локації.")
    finally:
        driver.quit()
        logging.info("Закрито веб-драйвер.")


if __name__ == "__main__":
    main()
