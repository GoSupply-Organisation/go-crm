import time
# importing webdriver from selenium
from selenium import webdriver

# Here Chrome  will be used
driver = webdriver.Chrome()

# URL of website
url = "https://www.geeksforgeeks.org/"

# Opening the website
driver.get(url)

# getting the button by class name
button = driver.find_element_by_class_name("slide-out-btn")

# clicking on the button
button.click()