from bs4 import BeautifulSoup
import requests
import csv
import threading

def scrape_tenders(url):
    """
    Scrape tender information from the given URL
    """
    # Set headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Make the request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all tender elements
        tender_wraps = soup.find_all('div', class_='tender-wrap')
        
        tenders = []
        
        # Process each tender
        for tender in tender_wraps:
            # Extract the title
            title_element = tender.find('div', class_='title-wrap col-12 col-sm-12 p-2 pb-2')
            title = title_element.find('span', itemprop='name').text.strip() if title_element else "No title found"
            
            # Extract the link
            link_element = tender.find('a', class_='btn btn-new')
            link = link_element['href'] if link_element else "No link found"
            
            # Extract additional information if needed
            # Country
            country_element = tender.find('span', itemprop='address')
            country = country_element.text.strip() if country_element else "No country found"
            
            # Posting date
            posting_date_element = tender.find('div', itemprop='startDate')
            posting_date = posting_date_element.text.strip() if posting_date_element else "No posting date found"
            
            # Deadline
            deadline_element = tender.find('div', itemprop='endDate')
            deadline = deadline_element.text.strip() if deadline_element else "No deadline found"
            
            tenders.append({
                'title': title,
                'link': link,
                'country': country,
                'posting_date': posting_date,
                'deadline': deadline
            })
        
        return tenders
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []
    except Exception as e:
        print(f"Error parsing the HTML: {e}")
        return []

# def save_to_csv(tenders, filename='tenders.csv'):
#     """
#     Save the tender data to a CSV file
#     """
#     if not tenders:
#         print("No tenders to save")
#         return
    
#     # Define the field names
#     fieldnames = ['title', 'link', 'country', 'posting_date', 'deadline']
    
#     # Write to CSV
#     with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(tenders)
    
#     print(f"Saved {len(tenders)} tenders to {filename}")

# def more_info(url):
#     driver = webdriver.Chrome()
#     driver.get(url)
#     button = driver.find_element_by_class_name("btn btn-new")
#     button.click()
#     driver.quit()


def main():
    # URL of the page you want to scrape
    url = "https://www.globaltenders.com/australia/au-healthcare-equipment-services-tenders"  # Replace with the actual URL
    
    print("Scraping tenders...")
    tenders = scrape_tenders(url)
    # more_info(url)
    
    if tenders:
        print(f"Found {len(tenders)} tenders")
        
        # Print the first 5 tenders as an example
        for i, tender in enumerate(tenders[:20]):
            print(f"\nTender {i+1}:")
            print(f"Title: {tender['title']}")
            print(f"Link: {tender['link']}")
            print(f"Country: {tender['country']}")
            print(f"Posting Date: {tender['posting_date']}")
            print(f"Deadline: {tender['deadline']}")
        

    else:
        print("No tenders found or an error occurred")

if __name__ == "__main__":
    main()

