""" scraper.py - Web Identity Scraper

Collects user identity information from a website.
"""
import argparse
import requests

from lxml import html


def scrape(url):
    """Grab identity information from the given URL.

    :Parameters:
      - `url`: The url of a website.
    """
    # TODO


if __name__ == "__main__":
    # Set up command line options
    parser = argparse.ArgumentParser(
            prog="scraper",
            description="Finds user identity info on websites")
    parser.add_argument(
            "url",
            nargs="+",
            help="One or more URLs to scrape.")

    args = parser.parse_args()

    # Begin work
    for url in args.urls:
        scrape(url)
