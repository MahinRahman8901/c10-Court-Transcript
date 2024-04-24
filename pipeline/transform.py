"""This script is responsible for transforming court transcript data into meaningful sentiments"""

from os import environ as ENV

from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
from extract import extract_cases


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

    cases['verdict'] = cases['conclusion'].apply(
        get_case_verdict, args=(AI,))

    cases['summary'] = cases['introduction'].apply(
        get_case_summary, args=(AI,))

    cleaned_cases = cases.drop(columns=['introduction', 'conclusion'])

    return cleaned_cases


if __name__ == "__main__":

    cases = extract_cases(1)

    transformed_cases = transform_and_apply_gpt(cases)
