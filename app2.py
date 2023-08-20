import os
import json
import streamlit as st
from web3 import Web3
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('sample.env')
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY")
WEB3_PROVIDER_URI = os.getenv("WEB3_PROVIDER_URI")
SMART_CONTRACT_ADDRESS = os.getenv("SMART_CONTRACT_ADDRESS")

# Define Pinata API endpoints
PINATA_BASE_URL = "https://indigo-sufficient-porpoise-423.mypinata.cloud" # minh's gateway, modify as needed 
PINATA_GET_IPFS_DATA_ENDPOINT = f"{PINATA_BASE_URL}/ipfs/"

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))

# Function to load the smart contract
@st.cache(allow_output_mutation=True)
def load_contract():

    # Load PlayerToken ABI
    with open(Path('./contracts/compiled/PlayerToken_abi.json')) as f:
        player_token_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=player_token_abi
    )
    # Return the contract from the function
    return contract

# Load the contract
contract = load_contract()

# Select Account to Mint
st.title("Fantasy Soccer Player Minting")
st.write("Choose an account to mint a new player token")
accounts = w3.eth.accounts
address = st.selectbox("Select Account", options=accounts)
st.markdown("---")

# Function to retrieve JSON data from Pinata using CID
def retrieve_json_data_from_pinata(cid, pinata_secret_api_key):
    headers = {
        "Authorization": f"Bearer {pinata_secret_api_key}"
    }

    response = requests.get(f"{PINATA_GET_IPFS_DATA_ENDPOINT}{cid}", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to retrieve JSON data from Pinata. Status Code: {response.status_code}")
        st.text(response.content.decode())  # Print response content for debugging
        return None

# Function to display player data in boxes
def display_player_data(player_data):
    for player in player_data:
        st.write(f"Player Name: {player['playerName']} {player['playerLastName']}")
        st.write(f"Team: {player['team']}")
        st.write(f"Position: {player['position']}")
        st.write(f"League: {player['league']}")
        st.write(f"Season: {player['season']}")
        st.write(f"Nationality: {player['nationality']}")
        st.write(f"Year of Birth: {player['yearOfBirth']}")
        st.write(f"Fantasy Points: {player['fantasyPoints']}")
        st.text(" \n")  # Add some spacing between player data

# Retrieve JSON data from Pinata using the CID
cid = "QmWh8wwhLMbZxRJ3PjSTZe3FnFUD5y8DyvBxXxB7EgqtFG"
player_db = retrieve_json_data_from_pinata(cid, PINATA_SECRET_API_KEY)

if player_db:
    
     # Display the player data in boxes
    display_player_data(player_db)
    
    # Allow the user to select a player to buy
    selected_player_name = st.selectbox("Select a Player to Mint", options=[player for player in player_db])

    if st.button("Mint Player"):
        selected_player = selected_player_name
        tx_hash = contract.functions.mint(
            address,
            "ipfs://example-ipfs-hash",  # Replace with actual IPFS hash of tokenURI
            selected_player_name
        ).transact({'from': address, 'value': contract.functions.PRICE_IN_ETH().call(), 'gas': 1000000})
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write("Transaction receipt mined:")
        st.write(dict(receipt))
        st.write("Player token has been minted!")