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
driver = webdriver.PhantomJS()
url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

"""
    Easy categories that we do with BeautifulSoup
"""
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


def pixelBeacon(soup, url, domain, max_dim=5):
    # Should also check for 2x2, maybe just greater than 5 in any dimension? 
    images = soup.findAll('img', width=re.compile("\d+"))
    for image in images:
        if int(image['width']) > max_dim or int(image['height']) > max_dim:
            continue
        resource_url = image['src']
        extract = tldextract(resource_url)
        resource_domain = '%s.%s' % (extract.domain, extract.suffix)
        if domain != resource_domain:
            yield (url, resource_url, domain, resource_domain, 'pixel beacon')

"""
    Hard categories that we do with selenium
"""
def popup_urls(url):
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
                        yield driver.current_url
                        ########
                        driver.close() # close the popup window, move on to any others
                driver.switch_to_window(main_window_handle) # switch back to main window
                
def twitterTweet(url, domain, popup_url):
    if popup_url.startswith('https://twitter.com/intent/tweet'):
        return (url, popup_url, domain, 'twitter.com', 'Twitter tweet')

def googleLogin(url, domain, popup_url):
    if popup_url.startswith('https://accounts.google.com'):
        return (url, popup_url, domain, 'google.com', 'Google login')

def facebookLogin(url, domain, popup_url):
    if popup_url.startswith('https://www.facebook.com/login.php'):
        return (url, popup_url, domain, 'facebook.com', 'Facebook login')


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
    easy_categories = [image, video, pixelBeacon]
    for category in easy_categories:
        tuples.update(category(soup, url, domain))

    hard_categories = [twitterTweet, googleLogin, facebookLogin]
    for popup_url in popup_urls(url):
        for category in hard_categories:
            tpl = category(url, domain, popup_url)
            if tpl: tuples.add(category(url, domain, popup_url))

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
