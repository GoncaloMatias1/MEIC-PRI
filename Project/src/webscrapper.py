
import requests, os, csv
from bs4 import BeautifulSoup
from bs4.element import Comment

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

HEADERS = headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
URLS_PATH = "url_out/urls.txt"
OUT = "webscrapper_out"
FILENAME = "ign.csv"
CSV_HEADERS = ["Title", "Subtitle", "Subheader", "Content", "Score"]

# Get urls
with open(URLS_PATH, "r") as f:
    urls = f.readlines()

# remove '\n' chars from urls
urls = list(map(lambda s: s[:-1], urls))

# Define constants for DOM traversal
class HTML:
    DIV = "div"
    P = "p"
    H1 = "h1"
    H2 = "h2"
    SECTION = "section"
class ID: # id
    MAIN_CONTENT = "main-content"
class Class: # class
    PAGE_HEADER = "page-header"
    PAGE_CONTENT = "page-content"
    WATCH_READ_VIDEO = "watch-read-video"
    ARTICLE_AUTHORS = "article-authors"
    CAPTION = "caption"
    ARTICLE_CONTENT = "article-content"
    ARTICLE_PAGE = "article-page"
    DISPLAY_TITLE = "display-title"
    TITLE3 = "title3"
class Data: # data-cy
    ARTICLE_HEADLINE = "article-headline"
    ARTICLE_SUB_HEADLINE = "article-sub-headline"
    VERDICT = "verdict"

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body):
    texts = body.find_all(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)

def tag_to_string(tag):
    if tag is None: return ""
    return tag.string

# Eliminate out file if already exists.
out_filename = f"{OUT}/{FILENAME}"
if os.path.isfile(out_filename):
    os.remove(out_filename)

# Iterate through each url and extract information into dabase
print(f"Extracting information into \"{out_filename}\".")
prev_url_size = 0
with open(out_filename, "a+") as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow(CSV_HEADERS)
    for i, url in enumerate(urls):
        perc = i / len(urls) * 100
        print(f"\r[{perc:.2f}% {i+1}/{len(urls)}] Getting \"{url}\"{' ' * (max(0, prev_url_size - len(url)))}", end="")
        prev_url_size = len(url)
        resp = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(resp.content, "html.parser")
        content_divs = soup.find_all(HTML.DIV, class_=Class.PAGE_CONTENT)
        if len(content_divs) != 6:
            print(f"\r[ERROR] \"{url}\" has {len(content_divs)} divs not 6.")
            continue
        header, sub_header, page_content, summary, *_ = content_divs
        try:
            title = tag_to_string(header.css.select_one(f"{HTML.H1}.{Class.DISPLAY_TITLE}"))
            subtitle = tag_to_string(header.css.select_one(f"{HTML.H2}.{Class.TITLE3}"))
            subheader = text_from_html(sub_header)
            content = text_from_html(page_content.css.select_one(f"{HTML.SECTION}.{Class.ARTICLE_PAGE}"))
            score = summary.figcaption.string
            csvwriter.writerow([title, subtitle, subheader, content, score])
        except Exception as e:
            print(f"\n[Error] {e}")
print("\nFinished.")
