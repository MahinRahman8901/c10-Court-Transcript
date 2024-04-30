"""Python script that extracts, transforms and loads
case-relevant information to a relational database service on AWS"""

from extract import extract_cases
from transform import transform_and_apply_gpt
from load import load_to_database


def main():
    """Run the pipeline functions -
    Web scrapes government case website
    Clean, process and pass data to openai API
    Upload case data to RDS
    """

    cases = extract_cases(1)

    if not cases.empty:
        transformed_cases = transform_and_apply_gpt(cases)

        load_to_database(transformed_cases)


def handler(event, context):
    """Pass the main function to a handler to be run by Lambda on AWS"""

    main()


if __name__ == "__main__":

    main()
