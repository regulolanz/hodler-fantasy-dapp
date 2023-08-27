import os
import json
import pycountry
import phonenumbers
from web3 import Web3
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import requests

from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json

load_dotenv('SAMPLE.env')
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

MINTING_FEE_IN_USD = 50

position_options = ["GOA", "DEF", "MID", "STK"]
league_options = ["UPSL_Division_1", "USSL_Elite", "PFL_Division_1"]
season_options = ["2023_Spring", "2023_Fall"]
team_options = ["Hodler Miami FC"]

def load_contracts():
    # Load ABIs
    with open(Path('./contracts/compiled/registration_abi.json')) as f:
        player_registration_abi = json.load(f)
    
    with open(Path('./contracts/compiled/player_card_abi.json')) as f:
        player_card_abi = json.load(f)

    # Contract addresses
    player_registration_address = os.getenv("PLAYER_REGISTRATION_CONTRACT_ADDRESS")
    player_card_address = os.getenv("PLAYER_CARD_CONTRACT_ADDRESS")

    # Create contracts
    player_registration_contract = w3.eth.contract(
        address=player_registration_address,
        abi=player_registration_abi
    )
    
    player_card_contract = w3.eth.contract(
        address=player_card_address,
        abi=player_card_abi
    )

    return player_registration_contract, player_card_contract

player_registration_contract, player_card_contract = load_contracts()

def register_player():
    st.markdown("## Register a New Player")
    
    # Player details
    nationalities = [country.name for country in pycountry.countries]
    country_codes = [f"+{phonenumbers.COUNTRY_CODE_TO_REGION_CODE[code][0]}: +{code}" for code in phonenumbers.COUNTRY_CODE_TO_REGION_CODE if code]
        
    player_name = st.text_input("Enter the player's first name")
    player_last_name = st.text_input("Enter the player's last name")
    nationality = st.selectbox("Select nationality", options=nationalities)
    dob = st.date_input("Date of Birth")
    selected_country_code = st.selectbox("Country Code", options=country_codes)
    phone_number = st.text_input("Phone Number")
    uploaded_file = st.file_uploader("Upload a selfie")

    if st.button("Register Player"):
        try:
            if not uploaded_file:
                st.write("Please upload a selfie.")
                st.stop()

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
            
            # Gas estimation and transaction
            gas_estimate = player_registration_contract.functions.registerPlayer(player_data_hash).estimateGas({'from': address, 'gas': 5000000})
            tx_hash = player_registration_contract.functions.registerPlayer(player_data_hash).transact({'from': address, 'gas': gas_estimate})

            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.success("Player has been registered!")
            st.write(dict(receipt))
        except ValueError as ve:
            st.error(f"Transaction error: {ve}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

def mint_player_card():
    st.markdown("## Mint a Player Card")
    
    team = st.selectbox("Select player's team", options=team_options)
    position = st.selectbox("Select player's position", options=position_options)
    league = st.selectbox("Select league", options=league_options)
    season = st.selectbox("Select season", options=season_options)
    profile_picture = st.text_input("Profile picture URL or IPFS hash")
    fantasy_points = 0  # Initial value, user can't modify

    current_eth_price = player_card_contract.functions.getCurrentPrice().call()
    required_fee_in_eth = player_card_contract.functions.calculateMintingFee().call()

    if st.button("Mint Card"):
        try:
            tx_hash = player_card_contract.functions.mintCard(team, position, league, season, profile_picture, fantasy_points).transact({'from': address, 'value': required_fee_in_eth})
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.success("Player card minted!")
            st.write(dict(receipt))
        except ValueError as ve:
            st.error(f"Transaction error: {ve}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

st.title("Fantasy Soccer Player Registration")
address = st.selectbox("Select Account", options=w3.eth.accounts)

# Check if the player is registered
is_registered = player_registration_contract.functions.isPlayerRegistered(address).call()

# Check if the account has the REGISTRAR_ROLE
REGISTRAR_ROLE = player_registration_contract.functions.REGISTRAR_ROLE().call()
is_waitlisted = player_registration_contract.functions.playerInfos(address).call()[2]

# Logic to display registration, minting, and other options
if is_registered:
    mint_player_card()
elif is_waitlisted:
    register_player()
    
def update_fantasy_points():  # only owner 
    st.markdown("## Update Fantasy Points")
    
    player_name = st.text_input("Enter the player's full name")
    league = st.selectbox("Select league", options=league_options)
    season = st.selectbox("Select season", options=season_options)
    team = st.selectbox("Select player's team", options=team_options)
    
    if st.button("Update Fantasy Points"):
        # Prepare the data to send in the request
        data = {
            "playerName": player_name,
            "league": league,
            "season": season,
            "team": team,
            # Add more data as needed
        }
        
        # Define the API Gateway URL
        api_gateway_url = "https://mdaq0itlok.execute-api.us-east-2.amazonaws.com/prod/chainlink" # replace with your gateway from GET method
        
        # Send an HTTP GET request to the API Gateway
        response = requests.get(api_gateway_url, json=data)
        
       # Needs interaction with PlayerCard contract and call updateFantasyPoints function