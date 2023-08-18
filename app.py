import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json

load_dotenv('SAMPLE.env')

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

################################################################################
# Contract Helper function:
# 1. Loads the contract once using cache
# 2. Connects to the contract using the contract address and ABI
################################################################################

# Cache the contract on load
@st.cache(allow_output_mutation=True)
# Define the load_contract function
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

################################################################################
# Mint New Player Token
################################################################################
st.title("Fantasy Soccer Player Minting")
st.write("Choose an account to mint a new player token")
accounts = w3.eth.accounts
address = st.selectbox("Select Account", options=accounts)
st.markdown("---")

################################################################################
# Mint New Player Token Form
################################################################################
st.markdown("## Mint New Player Token")
player_name = st.text_input("Enter the player's name")
player_last_name = st.text_input("Enter the player's last name")
team = st.text_input("Enter the team")
position = st.text_input("Enter the position")
league = st.text_input("Enter the league")
season = st.text_input("Enter the season")
nationality = st.text_input("Enter the nationality")
year_of_birth = st.number_input("Enter the year of birth", min_value=1900, max_value=2023, step=1)
fantasy_points = st.number_input("Enter the initial fantasy points", min_value=0, step=1)

if st.button("Mint Player Token"):
    player_attributes = {
        "playerName": player_name,
        "playerLastName": player_last_name,
        "team": team,
        "position": position,
        "league": league,
        "season": season,
        "nationality": nationality,
        "yearOfBirth": year_of_birth,
        "fantasyPoints": fantasy_points
    }

    tx_hash = contract.functions.mint(
        address,
        "ipfs://example-ipfs-hash",  # Replace with actual IPFS hash of tokenURI
        player_attributes
    ).transact({'from': address, 'value': contract.functions.PRICE_IN_ETH().call(), 'gas': 1000000})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))
    st.write("Player token has been minted!")

st.markdown("---")
