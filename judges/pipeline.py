"""Python script responsible for extracting judge data using web scraping"""

# from os import environ as ENV
# from time import sleep
# import logging
from datetime import datetime
# from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import pandas as pd


# ========== FUNCTIONS: SCRAPING ==========
def scrape_HCKB(url: str) -> pd.DataFrame:
    """Get data from a list of judges with a URL"""

    try:
        response = requests.get(url, timeout=10)

        soup = BeautifulSoup(response.content, 'html.parser')

        cells = soup.find_all(
            "td", class_="govuk-table__cell")
        cells = [cell.text
                 for cell in cells
                 if "<strong>" not in str(cell)]

        rows = []
        for c in range(0, len(cells), 2):
            rows.append({"judge": cells[c],
                         "appointment": cells[c+1]})

        return pd.DataFrame(rows)

    except requests.RequestException as error:
        logging.info(f"Error fetching URL: {error}")
        return pd.DataFrame([])


def scrape_CJ(url: str) -> pd.DataFrame:
    """Get data from a list of judges with a URL"""

    try:
        response = requests.get(url, timeout=10)

        soup = BeautifulSoup(response.content, 'html.parser')

        cells = soup.find_all(
            "td", class_="govuk-table__cell")
        cells = [cell.text
                 for cell in cells
                 if "strong" not in str(cell)]

        rows = []
        for c in range(0, len(cells), 3):
            rows.append({"judge": cells[c],
                         "circuit": cells[c+1],
                         "appointment": cells[c+2]})

        return pd.DataFrame(rows)

    except requests.RequestException as error:
        logging.info(f"Error fetching URL: {error}")
        return pd.DataFrame([])


# ========== FUNCTIONS: TRANSFORMING ==========
def convert_date(datestr: str) -> datetime:
    """Turns date string to datetime.
    Returns date as datetime."""

    datestr = datestr.split()[0]
    length = len(datestr)

    if length == 10:
        return datetime.strptime(datestr, "%d-%m-%Y")
    if length == 8:
        return datetime.strptime(datestr, "%d-%m-%y")
    if length == 9:
        return datetime.strptime(datestr, "%d-%b-%y")


def extract_name(judge: str, title: str) -> str:
    """Strips away any prefix and suffix.
    Returns a name."""

    if title in judge:
        prefix, name = judge.split(f" {title} ")
    else:
        for token in title.split():
            if token in judge:
                prefix, name = judge.split(f" {token} ")
                break

    if prefix in ["Her", "Mrs", "Ms", "Miss"]:
        gender = "F"
    elif prefix in ["His", "Mr"]:
        gender = "M"
    else:
        gender = "X"

    if "(" not in name:
        return name, gender

    name = name[:name.find("(")]

    return name, gender


def transform_HCKB(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and enriches the data.
    Returns transformed data as pd.DF."""

    df["appointment"] = df["appointment"].apply(convert_date)

    df["judge"] = df["judge"].apply(extract_name, args=("Justice",))
    df["name"] = df["judge"].str[0]
    df["gender"] = df["judge"].str[1]

    df["type"] = "High Court King’s Bench Division"

    df["circuit"] = ""

    df = df[["name", "gender", "appointment", "type", "circuit"]]

    return df


def transform_CJ(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and enriches the data.
    Returns transformed data as pd.DF."""

    df["appointment"] = df["appointment"].apply(convert_date)

    df["judge"] = df["judge"].apply(extract_name, args=("Honour Judge",))
    df["name"] = df["judge"].str[0]
    df["gender"] = df["judge"].str[1]

    df["type"] = "Circuit Judge"

    df = df[["name", "gender", "appointment", "type", "circuit"]]

    return df


def transform_df(df: pd.DataFrame,
                 title: str,
                 type: str,
                 circuit: str = "") -> pd.DataFrame:
    """Cleans and enriches the data.
    Returns transformed data as pd.DF."""

    df["appointment"] = df["appointment"].apply(convert_date)

    df["judge"] = df["judge"].apply(extract_name, args=(title,))
    df["name"] = df["judge"].str[0]
    df["gender"] = df["judge"].str[1]

    df["type"] = type

    if "circuit" not in df.columns:
        df["circuit"] = circuit

    df = df[["name", "gender", "appointment", "type", "circuit"]]

    return df


if __name__ == "__main__":

    # load_dotenv()

    HCKB = scrape_HCKB(
        "https://www.judiciary.uk/about-the-judiciary/who-are-the-judiciary/senior-judiciary-list/kings-bench-division-judges/")
    HCKB = transform_df(HCKB, "Justice", "High Court King’s Bench Division")

    CJ = scrape_CJ(
        "https://www.judiciary.uk/about-the-judiciary/who-are-the-judiciary/list-of-members-of-the-judiciary/circuit-judge-list/")
    CJ = transform_df(CJ, "Honour Judge", "Circuit Judge")
