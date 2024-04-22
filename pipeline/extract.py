"""Python script responsible for extracting court transcript data using web scraping"""

from os import environ as ENV

from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
import logging
from time import sleep

# TODO: work on just one court for now - pass in filter variable for grabbing urls
# TODO: use gpt to get verdict in one word
# TODO: parse the pdf of each case rather than the html


def get_index_to_infinity():
    """Get index to infinity"""
    index = 0
    while True:
        yield index
        index += 1


def scrape_law_case_urls(url: str) -> list[str]:
    """Get the url for each case on the courts webpage"""
    try:
        response = requests.get(url)

        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        case_law_container = soup.find(
            'div', class_='results__result-list-container')

        case_law_urls = case_law_container.find(
            'ul', class_='judgment-listing__list')

        if case_law_urls:
            case_law_items = case_law_urls.find_all('a')

            case_urls = []
            for link in case_law_items:
                case_urls.append(link['href'])

        return case_urls
    except requests.RequestException as e:
        logging.info(f"Error fetching URL: {e}")
        return []


def combine_case_url(url_list: list[str]) -> list[str]:
    """Return the combined url of case with url of webpage"""

    if url_list:
        case_urls = []

        for url in url_list:
            full_case_link = f"{ENV['BASE_URL']}/{url}"
            case_urls.append(full_case_link)
        return case_urls
    else:
        logging.info("No case law items found.")
        return []


def get_case_pdf_url(case_url: str) -> str:
    """Return the url for downloading the pdf transcript of a case"""
    ...


if __name__ == "__main__":

    load_dotenv()

    for i in get_index_to_infinity():
        query_extension = ENV['COMM_QUERY_EXTENSION'] + str(i)
        url = f"{ENV['BASE_URL']}/{query_extension}"

        case_urls = scrape_law_case_urls(url)

        combined_urls = combine_case_url(case_urls)
        print(combined_urls)
        sleep(1)
        if i >= 2:
            break
