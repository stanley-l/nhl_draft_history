
""" 
Scrape http://www.hockeydb.com/ihdb/draft/ to collect NHL draft history.
"""

import csv
import datetime
import os
import time
import random
import re
import requests
from bs4 import BeautifulSoup as BS


def get_data(url):
    """(str) -> str
    Access url using requests, get content of that page and return it as str
    """
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
              'Accept-language': 'en-US,en;q=0.5'}
    try:
        content = requests.get(url, headers=header)
    except Exception:
        return None
    return content.text


def draft_links(url):
    """(str) -> list of str
    Get links to pages with draft data per year.
    """
    root_url = 'http://www.hockeydb.com'
    content = get_data(url)
    # Get links from 'draft-container' table, 'draft_line' rows.
    soup = BS(content, 'html.parser')
    table = soup.find('div', {'class': 'draft_container'})
    links = table.find_all('div', {'class': 'draft_line'})
    # Construct destination links using concatenation of base_url and parsed internal link.
    return [root_url + link.a.get('href') for link in links]


def clean_string(s):
    """ (str) -> str
    """
    s = re.sub('[^a-zA-Z0-9 ]', '', s)    # remove characters that are not letters, digits or spaces
    s = re.sub(' {2,}', ' ', s)           # replace sequences of multiple spaces with single space
    return s.strip()


def write_to_csv(data, path):
    """ (iterable, str) -> NoneType
    """
    with open(path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        for item in data:
            writer.writerow(item)


def scrape_data(html):
    """ (str) -> list of lists of str
    """
    soup = BS(html, 'html.parser')
    page_title = soup.find('h1', {'class': 'title'}).text
    # Get draft year from title page.
    year = page_title.split()[0]
    # Remove empty and decorative rows that contain 'hideme' text in class name.
    for item in soup.find_all('tr', {'class': 'hideme'}):
        item.decompose()
    # Get data from table with draft information.
    table = soup.find('table', {'class': 'sortable autostripe'}).tbody
    rows = table.find_all('tr')
    data = []
    for row in rows:
        rowdata = [year]
        for cell in row:
            try:
                rowdata.append(clean_string(cell.get_text()))
            except AttributeError:
                pass
        data.append(rowdata)
    print('{} data collected'.format(year))    
    return data
    
    
def hockeydb_scrape_main():
    URL = 'http://www.hockeydb.com/ihdb/draft/'
    links = draft_links(URL)
    date = datetime.datetime.today().strftime('%Y%m%d')
    os.makedirs('draft_history', exist_ok=True)
    filename = os.path.join('draft_history', 'nhl_draft_history_{}.csv'.format(date))
    # Create csv file (if it does not yet exist) and write header. 
    if not os.path.exists(filename):
        header = [['Year', 'Round', 'Num.', 'Drafted By', 
                  'Player', 'Pos', 'Drafted From',
                  'GP', 'G', 'A', 'Pts', 'PIM', 'Last Season']]
        write_to_csv(header, filename)
        print('Created {}'.format(filename))
    for link in links:
        try:
            html = get_data(link)
        except Exception as e:
            print('Can not access data on {}'.format(link),'\n', e)
            continue
        content = scrape_data(html)
        if content:
            write_to_csv(content, filename)
            print('{} data saved to csv.'.format(link))
        time.sleep(random.randint(1, 3))
    print('Done.')


if __name__ == '__main__':
    hockeydb_scrape_main()

