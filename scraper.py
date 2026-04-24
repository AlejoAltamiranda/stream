import requests
from bs4 import BeautifulSoup
import json
import re
from dateutil import parser
import pytz

BASE_URL = "https://sharkstreams.net/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_html(url):
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text


# 🔥 convertir hora a UTC
def convert_to_utc(date_str):
    try:
        dt = parser.parse(date_str)

        # si no tiene timezone, asumimos US Eastern (como en tu web)
        if dt.tzinfo is None:
            dt = pytz.timezone("US/Eastern").localize(dt)

        dt_utc = dt.astimezone(pytz.utc)

        return dt_utc.strftime("%Y-%m-%d %H:%M UTC")

    except Exception:
        return date_str


def extract_channel_links(html):
    soup = BeautifulSoup(html, "html.parser")

    results = []

    rows = soup.find_all("div", class_="row")

    for row in rows:
        category = row.find("span", class_="ch-category")
        name = row.find("span", class_="ch-name")
        date = row.find("span", class_="ch-date")

        onclick_links = row.find_all("a", onclick=True)

        for a in onclick_links:
            onclick = a.get("onclick", "")

            match = re.search(r"player\.php\?channel=(\d+)", onclick)
            if match:
                channel_id = match.group(1)

                player_url = f"{BASE_URL}player.php?channel={channel_id}"

                results.append({
                    "title": name.text.strip() if name else None,
                    "category": category.text.strip() if category else None,
                    "time": convert_to_utc(date.text.strip()) if date else None,
                    "channel": channel_id,
                    "link": player_url
                })

    return results


def save_json(data):
    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    print("🚀 Scraping started...")

    html = get_html(BASE_URL)
    data = extract_channel_links(html)

    save_json(data)

    print(f"✅ Done - {len(data)} events saved to events.json")


if __name__ == "__main__":
    main()
