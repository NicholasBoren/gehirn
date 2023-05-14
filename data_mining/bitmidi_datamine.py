from bs4 import BeautifulSoup
import cloudscraper
import re
from time import sleep
import os
import requests
import urllib.request

scraper = cloudscraper.create_scraper()
session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.110 Safari/537.36'
}

BASE_URL = 'https://bitmidi.com'

def download_page(url, folder_path):
    file_name = url.split('/')[-3] + '.mid'
    midi_download_path = '/'.join(url.split('/')[-2:])
    url = BASE_URL + '/' + midi_download_path

    print('Downloading', url)
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'wb') as f:
        f.write(response.read())



def get_page_data(url, folder_path):
    response = scraper.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    midi_links = soup.find_all('a', {'class': 'pointer no-underline fw4 white underline-hover'})
    if not midi_links:
        return

    for midi_link in midi_links:
        midi_page = midi_link['href']
        midi_response = scraper.get(BASE_URL + midi_page)
        midi_soup = BeautifulSoup(midi_response.content, 'html.parser')
        for link in midi_soup.find_all('a'):
            href = link.get('href')
            if href and href.endswith('.mid'):
                midi_url = BASE_URL + midi_page + href
                download_page(midi_url, folder_path)

        sleep(1)


def get_bitmidi_data(starting_url='https://bitmidi.com', base_folder_path='../data/bitmidi'):
    page_pattern = re.compile(r'\?page=\d+')
    page_match = re.search(page_pattern, starting_url)
    base_url = starting_url
    page_number = 0
    folder_path = base_folder_path + '/page' + str(page_number)
    if page_match:
        page_number = page_match.group(0).split('=')[1]
        base_url = starting_url.split(page_pattern.search(starting_url).group(0))[0]

    while True:
        print('Currently on page', page_number)
        print('-' * 20)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        url = f'{base_url}/?page={page_number}'
        if page_number == 0:
            get_page_data(base_url, folder_path)

        get_page_data(url, folder_path)
        page_number = str(int(page_number) + 1)
        folder_path = base_folder_path + '/page' + str(page_number)


if __name__ == '__main__':
    get_bitmidi_data(starting_url='https://bitmidi.com?page=1')
    #get_bitmidi_data()
