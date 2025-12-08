import requests
from bs4 import BeautifulSoup

r = requests.get("https://www.globaltenders.com/australia/au-healthcare-equipment-services-tenders")
soup = BeautifulSoup(r.text, 'html.parser')

parsed=soup.find_all("div", {"class": "tender-wrap"})

print(parsed)



title_element = soup.find('div', class_='title-wrap')
title = title_element.find('span', itemprop='name').text.strip() if title_element else "No title found"

# Extract the link
link_element = soup.find('a', class_='btn btn-new')
link = link_element['href'] if link_element else "No link found"

print(f"Title: {title}")
print(f"Link: {link}")