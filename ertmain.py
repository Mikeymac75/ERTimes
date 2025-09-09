import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
import os

# The URL of the PEI hospital wait times page
URL = "https://www.princeedwardisland.ca/en/information/health-pei/emergency-department-wait-times"

# The name of the file where we'll save the data
CSV_FILE = "hospital_wait_times.csv"

def scrape_wait_times():
    """
    Scrapes the hospital wait times from the Health PEI website
    and returns a list of dictionaries, one for each hospital.
    """
    print("Fetching new wait times...")
    try:
        # Get the webpage content
        response = requests.get(URL)
        response.raise_for_status() # This will raise an error for bad responses (4xx or 5xx)

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the sections that contain hospital wait time info
        # The site structure uses 'views-row' for each hospital block
        hospital_blocks = soup.find_all('div', class_='views-row')
        
        scraped_data = []
        
        # Get the current time for the timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for block in hospital_blocks:
            # Find the hospital name (it's in an h3 tag)
            hospital_name_tag = block.find('h3')
            hospital_name = hospital_name_tag.get_text(strip=True) if hospital_name_tag else "N/A"
            
            # Find the wait time (it's in a div with a specific class)
            wait_time_tag = block.find('div', class_='views-field-field-er-wait-times')
            if wait_time_tag:
                wait_time_text = wait_time_tag.get_text(strip=True)
                # Remove the "Wait Time:" prefix for cleaner data
                wait_time = wait_time_text.replace("Wait Time:", "").strip()
            else:
                wait_time = "N/A"
            
            # Add the collected data to our list
            scraped_data.append({
                "Timestamp": timestamp,
                "Hospital": hospital_name,
                "WaitTime": wait_time
            })
            
        print(f"Successfully scraped {len(scraped_data)} entries.")
        return scraped_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

def save_to_csv(data):
    """
    Saves the scraped data to a CSV file.
    Creates the file and writes the header if it doesn't exist.
    """
    # Check if the file already exists to decide whether to write the header
    file_exists = os.path.isfile(CSV_FILE)
    
    try:
        # Open the file in 'append' mode
        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
            # Define the column names
            fieldnames = ["Timestamp", "Hospital", "WaitTime"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # If the file is new, write the header row
            if not file_exists:
                writer.writeheader()
            
            # Write the data rows
            writer.writerows(data)
            
        print(f"Data successfully saved to {CSV_FILE}")
        
    except IOError as e:
        print(f"Error writing to file: {e}")


if __name__ == "__main__":
    while True:
        # 1. Scrape the data
        data_to_save = scrape_wait_times()
        
        # 2. If data was scraped successfully, save it
        if data_to_save:
            save_to_csv(data_to_save)
            
        # 3. Wait for an hour (3600 seconds) before running again
        print("Waiting for 1 hour before next scrape...")
        time.sleep(3600)
