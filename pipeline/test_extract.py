"""This script test functions in the extract.py file"""
from extract import create_dataframe, combine_case_url


def test_create_dataframe_drops_columns():
    test_dict_list = [{"pdf": "foo", "filepath": "bar", "title": "foobar"}]
    df = create_dataframe(test_dict_list)
    assert df.columns.values[0] == "title"


def test_create_dataframe_returns_correct_num_items():
    test_dict_list = [{"pdf": "foo", "filepath": "bar", "title": "foobar"}, {
        "pdf": "fizz", "filepath": "buzz", "title": "fizzbuzz"}]
    df = create_dataframe(test_dict_list)
    assert len(df) == 2


def test_passing_for_workflow():
    """
    Passing test for workflow to run
    """

    pass
