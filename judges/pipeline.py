"""Python script responsible for extracting judge data using web scraping"""

from os import environ as ENV
import logging
from datetime import datetime
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import pandas as pd
from psycopg2 import connect
from psycopg2.extras import RealDictCursor


# ========== GLOBALS ==========
HCKB_URL = "https://www.judiciary.uk/about-the-judiciary/who-are-the-judiciary/senior-judiciary-list/kings-bench-division-judges/"
CJ_URL = "https://www.judiciary.uk/about-the-judiciary/who-are-the-judiciary/list-of-members-of-the-judiciary/circuit-judge-list/"


# ========== FUNCTIONS: SCRAPING ==========
def scrape_high_court_kings_bench(url: str) -> pd.DataFrame:
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


def scrape_circuit_judges(url: str) -> pd.DataFrame:
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
        return name.strip(), gender

    name = name[:name.find("(")]

    return name.strip(), gender


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


def concat_dfs(dfs: list[pd.DataFrame]) -> pd.DateOffset:
    """Concatenates pd.DFs.
    Returns one single pd.DF"""

    return pd.concat(dfs, ignore_index=True).to


# ========== FUNCTIONS: DATABASE ==========
# def get_db_connection(config) -> connect:
#     """Returns db connection."""

#     return connect(dbname=config["DB_NAME"],
#                    user=config["DB_USER"],
#                    password=config["DB_PASSWORD"],
#                    host=config["DB_HOST"],
#                    port=config["DB_PORT"],
#                    cursor_factory=RealDictCursor)


# def upload_data(conn: connect, df: pd.DataFrame) -> None:
#     """Insert judge data into judge table in db."""

#     with conn.cursor() as cur:
#         query = """
#                 INSERT INTO judges
#                     (name, gender, appointed, judge_type_id, circuit_id)
#                 VALUES
#                     (%s, %s, %s)
#                 """
#         cur.executemany(query,
#                         [df["at"], df["site"], df["val"]])
#     conn.commit()


# ========== MAIN ==========
def main():
    """Encapsulates all functions to run in main."""

    logger = logging.getLogger(__name__)
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    load_dotenv()
    # conn = get_db_connection(ENV)

    logger.info("=========== SCRAPING ==========")

    logger.info("===== scraping HCKB... =====")
    HCKB = scrape_high_court_kings_bench(HCKB_URL)

    logger.info("===== scraping CJ... =====")
    CJ = scrape_circuit_judges(CJ_URL)

    logger.info("=========== TRANSFORMING ==========")

    logger.info("===== transforming HCKB... =====")
    HCKB = transform_df(HCKB, "Justice", "High Court King’s Bench Division")

    logger.info("===== transforming CJ... =====")
    CJ = transform_df(CJ, "Honour Judge", "Circuit Judge")

    logger.info("===== concatenating DFs... =====")
    judges = concat_dfs([HCKB, CJ])

    logger.info("=========== LOADING ==========")


if __name__ == "__main__":
    main()
