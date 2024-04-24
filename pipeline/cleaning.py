'''Cleans the date and name columns of a given dataframe so that the dates are in the format dd/mm/yyyy 
and the names are stripped of their titles.'''

import re

import pandas as pd

from extract import extract_cases


def is_correct_date_format(date: str) -> bool:
    '''Checks that the given date has format dd/mm/yyyy.'''

    date_pattern = r"\d{2}/\d{2}/\d{4}"
    result = re.match(date_pattern, date)

    if result:
        return True

    return False


def format_date(date: str, split_on: str):
    '''Formats dates that are given in format d/mm/yyyy or d month yyyy.'''

    components = date.split(split_on)

    if len(components[0]) == 1:
        components[0] = '0' + components[0]

    if components[1].isalpha():

        months = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
                  'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'}

        components[1] = months[components[1]]

    formatted_date = "/".join(components)

    return formatted_date


def clean_date(date: str) -> str:
    '''If date is in (incorrect) format d/mm/yyyy or d month yyyy then formats it to dd/mm/yyyy.
    Any other (incorrect) formats return None.'''
    if not is_correct_date_format(date):

        extracted_date = re.search(
            r"\d\d? [A-Za-z]+ \d\d(\d\d)?|\d/\d\d/\d\d\d?\d?", date)

        if extracted_date:

            match = extracted_date.group(0)

            if "/" in match:
                formatted_date = format_date(match, "/")

            else:
                formatted_date = format_date(match, " ")

            return formatted_date

        return None

    return date


if __name__ == "__main__":

    data = extract_cases(5)
    data['date'] = data['date'].apply(clean_date)
