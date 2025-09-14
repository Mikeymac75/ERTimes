# PEI Emergency Room Wait Time Tracker

This project scrapes the emergency room wait times for hospitals on Prince Edward Island. It uses a multimodal AI approach to visually extract data from the [official Health PEI website](https://www.princeedwardisland.ca/en/information/health-pei/emergency-department-wait-times). It runs continuously, saving the data every hour to a CSV file. This allows for building a historical record of wait times to analyze trends.

## Features

- Uses Playwright to take screenshots of hospital wait time pages.
- Leverages a local Moondream model to extract wait time data from screenshots.
- Saves data with a timestamp to `hospital_wait_times.csv`.
- Runs automatically every hour to collect data continuously.

## How to Use

### 1. Prerequisites

This project requires a locally running instance of the Moondream model. You can set this up using [Ollama](https://ollama.ai/).

1.  **Install Ollama:** Follow the instructions on the Ollama website to install it on your system.
2.  **Pull the Moondream model:** Once Ollama is installed, pull the Moondream model by running the following command in your terminal:
    ```bash
    ollama pull moondream
    ```
3.  **Ensure the Ollama server is running:** The script connects to the Ollama API at `http://localhost:11434`. Make sure the Ollama application is running before you start the scraper.

### 2. Setup

First, you need to install the necessary Python dependencies. It's recommended to do this in a virtual environment.

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install the required packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 3. Running the Scraper

To start the scraper, simply run the `ertmain.py` script:

```bash
python ertmain.py
```

The script will then start running in your terminal. It will print status messages as it navigates to the hospital websites, takes screenshots, and analyzes them with Moondream.

```
Navigating to https://www.princeedwardisland.ca/en/feature/emergency-department-wait-times-queen-elizabeth-hospital-qeh...
Screenshot saved to screenshot_0.png
Analyzing screenshot_0.png with Moondream...
Data successfully saved to hospital_wait_times.csv
...
Waiting for 1 hour before next scrape...
```

You can stop the scraper at any time by pressing `Ctrl+C` in the terminal.

### 4. The Output

The scraped data is saved in a file named `hospital_wait_times.csv`. A new entry for each hospital is added every hour.

The CSV file has the following columns:

- **Timestamp**: The date and time when the data was scraped.
- **HospitalName**: The name of the hospital.
- **DataUpdated**: The timestamp from the website indicating when the data was last updated.
- **PatientsInWaitingRoom**: The number of patients in the waiting room.
- **MostUrgent_Patients**: The number of patients in the "Most Urgent" category.
- **MostUrgent_WaitTime**: The wait time for the "Most Urgent" category.
- **Urgent_Patients**: The number of patients in the "Urgent" category.
- **Urgent_WaitTime**: The wait time for the "Urgent" category.
- **LessUrgent_Patients**: The number of patients in the "Less Urgent" category.
- **LessUrgent_WaitTime**: The wait time for the "Less Urgent" category.
- **PatientsBeingTreated**: The number of patients currently being treated.
- **TotalPatientsInED**: The total number of patients in the Emergency Department.
