"""This script test functions in the extract.py file"""
from os import environ as ENV

from extract import create_dataframe, combine_case_url, get_index_to_infinity

"""
Testing create_dataframe
"""


def test_create_dataframe_drops_columns():
    test_dict_list = [{"pdf": "foo", "filepath": "bar", "title": "foobar"}]
    df = create_dataframe(test_dict_list)
    assert df.columns.values[0] == "title"


def test_create_dataframe_returns_correct_num_items():
    test_dict_list = [{"pdf": "foo", "filepath": "bar", "title": "foobar"}, {
        "pdf": "fizz", "filepath": "buzz", "title": "fizzbuzz"}]
    df = create_dataframe(test_dict_list)
    assert len(df) == 2


"""
Testing combine_case_url
"""


def test_combine_case_url_returns_list():
    ENV['BASE_URL'] = "real.url"
    urls = ["fizz", "buzz", "foo", "bar"]
    case_urls = combine_case_url(urls)
    assert isinstance(case_urls, list)


def test_combine_case_url_returns_correct_url():
    ENV['BASE_URL'] = "real.url"
    urls = ["fizz"]
    case_urls = combine_case_url(urls)
    assert case_urls[0] == "real.url/fizz"


"""
Testing get_index_to_infinity
"""


def test_get_index_to_infinity():
    indexes = get_index_to_infinity()
    first = next(indexes)
    second = next(indexes)
    assert first == 1
    assert second == 2
