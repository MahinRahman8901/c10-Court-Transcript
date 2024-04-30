"""Python script responsible for extracting court transcript data using web scraping."""

from os import makedirs, path, environ as ENV
import re

from time import sleep
import logging
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
import pandas as pd
from pypdf import PdfReader
from psycopg2 import connect
from psycopg2.extras import RealDictCursor


def get_db_connection() -> connect:
    """Returns db connection."""

    return connect(dbname=ENV["DB_NAME"],
                   user=ENV["DB_USER"],
                   password=ENV["DB_PASSWORD"],
                   host=ENV["DB_HOST"],
                   port=ENV["DB_PORT"],
                   cursor_factory=RealDictCursor)


def get_stored_titles(conn) -> list:
    """Returns the list of titles stored in the database"""

    with conn.cursor() as cur:
        cur.execute("SELECT title FROM transcript;")
        result = cur.fetchall()

    return [row["title"] for row in result]


def get_index_to_infinity():
    """Get index to infinity."""

    index = 1
    while True:
        yield index
        index += 1


def scrape_law_case_urls(web_url: str) -> list[str]:
    """Get the url for each case on the courts webpage."""

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
    """Return the combined url of case with url of webpage."""

    if url_list:
        case_urls = []

        for url in url_list:
            full_case_link = f"{ENV['BASE_URL']}/{url}"
            case_urls.append(full_case_link)
        return case_urls
    logging.info("No case law items found.")
    return []


def get_case_soup(web_url: str) -> BeautifulSoup:
    """Returns the soup of a webpage."""

    try:
        response = requests.get(web_url, timeout=10)

        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        return soup
    except requests.RequestException as error:
        logging.info(f"Error fetching URL: {error}")


def get_case_pdf_url(case_soup: BeautifulSoup) -> str:
    """Return the url for downloading the pdf transcript of a case."""

    pdf_container = case_soup.find(
        'div', class_='judgment-toolbar__buttons judgment-toolbar-buttons')

    pdf_url_anchor = pdf_container.find(
        'a', class_='judgment-toolbar-buttons__option--pdf btn')

    pdf_url = pdf_url_anchor['href']

    return pdf_url


def get_case_title(case_soup: BeautifulSoup) -> str:
    """Return the title of an accessed case."""

    title_container = case_soup.find(
        'h1', class_='judgment-toolbar__title')

    title = title_container.text

    return title.replace("/", "-")


def download_pdfs(court_case: dict) -> None:
    """Downloads a pdf from the link given in the court_case dict."""

    if not path.exists(f"{ENV['STORAGE_FOLDER']}"):
        makedirs(f"{ENV['STORAGE_FOLDER']}")

    court_case["filepath"] = f"{ENV['STORAGE_FOLDER']}/{court_case['title']}.pdf"

    try:
        response = requests.get(court_case["pdf"], timeout=10)
        with open(f"{court_case['filepath']}", "wb") as f:
            f.write(response.content)
        return
    except (requests.exceptions.MissingSchema, requests.exceptions.ReadTimeout):
        pass

    try:
        response = requests.get(
            f"{ENV['BASE_URL']}{court_case['pdf']}", timeout=10)
        with open(f"{court_case['filepath']}", "wb") as f:
            f.write(response.content)
    except (requests.exceptions.MissingSchema, requests.exceptions.ReadTimeout):
        court_case.clear()


def parse_pdf(court_case: dict):
    """Extracts judge name, case number, date, introduction, and conclusion from pdf."""

    reader = PdfReader(court_case['filepath'])
    first_page = reader.pages[0].extract_text().lower()
    second_page = reader.pages[1].extract_text()
    last_page = reader.pages[-1].extract_text()

    try:
        judge = re.search(r"(?<=Before :\n)([A-Z a-z]*)", first_page)
        if not judge:
            judge = re.search(r"(?<=Before  : \n \n)([A-Z a-z]*)", first_page)
        if not judge:
            judge = re.search(r"(?<=Before : \n \n)([A-Z a-z]*)", first_page)
        if not judge:
            judge = re.search(r"(?<=Before:\n)([A-Z a-z]*)", first_page)
        if not judge:
            judge = re.search(r"(?<=BEFORE:\n)([A-Z a-z]*)", first_page)
        if not judge:
            judge = re.search(r"(THE HONOURABLE [A-Z a-z]*)", first_page)
        court_case["judge_name"] = judge.group(1).strip()

        case_no = re.search(
            r"([A-Z]{2} ?- ?[0-9]{4} ?- ?[0-9]{6})", first_page)
        court_case["case_no"] = case_no.group(1).strip()

        court_date = re.search(
            r"(?<=Date: )(.*)", first_page)
        if not court_date:
            court_date = re.search(
                r"(?<=Date : )(.*)", first_page)
        if not court_date:
            court_date = re.search(
                r"([\w]{0,},? ?[0-9]{1,2} [A-Z|a-z]+ [0-9]{2,4})|([0-9]{2}[/][0-9]{2}[/][0-9]{2,4})", first_page)
        court_case["date"] = court_date.group(1).strip()

        court_case["introduction"] = second_page

        court_case["conclusion"] = last_page

    except:
        court_case.clear()


def create_dataframe(court_cases: list[dict]) -> pd.DataFrame:
    """Given a list of court cases, creates and returns a pandas dataframe."""

    cases = pd.DataFrame(court_cases)
    cases = cases.drop(columns=["pdf", "filepath"])

    return cases


def extract_cases(end_page: int, start_page: int = 1, ) -> pd.DataFrame:
    """Given a range of pages (default from 1 - end_page), 
    will return a DataFrame of all the cases from these pages."""

    load_dotenv()

    conn = get_db_connection()

    stored_titles = get_stored_titles(conn)

    extracted_cases = []

    for i in range(start_page, end_page+1):
        query_extension = ENV['COMM_QUERY_EXTENSION'] + str(i)
        url = f"{ENV['BASE_URL']}/{query_extension}"

        case_url_list = scrape_law_case_urls(url)

        combined_urls = combine_case_url(case_url_list)

        for case_url in combined_urls:
            case_soup = get_case_soup(case_url)
            if case_soup:
                case_title = get_case_title(case_soup)
                if case_title not in stored_titles:
                    pdf_url = get_case_pdf_url(case_soup)
                    extracted_cases.append(
                        {"title": case_title, "pdf": pdf_url})
                    stored_titles.append(case_title)

        sleep(1)

    for case_data in extracted_cases:
        download_pdfs(case_data)
        if case_data:
            parse_pdf(case_data)

    extracted_cases = list(filter(None, extracted_cases))

    if extracted_cases:
        df = create_dataframe(extracted_cases)
        return df

    logging.info("No new cases found.")
    return pd.DataFrame()


if __name__ == "__main__":

    df = extract_cases(1)
    if not df.empty:
        print(df[["title", "case_no", "date"]])
    else:
        print("empty")
