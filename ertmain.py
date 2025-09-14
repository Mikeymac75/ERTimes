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
OLLAMA_API_URL = "http://localhost:11434/api/generate" # Default Ollama API URL

async def capture_screenshot(page, url, screenshot_path):
    """
    Navigates to a URL and captures a screenshot using an existing page object.
    """
    try:
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"Error capturing screenshot from {url}: {e}")
        return None

def encode_image(image_path):
    """
    Encodes an image file to base64.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_with_moondream(image_path):
    """
    Sends a screenshot to the Moondream server for analysis.
    """
    print(f"Analyzing {image_path} with Moondream...")
    base64_image = encode_image(image_path)

    payload = {
        "model": "moondream",
        "prompt": "Analyze the attached screenshot of a hospital wait times website. Extract the name of the hospital and all wait time categories with their corresponding patient counts and wait times. Return the data as a clean, machine-readable JSON object. The JSON should have keys like 'hospital_name', 'patients_in_waiting_room', 'urgent_patients', 'urgent_wait_time', etc.",
        "images": [base64_image],
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        response_json = response.json()
        json_data_str = response_json.get('response')
        # Clean up the response from Moondream
        clean_json_str = json_data_str.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_json_str)
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error processing Moondream response: {e}")
        return None

def flatten_json_data(data):
    """
    Transforms the nested JSON data from the AI model into a flat dictionary.
    """
    flat_data = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "HospitalName": data.get("hospital_name"),
        "DataUpdated": data.get("data_updated"),
    }

    for item in data.get("wait_times", []):
        category = item.get("category", "").replace(" ", "")
        patients = item.get("patients")
        wait_time = item.get("wait_time")

        if "PatientsintheWaitingRoom" in category:
            flat_data["PatientsInWaitingRoom"] = patients
        elif "MostUrgent" in category:
            flat_data["MostUrgent_Patients"] = patients
            flat_data["MostUrgent_WaitTime"] = wait_time
        elif "Urgent(Level3)" in category:
            flat_data["Urgent_Patients"] = patients
            flat_data["Urgent_WaitTime"] = wait_time
        elif "LessthanUrgent(Level4&5)" in category:
            flat_data["LessUrgent_Patients"] = patients
            flat_data["LessUrgent_WaitTime"] = wait_time

    additional_stats = data.get("additional_stats", {})
    flat_data["PatientsBeingTreated"] = additional_stats.get("patients_being_treated")
    flat_data["TotalPatientsInED"] = additional_stats.get("total_patients_in_ed")

    return flat_data

def save_to_csv(flat_data):
    """
    Saves the flattened data to a CSV file.
    """
    file_exists = os.path.isfile(CSV_FILE)
    
    fieldnames = [
        "Timestamp", "HospitalName", "DataUpdated",
        "PatientsInWaitingRoom", "MostUrgent_Patients", "MostUrgent_WaitTime",
        "Urgent_Patients", "Urgent_WaitTime", "LessUrgent_Patients", "LessUrgent_WaitTime",
        "PatientsBeingTreated", "TotalPatientsInED"
    ]

    try:
        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(flat_data)
        print(f"Data successfully saved to {CSV_FILE}")
    except IOError as e:
        print(f"Error writing to file: {e}")


async def main():
    """
    Main function to orchestrate the scraping process.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            while True:
                for url in URLS:
                    screenshot_path = f"screenshot_{URLS.index(url)}.png"
                    screenshot_path = await capture_screenshot(page, url, screenshot_path)

                    if screenshot_path:
                        # Analyze the screenshot with Moondream
                        wait_time_data = analyze_image_with_moondream(screenshot_path)

                        if wait_time_data:
                            # Flatten the data and save to CSV
                            flat_data = flatten_json_data(wait_time_data)
                            save_to_csv(flat_data)

                        # Clean up the screenshot file
                        if os.path.exists(screenshot_path):
                            os.remove(screenshot_path)

                # Wait for an hour (3600 seconds) before running again
                print("Waiting for 1 hour before next scrape...")
                time.sleep(3600)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
