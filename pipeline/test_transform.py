'''This script tests functions in the transform.py file.'''

import re
import pytest
from transform import is_correct_date_format, format_date, clean_date, strip_titles, standardize_case_no


'''
Tests for standardizing date format.
'''


def test_is_correct_date_format_returns_bool():
    '''Checks the function returns a bool.'''
    result = is_correct_date_format('sdfgh')
    assert isinstance(result, bool)


def test_correct_date_format_returns_true():
    '''Checks the function returns true for a date of the right format.'''
    assert is_correct_date_format('06/03/2002') is True


def test_incorrect_date_format_returns_false():
    '''Checks the function returns false for a date incorrectly formatted.'''
    assert is_correct_date_format('06 March 2002') is False


'''
Parameterized tests for is_correct_date_format.
'''


@pytest.mark.parametrize("test_input, expected", [("22/04/2024", True),
                                                  ("23 April 2024", False),
                                                  ("11/04/2024", True),
                                                  ("Friday, 22 March 2024", False),
                                                  ("SDFGHJKJHGFC", False),
                                                  ("Date : 8 March 2024", False),
                                                  ("1 March 2024", False),
                                                  ("1/03/2024", False)])
def test_is_correct_date_format(test_input, expected):
    assert is_correct_date_format(test_input) == expected


'''
Parameterized tests for format_date.
'''


@pytest.mark.parametrize("input_date, split_on, expected", [("23 April 2024", " ", "23/04/2024"),
                                                            ("1 March 2024",
                                                             " ", "01/03/2024"),
                                                            ("1/03/2024", "/", "01/03/2024")])
def test_format_date(input_date, split_on, expected):
    assert format_date(input_date, split_on) == expected


'''
Parameterized tests for clean_date.
'''


@pytest.mark.parametrize("input_date, expected", [("23 April 2024", "23/04/2024"),
                                                  ("Friday, 22 March 2024",
                                                   "22/03/2024"),
                                                  ("Date : 8 March 2024",
                                                   "08/03/2024"),
                                                  ("SDFGHJKJHGFC", None),
                                                  ("1 March 2024", "01/03/2024"),
                                                  ("1/03/2024", "01/03/2024")])
def test_format_date(input_date, expected):
    assert clean_date(input_date) == expected


'''
Parameterized tests for strip_titles.
'''


@pytest.mark.parametrize("input_name, stripped_name", [("MRS JUSTICE DIAS DBE", "DIAS"),
                                                       ("MR JUSTICE FOXTON",
                                                        "FOXTON"),
                                                       ("HIS HONOUR JUDGE PEARCE",
                                                        "PEARCE"),
                                                       ("THE HONOURABLE MR JUSTICE HENSHAW",
                                                        "HENSHAW"),
                                                       ("SIR NIGEL TEARE",
                                                        "NIGEL TEARE"),
                                                       ("DAME CLARE MOULDER DBE", "CLARE MOULDER")])
def test_strip_titles(input_name, stripped_name):
    assert strip_titles(input_name) == stripped_name


'''
Parameterized tests for standardize_case_no.
'''


@pytest.mark.parametrize("input, case_no", [("CL -2023- 000873", "CL-2023-000873"),
                                            ("LM- 2022- 000232", "LM-2022-000232"),
                                            ("CL -2023- 000284 & CL-2023 -000873",
                                             "CL-2023-000284 & CL-2023-000873"),
                                            ("CL-2023-000284&CL-2023-000873 & CL-2023-000132", "CL-2023-000284 & CL-2023-000873 & CL-2023-000132")])
def test_standardize_case_no(input, case_no):
    assert standardize_case_no(input) == case_no
