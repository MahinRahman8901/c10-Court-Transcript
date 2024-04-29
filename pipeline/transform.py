'''Script to standardize and clean data as well as extracting summaries and verdicts using GPT.'''
import re
import pandas as pd

from os import environ as ENV
from dotenv import load_dotenv
from openai import OpenAI
from extract import extract_cases


def is_correct_date_format(date: str) -> bool:
    '''Checks that the given date has format dd/mm/yyyy.'''

    date_pattern = r"\d{2}/\d{2}/\d{4}"
    result = re.match(date_pattern, date)

    if result:
        return True

    return False


def format_date(date: str, split_on: str) -> str:
    '''Formats dates that are given in format d/mm/yyyy or d month yyyy.'''

    components = date.split(split_on)

    if int(components[0]) == 0:
        components[0] = '01'

    if len(components[0]) == 1:
        components[0] = '0' + components[0]

    if components[1].isalpha():

        months = {'January': '01', 'February': '02',
                  'March': '03', 'April': '04',
                  'May': '05', 'June': '06',
                  'July': '07', 'August': '08',
                  'September': '09', 'October': '10',
                  'November': '11', 'December': '12'}

        components[1] = months[components[1]]

    if len(components[2]) == 2:
        components[2] = '20' + components[2]

    formatted_date = "/".join(components)

    return formatted_date


def clean_date(date: str) -> str:
    '''If date is in incorrect format then determines how to 
    format it to dd/mm/yyyy. Any other (incorrect) formats return None.'''
    if not is_correct_date_format(date):

        extracted_date = re.search(
            r"\d\d? [A-Za-z]+ \d\d(\d\d)?|\d/\d\d/\d\d\d?\d?", date)

        if extracted_date:

            match = extracted_date.group(0)

            if "/" in match:
                formatted_date = format_date(match, "/")

            else:
                formatted_date = format_date(match, " ")

            return formatted_date.strip()

        return None

    return date.strip()


def strip_titles(full_name: str) -> str:
    '''Strips all titles so we are just left with the name.'''

    extras = ['mr', 'mrs', 'miss', 'ms', 'sir', 'justice', 'the', 'honourable',
              'his', 'her', 'honour', 'hon', 'kc', 'dbe', 'judge', 'dame']

    components = full_name.split(" ")

    judge_name = []

    for part in components:
        if part.lower() not in extras:
            judge_name.append(part)

    return ' '.join(judge_name).upper()


def standardize_case_no(case_no: str):
    '''Makes sure all case numbers are in the same format.'''
    if len(case_no) == 14:
        return case_no

    formatted = ''.join(case_no.split(' '))

    formatted = ' & '.join(formatted.split('&'))

    return formatted


def clean_data(data: pd.DataFrame):
    '''Formats dates and standardizes names and case number IDs..'''

    data['date'] = data['date'].apply(clean_date)
    data['judge_name'] = data['judge_name'].apply(strip_titles)
    data['case_no'] = data['case_no'].apply(standardize_case_no)


def get_case_verdict(conclusion: str, text_generator: OpenAI) -> str:
    """Extract case verdict as a single word"""

    response = text_generator.chat.completions.create(
        model="gpt-3.5-turbo",  # Use this one for testing
        messages=[
            {"role": "system", "content": "You are a solicitor reading case conclusion statements."},
            {"role": "user", "content": f"For the given case: '{conclusion}'. State in one word and no punctuation, in favour of whom did the judge rule, claimant or defendant?"},
        ]
    )

    return response.choices[0].message.content


def get_case_summary(introduction: str, text_generator: OpenAI) -> str:
    """Extract brief case summaries from introductions"""

    user_prompt = f"Given this introduction: '{introduction}'. Summarise the introduction to a few lines."

    response = text_generator.chat.completions.create(
        model="gpt-3.5-turbo",  # Use this one for testing
        messages=[
            {"role": "system", "content": "You are a solicitor reading case introduction statements."},
            {"role": "user", "content": user_prompt},
        ]
    )

    return response.choices[0].message.content


def transform_and_apply_gpt(cases: pd.DataFrame):
    """Run the complete transform script"""

    load_dotenv()

    AI = OpenAI(api_key=ENV["OPENAI_API_KEY"])

    clean_data(cases)

    cases['verdict'] = cases['conclusion'].apply(
        get_case_verdict, args=(AI,))

    cases['summary'] = cases['introduction'].apply(
        get_case_summary, args=(AI,))

    cleaned_cases = cases.drop(columns=['introduction', 'conclusion'])
    cleaned_cases.dropna(subset=['date'], inplace=True)

    cleaned_cases['date'] = pd.to_datetime(
        cleaned_cases['date'], dayfirst=True, format='mixed')

    return cleaned_cases


if __name__ == "__main__":

    cases = extract_cases(1)

    if not cases.empty:

        transformed_cases = transform_and_apply_gpt(cases)
