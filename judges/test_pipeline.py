"""This script tests functions in the pipeline.py file"""
import pytest

import pandas as pd

from pipeline import convert_date, extract_name_gender, transform_df, concat_dfs, fuzzy_match_circuit

"""
Testing convert_date
"""


@pytest.mark.parametrize("input_date, expected_date", [("12-03-2024", "2024-03-12"),
                                                       ("12-03-24", "2024-03-12"),
                                                       ("12-Mar-24", "2024-03-12"),
                                                       ("07-May-23", "2023-05-07"),
                                                       ("29-Sep-09", "2009-09-29")])
def test_convert_date_returns_correct_format(input_date, expected_date):
    """Tests that the dates are returned in the correct format."""

    assert convert_date(input_date) == expected_date


def test_convert_date_returns_datetime():
    """Tests that a string is returned."""

    date = convert_date("12-03-2024")
    assert isinstance(date, str)


"""
Testing extracting_name_gender
"""


@pytest.mark.parametrize("judge, title, expected_name, expected_gender", [("His Honour Judge Foo", "Honour Judge", "Foo", "M"),
                                                                          ("Her Honour Judge Bar",
                                                                           "Honour Judge", "Bar", "F"),
                                                                          ("Their Honour Judge Foobar",
                                                                           "Honour Judge", "Foobar", "X"),
                                                                          ("Mr Justice Fizz",
                                                                           "Justice", "Fizz", "M"),
                                                                          ("Mrs Justice Buzz",
                                                                           "Justice", "Buzz", "F"),
                                                                          ("Miss Justice Fizzbuzz",
                                                                           "Justice", "Fizzbuzz", "F")
                                                                          ])
def test_extracting_name_gender_returns_correct_name_and_gender(judge, title, expected_name, expected_gender):
    """Tests the correct name and gender are returned."""

    name, gender = extract_name_gender(judge, title)
    assert name == expected_name
    assert gender == expected_gender


def test_extracting_name_gender_returns_correct_types():
    """Tests return types are correct."""

    extraction = extract_name_gender(
        "His Honour Judge Fizz", "Honour Judge")
    assert len(extraction) == 2
    assert isinstance(extraction[0], str)
    assert isinstance(extraction[1], str)
    assert len(extraction[1]) == 1


"""
Testing transform_df
"""


@pytest.mark.parametrize("name, date, title", [("His Honour Judge Fizz", "12-Mar-24", "Honour Judge"),
                                               ("Her Honour Judge Buzz",
                                                "12-03-24", "Honour Judge"),
                                               ("Mr Justice Foo",
                                                "12-09-2024", "Justice"),
                                               ("Their Honour Judge Bar",
                                                "10-Jun-24", "Honour Judge"),
                                               ("Miss Justice Foobar", "07-05-02", "Justice")])
def test_transform_df_returns_data_frame(name, date, title):
    """Tests a DataFrame is returned."""

    judge_data = [{"judge": name,
                  "appointment": date}]
    df = pd.DataFrame(judge_data)
    tdf = transform_df(df, title, "Circuit Judge")

    assert isinstance(tdf, pd.DataFrame)


@pytest.mark.parametrize("name, date, title", [("His Honour Judge Fizz", "12-Mar-24", "Honour Judge"),
                                               ("Her Honour Judge Bar",
                                                "12-03-24", "Honour Judge"),
                                               ("Mr Justice Foo",
                                                "12-09-2024", "Justice"),
                                               ("Their Honour Judge Bar",
                                                "10-Jun-24", "Honour Judge"),
                                               ("Miss Justice Foobar", "07-05-02", "Justice")])
def test_transform_df_contains_correct_columns(name, date, title):
    """Tests that all desired columns are present in the transformed DataFrame."""

    judge_data = [{"judge": name,
                  "appointment": date}]
    df = pd.DataFrame(judge_data)
    tdf = transform_df(df, title, "Circuit Judge")

    columns = ["name", "gender", "appointment", "type", "circuit"]

    assert all(col in columns for col in tdf.columns.values)


"""
Testing concat_df
"""


def test_concat_df_returns_data_frame():
    """Tests that a DataFrame is returned."""

    foo = pd.DataFrame([{"data": "foo"}])
    bar = pd.DataFrame([{"data": "bar"}])
    foobar = pd.DataFrame([{"data": "foobar"}])

    test = [foo, bar, foobar]

    assert isinstance(concat_dfs(test), pd.DataFrame)


def test_concat_df_contains_rows_for_all_input_dfs():
    """Tests the number of rows in the output DataFrame
       is equal to the number of DataFrames provided in the input."""

    foo = pd.DataFrame([{"data": "foo"}])
    bar = pd.DataFrame([{"data": "bar"}])
    foobar = pd.DataFrame([{"data": "foobar"}])

    test = [foo, bar, foobar]

    assert len(concat_dfs(test)) == len(test)


"""
Testing fuzzy_match_circuit
"""


def test_fuzzy_match_circuit_returns_string():
    test = pd.DataFrame([{"name": "foo"}, {"name": "bar"}, {
                        "name": "fizz"}, {"name": "buzz"}])
    assert isinstance(fuzzy_match_circuit("foo", test), str)


def test_fuzzy_match_circuit_returns_correct_match():
    test = pd.DataFrame([{"name": "foo"}, {"name": "bar"}, {
                        "name": "fizz"}, {"name": "buzz"}])

    assert fuzzy_match_circuit("football", test) == "foo"


def test_fuzzy_match_circuit_returns_na_on_poor_match():
    test = pd.DataFrame([{"name": "foo"}, {"name": "bar"}, {
                        "name": "fizz"}, {"name": "buzz"}])

    assert fuzzy_match_circuit("frog", test) == "N/A"
