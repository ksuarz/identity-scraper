#!/usr/bin/env python
""" scraper.py - Web Identity Scraper

Collects user identity information from a website.
"""
import argparse
import requests
import re

from BeautifulSoup import BeautifulSoup
from tldextract import TLDExtract
from selenium import webdriver
tldextract = TLDExtract(suffix_list_url=False)
driver = webdriver.Firefox()
url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'


def image(soup, url, domain, min_dim=5):
    """Finds images on pages with minimum dimension.

    Images with dimension greater than `dim` are considered to be real images;
    otherwise, they are skipped and classified as pixel beacons.
    """
    images = soup.findAll('img', width=re.compile("\d+"))
    for image in images:
        if int(image['width']) > min_dim or int(image['height']) > min_dim:
            # Not a pixel beacon
            resource_url = image['src']
            extract = tldextract(resource_url)
            resource_domain = '%s.%s' % (extract.domain, extract.suffix)
            if domain != resource_domain:
                yield (url, resource_url, domain, resource_domain, 'image')
    

def video(soup, url, domain):
    """Finds video tags."""
    videos = soup.findAll('video')
    for video in videos:
        resource_url = video['src']
        extract = tldextract(resource_url)
        resource_domain = '%s.%s' % (extract.domain, extract.suffix)
        if domain != resource_domain:
            yield (url, resource_url, domain, resource_domain, 'video')


def pixelBeacon(soup, url, domain):
    # Should also check for 2x2, maybe just greater than 5 in any dimension? 
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
    driver.get(url)
    main_window_handle = driver.window_handles[0]
    a_tags = driver.find_elements_by_tag_name('a')
    for a_tag in a_tags:
        href = a_tag.get_attribute('href')
        # candidate tags either: don't have a href, have a href that doesn't look like a url, or start with the current url (essentially an extension of 2nd case because selenium always returns absolute href, even if it was something like "#")
        if a_tag.is_displayed() and (not href or not re.match(url_regex, href) or href.startswith(driver.current_url)) and a_tag.size['width'] > 2 and a_tag.size['height'] > 2:
            a_tag.click()
            if len(driver.window_handles) > 1: # rather, if a new window opened as a result of our click
                for window_handle in driver.window_handles:
                    if window_handle != main_window_handle: # find new windows
                        driver.switch_to_window(window_handle)
                        # we're looking at url of popup window here
                        if driver.current_url.startswith('https://twitter.com/intent/tweet'):
                            yield (url, driver.current_url, domain, 'twitter.com', 'twitter tweet')
                        ########
                        driver.close() # close the popup window, move on to any others
                driver.switch_to_window(main_window_handle) # switch back to main window


def googleLogin(soup, url, domain):
    google_oauth = 'https://accounts.google.com/o/openid'

    # Begin navigation to the page
    driver.get(url)
    main_window_handle = driver.window_handles[0]

    # Explore all possible links
    links = driver.find_elements_by_tag_name('a')
    for link in links:
        href = link.get_attribute('href')

        # Candidates are links with no href or links with no valid href (e.g.
        # '#') since there is JavaScript magic that does the login
        if (link.is_displayed() and (not href or not url_regex.match(href)) and
                int(link.size['width']) > 2 and int(link.size['height'])) > 2:
            link.click()

            # Pop-ups and the main window
            for window_handle in driver.window_handles:
                driver.switch_to_window(window_handle)
                # Found a Google OAuth page
                if driver.current_url.startswith(google_oauth):
                    yield (url, driver.current_url, domain,
                           'google.com', 'Google Login')
                # Close this popup
                if window_handle != main_window_handle:
                    driver.close()

            # Return to the main window
            driver.switch_to_window(main_window_handle)


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
    categories = [image, video, pixelBeacon, facebookShare, twitterTweet, pinterestPin]
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
    driver.quit()
