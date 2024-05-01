"""Python script responsible for extracting judge data using web scraping"""

from rapidfuzz.process import extractOne
from rapidfuzz.fuzz import partial_ratio
from psycopg2.extras import RealDictCursor
from psycopg2 import connect, sql
from os import environ as ENV
import logging
from datetime import datetime
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import pandas as pd


# ========== GLOBALS ==========
KINGS_BENCH_URL = "https://www.judiciary.uk/about-the-judiciary/who-are-the-judiciary/senior-judiciary-list/kings-bench-division-judges/"
CIRCUIT_URL = "https://www.judiciary.uk/about-the-judiciary/who-are-the-judiciary/list-of-members-of-the-judiciary/circuit-judge-list/"


# ========== FUNCTIONS: SCRAPING ==========
def scrape_kings_bench(url: str) -> pd.DataFrame:
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
        return datetime.strptime(datestr, "%d-%m-%Y").strftime("%Y-%m-%d")
    if length == 8:
        return datetime.strptime(datestr, "%d-%m-%y").strftime("%Y-%m-%d")
    if length == 9:
        return datetime.strptime(datestr, "%d-%b-%y").strftime("%Y-%m-%d")


def extract_name_gender(judge: str, title: str) -> str:
    """Strips away any prefix and suffix.
    Returns a name."""

    if title in judge:
        prefix, name = [part.strip() for part in judge.split(f" {title} ")]
    else:
        for token in title.split():
            if token in judge:
                prefix, name = judge.split(f" {token} ")
                break

    if prefix in ["Her", "Mrs", "Ms", "Miss"]:
        gender = "F"
    elif prefix in ["His", "Mr"]:
        gender = "M"
    elif prefix in ["Their"]:
        gender = "X"
    else:
        gender = None

    if "(" not in name:
        return name.strip(), gender

    name = name[:name.find("(")]

    return name.strip(), gender


def transform_df(df: pd.DataFrame,
                 title: str,
                 type: str,
                 circuit: str = "N/A") -> pd.DataFrame:
    """Cleans and enriches the data.
    Returns transformed data as pd.DF."""

    df["appointment"] = df["appointment"].apply(convert_date)

    df["judge"] = df["judge"].apply(extract_name_gender, args=(title,))
    df["name"] = df["judge"].str[0]
    df["gender"] = df["judge"].str[1]

    df["type"] = type

    if "circuit" not in df.columns:
        df["circuit"] = circuit

    df = df[["name", "gender", "appointment", "type", "circuit"]]

    return df


def concat_dfs(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    """Concatenates pd.DFs.
    Returns one single pd.DF"""

    return pd.concat(dfs, ignore_index=True)


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


def fuzzy_match_circuit(circuit: str, circuit_df: pd.DataFrame) -> int:
    """Returns corresponding circuit ids by fuzzy matching circuit strings."""

    circuits = circuit_df["name"]

    circuit_id = extractOne(circuit, circuits,
                            scorer=partial_ratio,
                            score_cutoff=90)

    if circuit_id == None:
        return "N/A"

    return circuit_id[0]


def fill_ids(judges: pd.DataFrame,
             types: pd.DataFrame,
             circuits: pd.DataFrame,
             stored_judges: pd.DataFrame) -> list[dict]:
    """Converts judge type and circuit strings to corresponding ids in db.
    Checks if judge currently exists in db, removes from list if so.
    Returns transformed judge data as pd.DF."""

    judges = judges.join(types.set_index("type_name"), "type", "left"
                         ).drop(columns="type")

    judges["circuit"] = judges["circuit"].apply(
        fuzzy_match_circuit, args=(circuits,))
    judges = judges.join(circuits.set_index("name"), "circuit", "left"
                         ).drop(columns="circuit")

    columns = list(zip(judges['name'], judges['gender'], judges['appointment'],
                       judges['judge_type_id'], judges['circuit_id']))

    already_stored = []
    i = 0
    for i in range(0, len(columns)):
        if (columns[i][0] in stored_judges["name"].values) and (columns[i][2] in [str(date) for date in stored_judges["appointed"].values]):
            already_stored.append(columns[i])
        else:
            i += 1
    return [new_judge for new_judge in columns if new_judge not in already_stored]


def upload_data(conn: connect, records: list[tuple]) -> None:
    """Insert judge data into judge table in db."""

    with conn.cursor() as cur:
        query = """
                INSERT INTO judge
                    (name, gender, appointed, judge_type_id, circuit_id)
                VALUES
                    (%s, %s, %s, %s, %s)
                """
        cur.executemany(query, records)
    conn.commit()


# ========== MAIN ==========
def main():
    """Encapsulates all functions to run in main."""

    logger = logging.getLogger(__name__)
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    load_dotenv()
    conn = get_db_connection(ENV)

    logger.info("=========== SCRAPING ==========")

    logger.info("===== scraping HCKB... =====")

    kings_bench = scrape_kings_bench(KINGS_BENCH_URL)

    logger.info("===== scraping CJ... =====")
    circuit_judges = scrape_circuit_judges(CIRCUIT_URL)

    logger.info("=========== TRANSFORMING ==========")

    logger.info("===== transforming HCKB... =====")

    kings_bench = transform_df(
        kings_bench, "Justice", "High Court King’s Bench Division")

    logger.info("===== transforming CJ... =====")
    circuit_judges = transform_df(
        circuit_judges, "Honour Judge", "Circuit Judge")

    logger.info("===== concatenating DFs... =====")
    judges = concat_dfs([kings_bench, circuit_judges])

    logger.info("=========== LOADING ==========")
    judge_types = get_db_table(conn, "judge_type")
    circuits = get_db_table(conn, "circuit")
    stored_judges = get_db_table(conn, "judge")
    judges = fill_ids(judges, judge_types, circuits, stored_judges)

    if judges:
        logger.info("===== uploading to database... =====")
        upload_data(conn, judges)
    else:
        logger.info("===== no new judges... =====")


def handler(event, context):
    """Pass the main function to a handler to be run by Lambda on AWS"""

    main()


if __name__ == "__main__":
    main()
