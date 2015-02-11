""" scraper.py - Web Identity Scraper

Collects user identity information from a website.
"""
import argparse
import requests
import re

from BeautifulSoup import BeautifulSoup
from tldextract import TLDExtract
tldextract = TLDExtract(suffix_list_url=False)


def image(soup, url, domain):
    images = soup.findAll('img', width=re.compile("\d+"))
    for image in images:
        if image['width'] > 0 or image['height'] > 0:
            # Not a pixel beacon
            resource_url = image['src']
            extract = tldextract(resource_url)
            resource_domain = '%s.%s' % (extract.domain, extract.suffix)
            if domain != resource_domain:
                yield (url, resource_url, domain, resource_domain, 'image')
    

def video(soup, url, domain):
    videos = soup.findAll('video')
    for video in videos:
        resource_url = video['src']
        extract = tldextract(resource_url)
        resource_domain = '%s.%s' % (extract.domain, extract.suffix)
        if domain != resource_domain:
            yield (url, resource_url, domain, resource_domain, 'video')


def pixelBeacon(soup, url, domain):
    beacons = soup.findAll('img', {'width': 1, 'height': 1})
    for beacon in beacons:
        resource_url = beacon['src']
        extract = tldextract(resource_url)
        resource_domain = '%s.%s' % (extract.domain, extract.suffix)
        if domain != resource_domain:
            yield (url, resource_url, domain, resource_domain, 'pixel beacon')

def facebookLike(soup, url, domain):
    return []
def twitterTweet(soup, url, domain):
    return []
def pinterestPin(soup, url, domain):
    return []

def scrape(url):
    """Grab identity information from the given URL.

    :Parameters:
      - `url`: The url of a website.
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    extract = tldextract(url)
    domain = '%s.%s' % (extract.domain, extract.suffix)

    tuples = set()
    categories = [image, video, pixelBeacon, facebookLike, twitterTweet, pinterestPin]
    for category in categories:
        tuples.update(category(soup, url, domain))

    for tpl in sorted(tuples):
        print '%s, %s, %s, %s, %s' % tpl

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
    for url in args.url:
        scrape(url)
