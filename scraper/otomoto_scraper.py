import requests
from bs4 import BeautifulSoup
import json
import time
import random
from tqdm import tqdm

with open("config.json", "r", encoding="utf-8") as file:
    config_data = json.load(file)

CURRENT_PAGE = config_data["CURRENT_PAGE"]
END_PAGE = config_data["END_PAGE"]
OUTPUT_FILE = config_data["OUTPUT_FILE"]
BASE_URL = config_data["BASE_URL"]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def update_config_current_page(page_number, config_file="config.json"):
    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["CURRENT_PAGE"] = page_number
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)



def save_to_jsonl(new_data, filename=OUTPUT_FILE):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(json.dumps(new_data, ensure_ascii=False) + '\n')


def get_next_data_json(url):
    response = requests.get(url, headers=HEADERS)
    if (response.status_code != 200):
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})

    if script_tag:
        return json.loads(script_tag.string)
    return None

def prepare_dict_data(advert, params, link):
    def get_val(key):
        vals = params.get(key, {}).get('values', [])
        return vals[0].get('label') if vals else "failure"

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
        "seller_type": advert.get('seller', {}).get('featuresBadges', [{}])[0].get('label', "")
    }

    return car_details


def load_offers_from_page(url_to_scan):
    try:
        response = requests.get(url_to_scan, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/oferta/' in href and 'otomoto.pl' in href:
                if href not in links:
                    links.append(href)
            elif href.startswith('/oferta/'):
                full_url = "https://www.otomoto.pl" + href
                if full_url not in links:
                    links.append(full_url)
        return links
    except Exception as e:
        with open("logs.txt", "a") as file:
            file.write(f"{e}\n")
        return None


def take_details_from_current_page(link):
    try:
        time.sleep(random.uniform(2,4.5))
        detail_data = get_next_data_json(link)

        if detail_data:
            page_props = detail_data.get('props', {}).get('pageProps', {})
            advert = page_props.get('advert', {})
            params = advert.get('parametersDict', {})

            car_data = prepare_dict_data(advert, params, link)
            return car_data
    except Exception as e:
        with open("logs.txt", "a") as file:
            file.write(f"{e}\n")
        return None


def get_total_pages(url):
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        pagination_buttons = soup.find_all("button", class_="ooa-13ptg7a")

        if pagination_buttons:
            last_page_text = pagination_buttons[-1].get_text()
            return int(last_page_text)

    except Exception as e:
        with open("logs.txt", "a") as file:
            file.write(f"{e}\n")
        return None


if __name__ == '__main__':
    try:
        ACTUAL_END_PAGE = get_total_pages(f"{BASE_URL}{CURRENT_PAGE}")

        if ACTUAL_END_PAGE:
            END_PAGE = ACTUAL_END_PAGE

        main_bar = tqdm(
            range(CURRENT_PAGE, END_PAGE + 1),
            desc="Total progress",
            position=0,
            colour='white',
        )

        for page in main_bar:
            curr_url = f"{BASE_URL}{page}"
            page_links = load_offers_from_page(curr_url)

            if not page_links:
                continue

            update_config_current_page(page + 1)

            sub_bar = tqdm(
                page_links,
                desc=f"Page {page}",
                position=1,
                leave=False,
                colour='white',
            )

            for link in sub_bar:
                try:
                    car_data = take_details_from_current_page(link)
                    if car_data:
                        save_to_jsonl(car_data)
                except Exception:
                    continue

            sub_bar.close()

            time.sleep(random.uniform(3, 6))

    except Exception as main_e:
        print(f"CRITICAL ERROR: {main_e}")