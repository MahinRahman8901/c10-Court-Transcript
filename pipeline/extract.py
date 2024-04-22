import requests
from bs4 import BeautifulSoup

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

        case_law_container = soup.find('div', class_='results__result-list-container')
        
        case_law_urls = case_law_container.find('ul', class_='judgment-listing__list')

        if case_law_urls:
            case_law_items = case_law_urls.find_all('a')

            case_urls = []
            for link in case_law_items:
                case_urls.append(link['href'])

        return case_urls
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []
    
def combine_case_url(url_list: list[str]) -> list[str]:
    """Return the combined url of case with url of webpage"""

    if url_list:
        case_urls = []
        
        for url in url_list:
            full_case_link = f"https://caselaw.nationalarchives.gov.uk{url}"
            case_urls.append(full_case_link)
        return case_urls
    else:
        print("No case law items found.")
        return []
    
# def scrape_


if __name__ == "__main__":

    for i in get_index_to_infinity():
        query_extension = f"?query=&order=&page={i}"
        url = "https://caselaw.nationalarchives.gov.uk/judgments/search"

        case_urls = scrape_law_case_urls(url)

        combined_urls = combine_case_url(case_urls)
        if i > 5:
            break

"""This script is responsible for extracting court transcript data"""

if __name__ == "__main__":
    pass