# PEI Emergency Room Wait Time Tracker

This project scrapes the emergency room wait times for hospitals on Prince Edward Island from the [official Health PEI website](https://www.princeedwardisland.ca/en/information/health-pei/emergency-department-wait-times). It runs continuously, saving the data every hour to a CSV file. This allows for building a historical record of wait times to analyze trends.

## Features

- Scrapes wait times for all hospitals listed on the Health PEI page.
- Saves data with a timestamp to `hospital_wait_times.csv`.
- Runs automatically every hour to collect data continuously.
- Cleans the scraped data for better readability.

## How to Use

### 1. Setup

First, you need to install the necessary Python dependencies. It's recommended to do this in a virtual environment.

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install the required packages
pip install -r requirements.txt
```

### 2. Running the Scraper

To start the scraper, simply run the `ertmain.py` script:

```bash
python ertmain.py
```

The script will then start running in your terminal. It will print status messages as it fetches new data.

```
Fetching new wait times...
Successfully scraped 4 entries.
Data successfully saved to hospital_wait_times.csv
Waiting for 1 hour before next scrape...
```

You can stop the scraper at any time by pressing `Ctrl+C` in the terminal.

### 3. The Output

The scraped data is saved in a file named `hospital_wait_times.csv`. A new entry for each hospital is added every hour.

The CSV file has the following columns:

- **Timestamp**: The date and time when the data was scraped (e.g., `2023-10-27 14:30:00`).
- **Hospital**: The name of the hospital.
- **WaitTime**: The estimated emergency room wait time at the time of scraping.
