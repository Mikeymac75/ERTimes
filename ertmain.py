import asyncio
from playwright.async_api import async_playwright
import csv
from datetime import datetime
import time
import os
import base64
import requests
import json

# The URLs of the PEI hospital wait times pages
URLS = [
    "https://www.princeedwardisland.ca/en/feature/emergency-department-wait-times-queen-elizabeth-hospital-qeh#/service/ERWaitTimes_QEH/ERWaitTimes_QEH",
    "https://www.princeedwardisland.ca/en/feature/emergency-department-wait-times-prince-county-hospital-pch#/service/ERWaitTimes_PCH/ERWaitTimes_PCH",
    "https://www.princeedwardisland.ca/en/feature/emergency-department-wait-times-kings-county-memorial-hospital-kcmh#/service/ERWaitTimes_KCMH/ERWaitTimes_KCMH",
    "https://www.princeedwardisland.ca/en/feature/emergency-department-wait-times-western-hospital#/service/ERWaitTimes_WH/ERWaitTimes_WH"
]

# The name of the file where we'll save the data
CSV_FILE = "hospital_wait_times.csv"
LLAVA_API_URL = "http://localhost:11434/api/generate" # Default Ollama API URL

async def capture_screenshot(url, screenshot_path):
    """
    Navigates to a URL and captures a screenshot.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
            return screenshot_path
        except Exception as e:
            print(f"Error capturing screenshot from {url}: {e}")
            return None
        finally:
            await browser.close()

def encode_image(image_path):
    """
    Encodes an image file to base64.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_with_llava(image_path):
    """
    Sends a screenshot to the Llava server for analysis.
    """
    print(f"Analyzing {image_path} with Llava...")
    base64_image = encode_image(image_path)

    payload = {
        "model": "llava",
        "prompt": "Analyze the attached screenshot of a hospital wait times website. Extract the name of the hospital and all wait time categories with their corresponding patient counts and wait times. Return the data as a clean, machine-readable JSON object. The JSON should have keys like 'hospital_name', 'patients_in_waiting_room', 'urgent_patients', 'urgent_wait_time', etc.",
        "images": [base64_image]
    }

    try:
        response = requests.post(LLAVA_API_URL, json=payload)
        response.raise_for_status()
        # The response from ollama is a stream of json objects, we need to parse the last one
        lines = response.text.strip().split('\n')
        last_line = lines[-1]
        json_data_str = json.loads(last_line).get('response')
        # Clean up the response from Llava
        clean_json_str = json_data_str.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_json_str)
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error processing Llava response: {e}")
        return None

def save_to_csv(data):
    """
    Saves the parsed data to a CSV file.
    Creates the file and writes the header if it doesn't exist.
    """
    file_exists = os.path.isfile(CSV_FILE)
    
    # Define the column names for the CSV file
    fieldnames = [
        "Timestamp",
        "HospitalName",
        "DataUpdated",
        "Category",
        "Patients",
        "WaitTime",
        "PatientsBeingTreated",
        "TotalPatientsInED"
    ]

    # Prepare the rows to be written to the CSV
    rows_to_write = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    hospital_name = data.get("hospital_name")
    data_updated = data.get("data_updated")
    additional_stats = data.get("additional_stats", {})
    patients_being_treated = additional_stats.get("patients_being_treated")
    total_patients_in_ed = additional_stats.get("total_patients_in_ed")

    for entry in data.get("wait_times", []):
        rows_to_write.append({
            "Timestamp": timestamp,
            "HospitalName": hospital_name,
            "DataUpdated": data_updated,
            "Category": entry.get("category"),
            "Patients": entry.get("patients"),
            "WaitTime": entry.get("wait_time"),
            "PatientsBeingTreated": patients_being_treated,
            "TotalPatientsInED": total_patients_in_ed
        })

    try:
        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(rows_to_write)
        print(f"Data successfully saved to {CSV_FILE}")
    except IOError as e:
        print(f"Error writing to file: {e}")


async def main():
    """
    Main function to orchestrate the scraping process.
    """
    while True:
        for url in URLS:
            screenshot_path = f"screenshot_{URLS.index(url)}.png"
            screenshot_path = await capture_screenshot(url, screenshot_path)
            
            if screenshot_path:
                # Analyze the screenshot with Llava
                wait_time_data = analyze_image_with_llava(screenshot_path)

                if wait_time_data:
                    # Save the data to the CSV file
                    save_to_csv(wait_time_data)

                # Clean up the screenshot file
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)

        # Wait for an hour (3600 seconds) before running again
        print("Waiting for 1 hour before next scrape...")
        time.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
