from selenium import webdriver
import re, sys

url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
test_url = sys.argv[1]

driver = webdriver.Firefox()
driver.get(test_url)
main_window_handle = driver.window_handles[0]

filtered = []
a_tags = driver.find_elements_by_tag_name('a')
for a_tag in a_tags:
	href = a_tag.get_attribute('href')
	if a_tag.is_displayed() and (not href or not re.match(url_regex, href) or href.startswith(driver.current_url)) and a_tag.size['width'] > 2 and a_tag.size['height'] > 2:
		a_tag.click()
		if len(driver.window_handles) > 1:
			for window_handle in driver.window_handles:
				if window_handle != main_window_handle:
					driver.switch_to_window(window_handle)
					print driver.current_url
					driver.close()
			driver.switch_to_window(main_window_handle)
		
driver.quit()

