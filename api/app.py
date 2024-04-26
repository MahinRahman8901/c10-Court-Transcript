'''Flask API for displaying data from the database.'''

from psycopg2 import OperationalError
from dotenv import load_dotenv
from flask import Flask
from queries import get_db_connection

app = Flask(__name__)


if __name__ == "__main__":

    load_dotenv()

    app.run(debug=True, host="0.0.0.0", port=5000)

    try:
        CONN = get_db_connection()
    except OperationalError as e:
        print("Error while connecting to PostgreSQL", e)
