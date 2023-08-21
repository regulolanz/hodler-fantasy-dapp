import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import phonenumbers
import pycountry

from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json

load_dotenv('SAMPLE.env')

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# Cache the contract on load
@st.cache(allow_output_mutation=True)
def load_contract():
    # Load PlayerToken ABI
    with open(Path('./contracts/compiled/player_registration_abi.json')) as f:
        player_registration_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=player_registration_abi
    )
    return contract

# Get all nationalities
nationalities = [country.name for country in pycountry.countries]

# Get all country codes
country_codes = [f"+{phonenumbers.COUNTRY_CODE_TO_REGION_CODE[code][0]}: +{code}" for code in phonenumbers.COUNTRY_CODE_TO_REGION_CODE if code]

# Load the contract
contract = load_contract()

# Title
st.title("Fantasy Soccer Player Registration")
st.write("Choose an account to register a new player")
accounts = w3.eth.accounts
address = st.selectbox("Select Account", options=accounts)

# Check if the player is already registered
is_registered = contract.functions.isPlayerRegistered(address).call()

if is_registered:
    st.warning(f"The address {address} is already registered as a player!")
    st.stop()

st.markdown("---")

# Registration form
st.markdown("## Register a New Player")
player_name = st.text_input("Enter the player's first name")
player_last_name = st.text_input("Enter the player's last name")

# Nationality Dropdown
nationality = st.selectbox("Select nationality", options=nationalities)

# Date of Birth
from datetime import datetime
current_year = datetime.now().year
dob = st.date_input("Date of Birth", min_value=datetime(1900, 1, 1), max_value=datetime(current_year, 12, 31))

# Phone with Country Code
selected_country_code = st.selectbox("Country Code", options=country_codes)
phone_number = st.text_input("Phone Number")

uploaded_file = st.file_uploader("Upload a selfie")

if st.button("Register Player"):
    if not uploaded_file:
        st.write("Please upload a selfie.")
        st.stop()

    # Here, you would ideally pin the uploaded selfie to IPFS and then pin the player details in JSON form.
    selfie_hash = pin_file_to_ipfs(uploaded_file)
    player_data = {
        "name": player_name,
        "lastName": player_last_name,
        "nationality": nationality,
        "dob": dob.strftime("%Y-%m-%d"),
        "phone": selected_country_code + phone_number,
        "selfieHash": selfie_hash
    }
    player_data_hash = pin_json_to_ipfs(player_data)

    tx_hash = contract.functions.registerPlayer(address, player_data_hash).transact({'from': address, 'gas': 1000000})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))
    st.write("Player has been registered!")

st.markdown("---")
