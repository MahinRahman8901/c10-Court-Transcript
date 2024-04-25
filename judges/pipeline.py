"""Python script responsible for extracting judge data using web scraping"""

from os import environ as ENV
import logging
from datetime import datetime
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import pandas as pd
from psycopg2 import connect, sql
from psycopg2.extras import RealDictCursor


# ========== GLOBALS ==========
<< << << < HEAD
HCKB_URL = "https://www.judiciary.uk/about-the-judiciary/who-are-the-judiciary/senior-judiciary-list/kings-bench-division-judges/"
CJ_URL = "https://www.judiciary.uk/about-the-judiciary/who-are-the-judiciary/list-of-members-of-the-judiciary/circuit-judge-list/"


# ========== FUNCTIONS: SCRAPING ==========
def scrape_high_court_kings_bench(url: str) -> pd.DataFrame:


== == == =
KINGS_BENCH_URL = "https://www.judiciary.uk/about-the-judiciary/who-are-the-judiciary/senior-judiciary-list/kings-bench-division-judges/"
CIRCUIT_URL = "https://www.judiciary.uk/about-the-judiciary/who-are-the-judiciary/list-of-members-of-the-judiciary/circuit-judge-list/"


# ========== FUNCTIONS: SCRAPING ==========
def scrape_kings_bench(url: str) -> pd.DataFrame:


>>>>>> > 28a01187c6fcec5ad8a470263efd9338062324a5
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


<< <<<< < HEAD
def scrape_circuit_judge(url: str) -> pd.DataFrame:
== == ===
def scrape_circuit_judges(url: str) -> pd.DataFrame:

>>>>>> > 28a01187c6fcec5ad8a470263efd9338062324a5
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
    """Strips away any prefix and suffix; extracts gender from prefix.
    Returns a name and a gender."""

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


def concat_dfs(dfs: list[pd.DataFrame]) -> list:
    """Concatenates pd.DFs.
    Returns one single pd.DF"""

    return pd.concat(dfs, ignore_index=True).to_records(index=False)


# ========== FUNCTIONS: DATABASE ==========
def get_db_connection(config) -> connect:
    """Returns db connection."""

    return connect(dbname=config["DB_NAME"],
                   user=config["DB_USER"],
                   password=config["DB_PASSWORD"],
                   host=config["DB_HOST"],
                   port=config["DB_PORT"],
                   cursor_factory=RealDictCursor)


def get_db_table(conn: connect, table: str) -> pd.DataFrame:
    """Returns table 'circuit' from database as pd.DF."""

    with conn.cursor() as cur:
        query = sql.SQL(
            """SELECT * FROM {};""").format(sql.Identifier(table))
        cur.execute(query)
        rows = cur.fetchall()

    return pd.DataFrame(rows)


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

<<<<<< < HEAD
  """Encapsulating the functions to run in main."""
== == ===
  """Encapsulates all functions to run in main."""
>>>>>> > 28a01187c6fcec5ad8a470263efd9338062324a5

  logger = logging.getLogger(__name__)
   logging.basicConfig(encoding='utf-8', level=logging.INFO)

    load_dotenv()
    conn = get_db_connection(ENV)

    logger.info("=========== SCRAPING ==========")

    logger.info("===== scraping HCKB... =====")
<< <<<< < HEAD
  HCKB = scrape_high_court_kings_bench(HCKB_URL)

   logger.info("===== scraping CJ... =====")
    CJ = scrape_circuit_judge(CJ_URL)
== == ===
  kings_bench = scrape_kings_bench(KINGS_BENCH_URL)

   logger.info("===== scraping CJ... =====")
    circuit_judges = scrape_circuit_judges(CIRCUIT_URL)
>>>>>> > 28a01187c6fcec5ad8a470263efd9338062324a5

  logger.info("=========== TRANSFORMING ==========")

   logger.info("===== transforming HCKB... =====")
<< <<<< < HEAD
  HCKB = transform_df(HCKB, "Justice", "High Court King’s Bench Division")

   logger.info("===== transforming CJ... =====")
    CJ = transform_df(CJ, "Honour Judge", "Circuit Judge")

    logger.info("===== concatenating DFs... =====")
    judges = concat_dfs([HCKB, CJ])
== == ===
  kings_bench = transform_df(
       kings_bench, "Justice", "High Court King’s Bench Division")

   logger.info("===== transforming CJ... =====")
    circuit_judges = transform_df(
        circuit_judges, "Honour Judge", "Circuit Judge")

    logger.info("===== concatenating DFs... =====")
    judges = concat_dfs([kings_bench, circuit_judges])
>>>>>> > 28a01187c6fcec5ad8a470263efd9338062324a5

  logger.info("=========== LOADING ==========")
   circuit = get_db_table(conn, "circuit")
    judge_type = get_db_table(conn, "judge_type")
    print(judge_type)


if __name__ == "__main__":
    main()
