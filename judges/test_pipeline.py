"""This script tests functions in the pipeline.py file"""
import pytest

from pipeline import convert_date, extract_name_gender, transform_df, concat_dfs

"""
Testing convert_date
"""


@pytest.mark.parametrize("input_date, expected_date", [("12-03-2024", "2024-03-12"),
                                                       ("12-03-24", "2024-03-12"),
                                                       ("12-Mar-24", "2024-03-12")])
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
                                                                          ("Their Honour Judge Foobar", "Honour Judge", "Foobar", "X")])
def test_extracting_name_gender_returns_correct_name_and_gender(judge, title, expected_name, expected_gender):
    name, gender = extract_name_gender(judge, title)
    assert name == expected_name
    assert gender == expected_gender


def test_extracting_name_gender_returns_correct_types():
    extraction = extract_name_gender(
        "His Honour Judge Fizz", "Honour Judge")
    assert len(extraction) == 2
    assert isinstance(extraction[0], str)
    assert isinstance(extraction[1], str)
    assert len(extraction[1]) == 1
