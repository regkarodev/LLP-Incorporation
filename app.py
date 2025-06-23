import requests
import pandas as pd
import time
import json
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import os 
from dotenv import load_dotenv


# --- 1. Load Environment Variables ---
# This line loads the variables from your .env file into the environment
load_dotenv()

MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")


# --- 1. Configuration: These values have been updated from your latest HAR file ---

# The full, valid cookie string for your session.
COOKIE_STRING = os.getenv("COOKIE_STRING")

# The matching CSRF token for the cookie above.

CSRF_TOKEN = os.getenv("CSRF_TOKEN")


# --- 2. Setup the Request Details (No changes needed below this line) ---

base_url = "https://www.mca.gov.in"
api_url = f"{base_url}/bin/mca/applicationHistory"

# Headers to mimic the browser's request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": base_url,
    "Referer": f"{base_url}/content/mca/global/en/application-history.html",
    "Cookie": COOKIE_STRING
}

# The different tabs you want to scrape data from
tabs_to_scrape = {
    'Filed_Ongoing': 'FO',
    'Under_Processing': 'UP',
    'Approved_Registered': 'AR',
    'Rejected': 'RN',
    'Cancelled': 'CX',
    'Payment_History': 'PS'
}

all_records = []
session = requests.Session()

# --- 3. Loop Through Tabs and Scrape Data ---

print("\nStarting data scraping with the provided Cookie and CSRF Token...")

for tab_name, tab_code in tabs_to_scrape.items():
    print(f"Fetching data for tab: '{tab_name}' ({tab_code})")

    # The payload now uses the CSRF_TOKEN you provided
    payload = {
        "requestType": "applicationHistory",
        "tab": tab_code,
        "cin": "",
        "srnno": "",
        "csrfToken": CSRF_TOKEN,
        "fromDate": "",
        "toDate": "",
        "profUser": ""
    }

    try:
        # Make the POST request using the session
        response = session.post(api_url, headers=headers, data=payload)
        response.raise_for_status() # Raises an error for bad status codes (like 403 Forbidden)

        json_response = response.json()

        if "data" in json_response and json_response["data"]:
            records = json_response["data"]
            for record in records:
                record['source_tab'] = tab_name
            all_records.extend(records)
            print(f"  > Success! Found {len(records)} records.")
        else:
            message = json_response.get("message", "No data")
            print(f"  > Success! Server message: '{message}'")

    except requests.exceptions.HTTPError as e:
        print(f"  > FAILED. An HTTP error occurred: {e}. This often means your Cookie or CSRF Token is invalid or has expired.")
    except ValueError:
        # This error happens when the server sends HTML (like a login page) instead of JSON
        print(f"  > FAILED. The server did not return valid data. Your Cookie or CSRF Token is almost certainly expired.")

    time.sleep(1) # Pause for 1 second between requests



# --- 5. Save the Collected Data to MongoDB ---

if all_records:
    print(f"\nAttempting to connect to MongoDB and save {len(all_records)} records...")
    client = None # Initialize client to None
    try:
        # Establish connection to MongoDB
        client = MongoClient(MONGO_CONNECTION_STRING)
        # Test the connection
        client.admin.command('ping')
        print("MongoDB connection successful.")

        # Select the database and collection
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # To avoid duplicates, you can optionally delete old records for this user before inserting new ones.
        # This is commented out by default. Uncomment if you want to clear the collection each time.
        # print("Deleting old records...")
        # collection.delete_many({}) # Deletes all documents in the collection

        # Insert the new records into the collection
        result = collection.insert_many(all_records)
        print(f"Successfully inserted {len(result.inserted_ids)} new documents into the '{COLLECTION_NAME}' collection.")

    except ConnectionFailure as e:
        print(f"\nMongoDB Connection Failed: {e}")
        print("Please ensure your MongoDB server is running and the connection string is correct.")
    except OperationFailure as e:
        print(f"\nAn error occurred during a database operation: {e}")
        print("This could be due to authentication issues (username/password) or permissions.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        # Ensure the connection is closed
        if client:
            client.close()
            print("MongoDB connection closed.")
else:
    print("\nScraping finished, but no records were collected to save to the database.")