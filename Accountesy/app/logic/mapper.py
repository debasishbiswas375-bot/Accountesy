from bs4 import BeautifulSoup

def parse_master(html):
    soup = BeautifulSoup(html, "html.parser")
    ledgers = []

    for td in soup.find_all("td"):
        text = td.text.strip()
        if text:
            ledgers.append(text.lower())

    return ledgers
