"""This script test functions in the extract.py file"""
from extract import create_dataframe


def test_create_dataframe_drops_columns():
    test_dict_list = [{"pdf": "foo", "filepath": "bar", "title": "foobar"}]
    df = create_dataframe(test_dict_list)
    assert df.columns.values[0] == "title"


def test_passing_for_workflow():
    """
    Passing test for workflow to run
    """

    pass
