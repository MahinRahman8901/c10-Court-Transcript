"""Python script responsible for extracting court transcript data using web scraping"""

from os import makedirs, path, environ as ENV

from time import sleep
import logging
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup


def get_index_to_infinity():
    """Get index to infinity"""
    index = 1
    while True:
        yield index
        index += 1


def scrape_law_case_urls(web_url: str) -> list[str]:
    """Get the url for each case on the courts webpage"""
    try:
        response = requests.get(web_url, timeout=10)

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
    except requests.RequestException as error:
        logging.info(f"Error fetching URL: {error}")
        return []


def combine_case_url(url_list: list[str]) -> list[str]:
    """Return the combined url of case with url of webpage"""

    if url_list:
        case_urls = []

        for url in url_list:
            full_case_link = f"{ENV['BASE_URL']}/{url}"
            case_urls.append(full_case_link)
        return case_urls
    logging.info("No case law items found.")
    return []


def get_case_pdf_url(web_url: str) -> str:
    """Return the url for downloading the pdf transcript of a case"""
    try:
        response = requests.get(web_url, timeout=10)

        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        pdf_container = soup.find(
            'div', class_='judgment-toolbar__buttons judgment-toolbar-buttons')

        pdf_url_anchor = pdf_container.find(
            'a', class_='judgment-toolbar-buttons__option--pdf btn')

        pdf_url = pdf_url_anchor['href']

        return pdf_url
    except requests.RequestException as error:
        logging.info(f"Error fetching URL: {error}")
        return ''


def get_case_title(web_url: str) -> str:
    """Return the title of an accessed case"""
    try:
        response = requests.get(web_url, timeout=10)

        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        title_container = soup.find(
            'h1', class_='judgment-toolbar__title')

        title = title_container.text

        return title
    except requests.RequestException as error:
        logging.info(f"Error fetching URL: {error}")
        return ''


def download_pdfs(url_data: list[dict]) -> None:
    if not path.exists(f"{ENV['STORAGE_FOLDER']}/"):
        makedirs(f"{ENV['STORAGE_FOLDER']}/")

    for pdf in url_data:
        response = requests.get(pdf["pdf"])
        with open(f"{ENV['STORAGE_FOLDER']}/{pdf['title']}.pdf", "wb") as f:
            f.write(response.content)


if __name__ == "__main__":

    load_dotenv()

    for i in get_index_to_infinity():
        query_extension = ENV['COMM_QUERY_EXTENSION'] + str(i)
        url = f"{ENV['BASE_URL']}/{query_extension}"

        case_url_list = scrape_law_case_urls(url)

        combined_urls = combine_case_url(case_url_list)

        extracted_cases = []

        for case_url in combined_urls:
            case_title = get_case_title(case_url)
            pdf_url = get_case_pdf_url(case_url)
            extracted_cases.append({"title": case_title, "pdf": pdf_url})
        sleep(1)
        print(extracted_cases)
        download_pdfs(extracted_cases)
        if i >= 1:
            break
