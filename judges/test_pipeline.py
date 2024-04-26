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
