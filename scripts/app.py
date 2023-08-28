import os
import json
import pycountry
import phonenumbers
from web3 import Web3
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import requests

from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json, fetch_from_ipfs

# Initialize environment and web3
load_dotenv('../SAMPLE.env')
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# Constants
MINTING_FEE_IN_USD = 50
position_options = ["GOA", "DEF", "MID", "STK"]
league_options = ["UPSL_Division_1", "USSL_Elite", "PFL_Division_1"]
season_options = ["2023_Spring", "2023_Fall"]
team_options = ["Hodler Miami FC"]

# ===================== Contract Initialization =====================
def load_contracts():
    with open(Path('../metadata/player_registration_abi.json')) as f:
        player_registration_abi = json.load(f)
    
    with open(Path('../metadata/player_card_abi.json')) as f:
        player_card_abi = json.load(f)

    player_registration_address = os.getenv("PLAYER_REGISTRATION_CONTRACT_ADDRESS")
    player_card_address = os.getenv("PLAYER_CARD_CONTRACT_ADDRESS")

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

ADMIN_ROLE = player_card_contract.functions.ADMIN_ROLE().call()

# ===================== Player Registration =====================
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

# ===================== Player Card Minting =====================
def mint_player_card():
    st.markdown("## Mint a Player Card")
    
    team = st.selectbox("Select player's team", options=team_options, key="mint_team")
    position = st.selectbox("Select player's position", options=position_options, key="mint_position")
    league = st.selectbox("Select league", options=league_options, key="mint_league")
    season = st.selectbox("Select season", options=season_options, key="mint_season")
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

# Global variable to maintain a mapping of card ID to player name
card_id_to_player_name = {}

# ===================== Fetch Player Data for All Cards =====================
def fetch_player_data_for_all_cards():
    # Fetch all card IDs
    all_card_ids = player_card_contract.functions.getAllCardIds().call()

    # Mapping to store card ID to player details
    card_id_to_player_details = {}

    for card_id in all_card_ids:
        player_address = player_card_contract.functions.cards(card_id).call()[0]
        ipfs_hash = player_registration_contract.functions.playerInfos(player_address).call()[1]
        player_data = fetch_from_ipfs(ipfs_hash)
        
        # Store the required details in the mapping
        card_id_to_player_details[card_id] = {
            "name": player_data["name"],
            "lastName": player_data["lastName"],
            "dob": player_data["dob"],
            "nationality": player_data["nationality"]
        }

    return card_id_to_player_details

# ===================== Fantasy Points Update =====================
def update_fantasy_points_on_chain(player_name, league, season, fantasy_points):
    # Find the card IDs using the mapping
    card_ids_for_player = [key for key, value in card_id_to_player_name.items() if value == player_name]
    
    if not card_ids_for_player:
        st.error(f"Couldn't find any cards associated with the name {player_name}")
        return

    for card_id in card_ids_for_player:
        card_data = player_card_contract.functions.cards(card_id).call()
        if card_data["isActive"] and card_data["league"] == league and card_data["season"] == season:
            try:
                tx_hash = player_card_contract.functions.updateFantasyPoints(card_id, fantasy_points).transact({'from': address})
                receipt = w3.eth.waitForTransactionReceipt(tx_hash)
                st.success(f"Fantasy points updated on-chain for card ID {card_id}!")
                st.write(dict(receipt))
            except ValueError as ve:
                st.error(f"Transaction error for card ID {card_id}: {ve}")
            except Exception as e:
                st.error(f"An unexpected error occurred for card ID {card_id}: {e}")

def update_fantasy_points():
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
            "team": team
        }
        
        # Define the API Gateway URL
        api_gateway_url = "https://mdaq0itlok.execute-api.us-east-2.amazonaws.com/prod/chainlink"
        
        # Send an HTTP GET request to the API Gateway
        api_response = requests.get(api_gateway_url, json=data)
    
        if api_response.status_code == 200:
            response_data = api_response.json()
            if player_name in response_data:
                fantasy_points = response_data[player_name]["Fantasy Points"]
                update_fantasy_points_on_chain(player_name, fantasy_points)
            else:
                st.error(f"Error fetching data for {player_name}")
        else:
            st.error(f"API error: {api_response.text}")

# ===================== Display All Registered Players =====================
def display_all_players():
    st.markdown("## List of Registered Players")
    for player_address in w3.eth.accounts:
        if player_registration_contract.functions.isPlayerRegistered(player_address).call():
            player_info = player_registration_contract.functions.playerInfos(player_address).call()
            player_data_hash = player_info[1]  # Assuming ipfsHash is the second item in the struct
            player_data = fetch_from_ipfs(player_data_hash)
            
            st.write(f"Player Number: {player_info[0]}")  # Assuming playerNumber is the first item in the struct
            st.write(f"Player Name: {player_data['name']} {player_data['lastName']}")
            st.write(f"DOB: {player_data['dob']}")
            st.write(f"Nationality: {player_data['nationality']}")
            st.write("----")

# ===================== Display All Minted Cards =====================
def display_all_cards():
    st.markdown("## List of All Minted Player Cards")
    all_card_ids = player_card_contract.functions.getAllCardIds().call()

    for card_id in all_card_ids:
        card_data = player_card_contract.functions.cards(card_id).call()
        player_address = card_data[0]  # Assuming the playerAddress is the first item in the struct
        player_info_hash = player_registration_contract.functions.playerInfos(player_address).call()[1]  # ipfsHash is the second item
        player_info = fetch_from_ipfs(player_info_hash)
        
        st.write(f"Card ID: {card_id}")
        st.write(f"Player Name: {player_info['name']} {player_info['lastName']}")
        st.write(f"Team: {card_data[1]}")  # Assuming team is the second item in the Card struct
        st.write(f"Position: {card_data[2]}")  # and so on for the other attributes...
        st.write(f"Fantasy Points: {card_data[6]}")  # Assuming fantasyPoints is the seventh item in the Card struct
        st.write("----")

# ===================== Main Streamlit App =====================
st.title("Fantasy Soccer Player Registration")

# Sidebar
st.sidebar.header("Account")
address = st.sidebar.selectbox("Select Account", options=w3.eth.accounts)

is_registered = player_registration_contract.functions.isPlayerRegistered(address).call()
REGISTRAR_ROLE = player_registration_contract.functions.REGISTRAR_ROLE().call()
is_waitlisted = player_registration_contract.functions.playerInfos(address).call()[3]

# Check if the connected address has the ADMIN_ROLE in the player_card_contract
if player_card_contract.functions.hasRole(ADMIN_ROLE, address).call():
    update_fantasy_points()

if is_registered:
    mint_player_card()
elif is_waitlisted:
    register_player()
    st.success(f"Your player number is: {player_registration_contract.functions.playerInfos(address).call()[0]}")

display_all_players()
display_all_cards() 

# Update the mapping when the app starts
card_id_to_player_details = fetch_player_data_for_all_cards()