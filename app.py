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

w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

@st.cache_resource
def load_contracts():
    # Load ABIs
    with open(Path('./contracts/compiled/player_registration_abi.json')) as f:
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
            gas_estimate = player_registration_contract.functions.registerPlayer(player_data_hash).estimateGas({'from': address})
            tx_hash = player_registration_contract.functions.registerPlayer(player_data_hash).transact({'from': address, 'gas': gas_estimate})

            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.success("Player has been registered!")
            st.write(dict(receipt))
        except ValueError as ve:
            st.error(f"Transaction error: {ve}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")


def mint_player_card():
    st.markdown("## Mint a New Player Card")
    
    team = st.text_input("Enter Team Name")
    position = st.selectbox("Position", options=["GOA", "DEF", "MID", "STK"])
    league = st.text_input("Enter League Name")
    season = st.text_input("Enter Season (e.g., 2023/2024)")
    profile_picture_file = st.file_uploader("Upload Player's Profile Picture")

    if st.button("Mint Player Card"):
        try:
            if not profile_picture_file:
                st.write("Please upload a profile picture.")
                st.stop()

            profile_picture_hash = pin_file_to_ipfs(profile_picture_file)

            # Adjust gas estimate by 20% for safety margin
            gas_estimate = player_card_contract.functions.mintCard(
                team, position, league, season, profile_picture_hash
            ).estimateGas({'from': address})

            gas_limit = int(gas_estimate * 1.20)  # 20% buffer

            tx_hash = player_card_contract.functions.mintCard(
                team, position, league, season, profile_picture_hash
            ).transact({'from': address, 'gas': gas_limit})

            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.success("Player card has been minted!")
            st.write(dict(receipt))
        except ValueError as ve:
            st.error(f"Transaction error: {ve}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

st.title("Fantasy Soccer Player Registration")

# Account selection
address = st.selectbox("Select Account", options=w3.eth.accounts)

# Check if the player is registered
is_registered = player_registration_contract.functions.isPlayerRegistered(address).call()

# Check if the account has the MINTER_ROLE
MINTER_ROLE = player_card_contract.functions.MINTER_ROLE().call()
is_registrar = player_card_contract.functions.hasRole(MINTER_ROLE, address).call()

# Check if player exists in the mapping and is not registered (thus, waitlisted)
player_info_hash = player_registration_contract.functions.getPlayerInfoHash(address).call()
is_waitlisted = player_info_hash != "" and not is_registered

# Logic to display registration and minting options
if is_registrar or not is_registered:
    if is_waitlisted:
        st.write(f"The address {address} is on the waitlist but not yet registered.")
    register_player()

if is_registered:
    mint_player_card()

