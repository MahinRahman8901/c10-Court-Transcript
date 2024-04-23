"""Python script responsible for extracting judge data using web scraping"""

from os import environ as ENV
from time import sleep
import logging
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup


if __name__ == "__main__":

    load_dotenv()
