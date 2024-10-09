
from bs4 import BeautifulSoup

# Get urls
with open("url_out/urls.txt", "r") as f:
    urls = f.readlines()

# remove '\n' chars
urls = list(map(lambda s: s[:-1], urls))

# TODO: Iterate through each url and extract information into dabase
