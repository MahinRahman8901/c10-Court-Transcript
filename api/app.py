'''Flask API for displaying data from the database.'''

from psycopg2 import OperationalError
from dotenv import load_dotenv
from flask import Flask, jsonify
from queries import get_db_connection, get_table
from os import environ as ENV

app = Flask(__name__)


@app.route('/cases', methods=['GET'])
def get_all_cases():
    """API that returns all the cases"""

    conn = get_db_connection(ENV)
    cases = get_table(conn, 'court_case')
    conn.close()
    if cases:
        return jsonify({'cases': cases}), 200
    else:
        return jsonify({'message': 'No cases found'}), 404


if __name__ == "__main__":

    load_dotenv()

    app.run(debug=True, host="0.0.0.0", port=5000)

    try:
        CONN = get_db_connection()
    except OperationalError as e:
        print("Error while connecting to PostgreSQL", e)
