import os
import nselib
from nselib import capital_market
import pickle
import pandas as pd
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ensure_data_directory():
    if not os.path.exists("data"):
        os.makedirs("data")

def equity():
    try:
        # Fetch equity list
        df = capital_market.equity_list()

        # Convert 'DATE OF LISTING' to datetime
        df[' DATE OF LISTING'] = pd.to_datetime(df[' DATE OF LISTING'], format='%d-%b-%Y')

        # Sort by date in descending order (latest first)
        df = df.sort_values(by=' DATE OF LISTING', ascending=False)

        # Reset index for a clean DataFrame
        df = df.reset_index(drop=True)

        # Combine 'NAME OF COMPANY' and 'SYMBOL' into a single column
        df['Combined'] = df['NAME OF COMPANY'] + " (" + df['SYMBOL'] + ")"

        # Get the cleaned list of dropdown values
        dropdown_values = df['Combined'].dropna().unique().tolist()

        ensure_data_directory()
        with open("data/dropdown_data.pkl", "wb") as f:
            pickle.dump(dropdown_values, f)

        logging.info("Equity data successfully scrapped.")
    except Exception as e:
        logging.error(f"Error in equity(): {e}")

def mutual_funds():
    try:
        response = requests.get("https://api.mfapi.in/mf")
        response.raise_for_status()
        data = response.json()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Combine scheme name and code
        df["Combined"] = df["schemeName"] + " (" + df["schemeCode"].astype(str) + ")"

        # Get unique dropdown values
        dropdown_values = df["Combined"].dropna().unique().tolist()

        ensure_data_directory()
        with open("data/mutual_dropdown_data.pkl", "wb") as f:
            pickle.dump(dropdown_values, f)

        logging.info("Mutual fund data successfully fetched.")
    except Exception as e:
        logging.error(f"Error in mutual_funds(): {e}")

def cryptocurrencies():
    try:
        res = requests.get("https://api.coingecko.com/api/v3/coins/list")
        res.raise_for_status()
        data = res.json()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Combine name and symbol
        df["Combined"] = df["name"] + " (" + df["symbol"].str.upper() + ")"

        # Get unique dropdown values
        dropdown_values = df["Combined"].dropna().unique().tolist()

        ensure_data_directory()
        with open("data/crypto_dropdown_data.pkl", "wb") as f:
            pickle.dump(dropdown_values, f)

        logging.info("Crypto data successfully fetched.")
    except Exception as e:
        logging.error(f"Error in cryptocurrencies(): {e}")

if __name__ == "__main__":
    equity()
    mutual_funds()
    cryptocurrencies()
