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

@st.cache(allow_output_mutation=True)
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

st.title("Fantasy Soccer Player Registration")
st.write("Choose an account to register a new player")
accounts = w3.eth.accounts
address = st.selectbox("Select Account", options=accounts)

is_registered = player_registration_contract.functions.isPlayerRegistered(address).call()
is_waitlisted = player_registration_contract.functions.isWaitlisted(address).call()
is_owner = address == os.getenv("OWNER_ADDRESS")

if not is_registered:
    if is_waitlisted:
        st.write(f"The address {address} is on the waitlist but not yet registered.")

    if is_waitlisted or is_owner:
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

            tx_hash = player_registration_contract.functions.registerPlayer(address, player_data_hash).transact({'from': address, 'gas': 3000000})
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.write("Transaction receipt mined:")
            st.write(dict(receipt))
            st.write("Player has been registered!")

            if 'status' in receipt and receipt['status'] == 1:
                is_registered = True

if is_registered:
    st.markdown("---")
    st.markdown("## Mint a New Player Card")

    team = st.text_input("Enter Team Name")
    position = st.selectbox("Position", options=["GOA", "DEF", "MID", "STK"])
    league = st.text_input("Enter League Name")
    season = st.text_input("Enter Season (e.g., 2023/2024)")
    profile_picture_file = st.file_uploader("Upload Player's Profile Picture")

    if st.button("Mint Player Card"):
        if not profile_picture_file:
            st.write("Please upload a profile picture.")
            st.stop()

        profile_picture_hash = pin_file_to_ipfs(profile_picture_file)

        tx_hash = player_card_contract.functions.mintCard(
            team, 
            position, 
            league, 
            season, 
            profile_picture_hash
        ).transact({'from': address, 'gas': 3000000})
        
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write("Transaction receipt mined:")
        st.write(dict(receipt))
        st.write("Player card has been minted!")
