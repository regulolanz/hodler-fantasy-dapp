import os
import json
import requests
from dotenv import load_dotenv

load_dotenv('../SAMPLE.env')

# ================== Headers ===================
json_headers = {
    "Content-Type": "application/json",
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY"),
}

file_headers = {
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY"),
}


# ========= Data Conversion to JSON ============
def convert_data_to_json(content):
    """
    Convert data to Pinata's desired JSON format.
    """
    data = {
        "pinataOptions": {"cidVersion": 1},
        "pinataContent": content
    }
    return json.dumps(data)


# ========== Pin File to IPFS via Pinata ========
def pin_file_to_ipfs(data):
    """
    Pins a file to IPFS using Pinata's pinFileToIPFS endpoint.
    """
    r = requests.post(
        "https://api.pinata.cloud/pinning/pinFileToIPFS",
        files={'file': data},
        headers=file_headers
    )
    response_json = r.json()
    print(response_json)  # For debugging purposes.
    
    if "IpfsHash" not in response_json:
        raise Exception("Unexpected response format from Pinata. 'IpfsHash' key not found. Response:", response_json)
        
    ipfs_hash = response_json["IpfsHash"]
    return ipfs_hash


# ========== Pin JSON to IPFS via Pinata ========
def pin_json_to_ipfs(data):
    """
    Pins a JSON object to IPFS using Pinata's pinJSONToIPFS endpoint.
    """
    # Convert the data to a serialized JSON string
    json_data = json.dumps(data)

    r = requests.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        data=json_data,  # Note: you're sending the serialized JSON string now
        headers=json_headers  # Make sure this has "Content-Type": "application/json"
    )
    response_json = r.json()
    print(response_json)  # For debugging purposes.
    
    if "IpfsHash" not in response_json:
        raise Exception("Unexpected response format from Pinata. 'IpfsHash' key not found. Response:", response_json)

    ipfs_hash = response_json["IpfsHash"]
    return ipfs_hash


# ========= Fetch Data from IPFS via Pinata ========
def fetch_from_ipfs(ipfs_hash):
    """
    Fetches data from IPFS using Pinata's Cloud API.
    """
    try:
        response = requests.get(f"https://api.pinata.cloud/gateway/v0/ipfs/{ipfs_hash}", headers=json_headers)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.RequestException as err:
        print(f"Error fetching data from IPFS: {err}")
        return {}
