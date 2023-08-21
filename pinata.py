import os
import json
import requests
from dotenv import load_dotenv
load_dotenv('SAMPLE.env')

json_headers = {
    "Content-Type": "application/json",
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY"),
}

file_headers = {
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY"),
}

def convert_data_to_json(content):
    data = {"pinataOptions": {"cidVersion": 1}, "pinataContent": content}
    return json.dumps(data)

def pin_file_to_ipfs(data):
    r = requests.post(
        "https://api.pinata.cloud/pinning/pinFileToIPFS",
        files={'file': data},
        headers=file_headers
    )
    response_json = r.json()
    print(response_json)  # You already have this, which is good for debugging.
    
    if "IpfsHash" not in response_json:
        raise Exception("Unexpected response format from Pinata. 'IpfsHash' key not found. Response:", response_json)
        
    ipfs_hash = response_json["IpfsHash"]
    return ipfs_hash

def pin_json_to_ipfs(data):
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
