'''Flask API for displaying data from the database.'''

from os import environ as ENV

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from psycopg2 import OperationalError

from queries import get_db_connection, get_table, get_case_by_case_no, get_judge_by_id, filter_judges


app = Flask(__name__)


@app.route('/')
def home():
    """Render the home page"""
    return render_template('homepage.html')


@app.route('/cases', methods=['GET'])
def get_all_cases():
    """API that returns all the cases"""

    conn = get_db_connection(ENV)
    cases = get_table(conn, 'transcript')
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


@app.route('/judges', methods=['GET'])
def get_all_judges():
    """API that returns all the judges"""

    conn = get_db_connection(ENV)
    filters = request.args.to_dict()

    if filters:
        judge = filter_judges(conn, filters)

    else:
        judge = get_table(conn, 'judge')
    conn.close()

    if judge:
        return jsonify({'judges': judge}), 200
    else:
        return jsonify({'message': 'No judges found'}), 404


@app.route('/judges/<int:judge_id>', methods=['GET'])
def get_all_judges_by_id(judge_id):
    """API that returns all the judges by given id"""

    try:
        judge_id = int(judge_id)
    except ValueError:
        return jsonify({'error': 'Judge ID must be an integer value'}), 404

    conn = get_db_connection(ENV)
    judge = get_judge_by_id(conn, judge_id)
    conn.close()
    if judge:
        return jsonify({'judges': judge}), 200
    else:
        return jsonify({'message': f'Judge with judge_id {judge_id} not found'}), 404


@app.route('/judge_types', methods=['GET'])
def get_all_judge_Types():
    """API that returns all the judge_types"""

    conn = get_db_connection(ENV)
    circuits = get_table(conn, 'judge_type')
    conn.close()
    if circuits:
        return jsonify({'judge_type': circuits}), 200
    else:
        return jsonify({'message': 'No judge_type found'}), 404


if __name__ == "__main__":

    load_dotenv()

    app.run(debug=True, host="0.0.0.0", port=5000)

    try:
        CONN = get_db_connection()
    except OperationalError as e:
        print("Error while connecting to PostgreSQL", e)
