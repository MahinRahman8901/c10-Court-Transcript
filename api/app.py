'''Flask API for displaying data from the database.'''

from psycopg2 import OperationalError
from dotenv import load_dotenv
from flask import Flask, jsonify
from queries import get_db_connection, get_table, get_case_by_case_no
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


@app.route('/cases/<case_no>', methods=['GET'])
def get_case_by_case_number(case_no):
    """API that returns information about a specific case"""

    conn = get_db_connection(ENV)
    case = get_case_by_case_no(conn, case_no)
    conn.close()
    if case:
        return jsonify({'case': case}), 200
    else:
        return jsonify({'message': f'Case with case number {case_no} not found'}), 404


@app.route('/circuits', methods=['GET'])
def get_all_circuits():
    """API that returns all the circuits"""

    conn = get_db_connection(ENV)
    circuits = get_table(conn, 'circuit')
    conn.close()
    if circuits:
        return jsonify({'circuits': circuits}), 200
    else:
        return jsonify({'message': 'No circuits found'}), 404


if __name__ == "__main__":

    load_dotenv()

    app.run(debug=True, host="0.0.0.0", port=5000)

    try:
        CONN = get_db_connection()
    except OperationalError as e:
        print("Error while connecting to PostgreSQL", e)
