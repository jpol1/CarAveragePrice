from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import time
from tqdm import tqdm

with open("config.json", "r", encoding="utf-8") as file:
    config_data = json.load(file)

CURRENT_PAGE = config_data["CURRENT_PAGE"]
END_PAGE = config_data["END_PAGE"]
OUTPUT_FILE = config_data["OUTPUT_FILE"]

SLEEP_LIST = config_data["SLEEP_LIST"]
SLEEP_DETAILS = config_data["SLEEP_DETAILS"]

driver = webdriver.Safari()
wait = WebDriverWait(driver, 15)


def update_config_current_page(page_number, config_file="config.json"):
    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["CURRENT_PAGE"] = page_number

    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)



def save_to_jsonl(new_data, filename=OUTPUT_FILE):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(json.dumps(new_data, ensure_ascii=False) + '\n')



def load_offerts_from_page(driver):
    time.sleep(SLEEP_LIST)
    offers = driver.find_elements(By.XPATH, "//a[contains(@href, '/oferta/')]")

    page_links = []
    for offer in offers:
        href = offer.get_attribute("href")
        if href and href not in page_links:
            page_links.append(href)

    return page_links



def prepare_dict_data(advert, params):
    def get_val(key):
        vals = params.get(key, {}).get('values', [])
        return vals[0].get('label') if vals else "brak"

    car_details = {
        "url": link,
        "price": advert.get('price', {}).get('value'),
        "currency": advert.get('price', {}).get('currency'),
        "make": get_val('make'),
        "model": get_val('model'),
        "year": get_val('year'),
        "mileage": get_val('mileage'),
        "engine_capacity": get_val('engine_capacity'),
        "engine_power": get_val('engine_power'),
        "fuel_type": get_val('fuel_type'),
        "gearbox": get_val('gearbox'),
        "body_type": get_val('body_type'),
        "color": get_val('color'),
        "is_imported": get_val('is_imported_car'),
        "region": advert.get('seller', {}).get('location', {}).get('region'),
        "city": advert.get('seller', {}).get('location', {}).get('city'),
        "seller_type": advert.get('seller', {}).get('featuresBadges', [{}])[0].get('label', "brak")
    }

    return car_details


def take_details_from_current_page(driver, link):
    driver.get(link)
    time.sleep(SLEEP_DETAILS)

    script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
    json_text = script_tag.get_attribute('innerHTML')
    full_data = json.loads(json_text)

    page_props = full_data.get('props', {}).get('pageProps', {})
    advert = page_props.get('advert', {})
    params = advert.get('parametersDict', {})

    car_details = prepare_dict_data(advert=advert, params=params)

    save_to_jsonl(car_details)

def get_total_pages(driver):
    try:
        pagination_buttons = driver.find_elements(By.CSS_SELECTOR, 'button.ooa-13ptg7a')

        if pagination_buttons:
            last_page_val = pagination_buttons[-1].text
            return int(last_page_val)
    except Exception as e:
        return None


if __name__ == '__main__':
    try:
        base_url = f"https://www.otomoto.pl/osobowe?page={CURRENT_PAGE}"
        driver.get(base_url)
        try:
            accept_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept_button.click()
        except:
            pass

        ACTUAL_END_PAGE = get_total_pages(driver)

        if ACTUAL_END_PAGE:
            print(f"ACTUAL_END_PAGE: {ACTUAL_END_PAGE}")
            END_PAGE = ACTUAL_END_PAGE

        for page in tqdm(range(CURRENT_PAGE, END_PAGE + 1), desc="Page progress"):
            list_url = f"https://www.otomoto.pl/osobowe?page={page}"
            driver.get(list_url)

            page_links = load_offerts_from_page(driver)

            update_config_current_page(page+1)

            for link in tqdm(page_links, desc=f"Downloading car data from page number: {page}", leave=False):
                try:
                    take_details_from_current_page(driver,link)
                except Exception as e:
                    continue

    except Exception as main_e:
        print(f"CRITICAL ERROR: {main_e}")

    finally:
        if driver:
            driver.quit()