"""This script test functions in the extract.py file"""
from os import environ as ENV

from bs4 import BeautifulSoup

from extract import create_dataframe, combine_case_url, get_index_to_infinity, get_case_pdf_url, get_case_title

"""
Testing create_dataframe
"""


def test_create_dataframe_drops_columns():
    """Tests that the correct columns get dropped."""

    test_dict_list = [{"pdf": "foo", "filepath": "bar", "title": "foobar"}]
    df = create_dataframe(test_dict_list)
    assert df.columns.values[0] == "title"


def test_create_dataframe_returns_correct_num_items():
    """Tests that it returns the same amount of items you pass in."""

    test_dict_list = [{"pdf": "foo", "filepath": "bar", "title": "foobar"}, {
        "pdf": "fizz", "filepath": "buzz", "title": "fizzbuzz"}]
    df = create_dataframe(test_dict_list)
    assert len(df) == len(test_dict_list)


"""
Testing combine_case_url
"""


def test_combine_case_url_returns_list():
    """Tests that a list is returned."""

    ENV['BASE_URL'] = "real.url"
    urls = ["fizz", "buzz", "foo", "bar"]
    case_urls = combine_case_url(urls)
    assert isinstance(case_urls, list)


def test_combine_case_url_returns_correct_url():
    """Tests that the correct url is formed."""

    ENV['BASE_URL'] = "real.url"
    urls = ["fizz"]
    case_urls = combine_case_url(urls)
    assert case_urls[0] == "real.url/fizz"


"""
Testing get_index_to_infinity
"""


def test_get_index_to_infinity():
    """Tests that the generator function yields incrementally by 1."""

    indexes = get_index_to_infinity()
    first = next(indexes)
    second = next(indexes)
    assert first == 1
    assert second == 2


"""
Testing get_case_pdf_url
"""


def test_get_case_pdf_url_returns_string():
    """Tests that a string is returned."""

    html_string = """
                    <div class="judgment-toolbar__buttons judgment-toolbar-buttons"> == $0
                        <a class="judgment-toolbar-buttons__option--pdf btn" href= "url"> == $0
                        </a>
                    </div>
                """
    fake_soup = BeautifulSoup(html_string, "html.parser")
    url = get_case_pdf_url(fake_soup)
    assert isinstance(url, str)


def test_get_case_pdf_url_returns_correct_element():
    """Tests that the correct part of the html is returned."""

    html_string = """
                    <div class="judgment-toolbar__buttons judgment-toolbar-buttons"> == $0
                        <a class="judgment-toolbar-buttons__option--pdf btn" href= "foobar"> == $0
                        </a>
                    </div>
                """
    fake_soup = BeautifulSoup(html_string, "html.parser")
    url = get_case_pdf_url(fake_soup)
    assert url == "foobar"


"""
Testing get_case_title
"""


def test_get_case_title_returns_string():
    html_string = """
            <h1 class="judgment-toolbar__title">
                Foobar
            </h1>
        """

    fake_soup = BeautifulSoup(html_string, "html.parser")
    title = get_case_title(fake_soup)

    assert isinstance(title, str)


def test_get_case_title_returns_correct_title():
    html_string = """
            <h1 class="judgment-toolbar__title">Foobar</h1>
        """

    fake_soup = BeautifulSoup(html_string, "html.parser")
    title = get_case_title(fake_soup)

    assert title == "Foobar"


def test_get_case_title_changes_slash_to_dash():
    html_string = """
            <h1 class="judgment-toolbar__title">Foo/bar</h1>
        """

    fake_soup = BeautifulSoup(html_string, "html.parser")
    title = get_case_title(fake_soup)

    assert title == "Foo-bar"
