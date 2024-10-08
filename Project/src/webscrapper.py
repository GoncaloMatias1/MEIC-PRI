from bs4 import BeautifulSoup

SELENIUM_OUT = "selenium_out"
OUT = "webscrapper_out"
SCORES = (
    "10,10",
    "9.0,9.9",
    "8.0,8.9",
    "7.0,7.9",
    "6.0,6.9",
    "5.0,5.9",
    "4.0,4.9",
    "3.0,3.9",
    "2.0,2.9",
    "1.0,1.9",
    "0.0,0.9",
)

BASE_URL = "https://www.ign.com"

urls = []
for score in SCORES:
    try:
        with open(f"{SELENIUM_OUT}/result{score.split(',')[0]}.html", "r") as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        # Parse soup
        games = soup.find_all('div', class_='content-item')
        with open(f"{OUT}/urls.txt", "a+") as f:
            for game in games:
                f.write(f"{BASE_URL}{game.a["href"]}\n")
    except FileNotFoundError:
        continue

# TODO: Go to each website and scrape the information needed