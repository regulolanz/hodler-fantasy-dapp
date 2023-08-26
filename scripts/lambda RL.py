import os
import json
import requests
import boto3
from web3 import Web3

s3 = boto3.client('s3')

# Initialize Web3
contract_address = Web3.toChecksumAddress(os.getenv('PLAYER_REGISTRATION_CONTRACT_ADDRESS'))
infura_endpoint = os.getenv('INFURA_ENDPOINT')
sender_address = os.getenv('SENDER_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')

w3 = Web3(Web3.HTTPProvider(infura_endpoint))
contract = w3.eth.contract(address=contract_address, abi=YOUR_CONTRACT_ABI)  # Add your ABI

def lambda_handler(event, context):
    bucket_name = 'hodlerfc'
    file_key = 'hodlerfc.json'
    
    # Download the JSON file from S3
    response = s3.get_object(Bucket=bucket_name, Key=file_key)

    # Parse the JSON content
    json_data = json.loads(response['Body'].read().decode('utf-8'))
        
    # Parse query parameters
    query_parameters = event.get("queryStringParameters", {})
    playerNames = query_parameters.get("playerNames", "")
    splitPlayerNames = playerNames.split(',')
    
    player_data = {}
    for name in splitPlayerNames:
        if name in json_data:
            player_data[name] = {
                    "Matchday Key": json_data[name].get("Matchday Key", ""),
                    "Fantasy Points": json_data[name].get("Fantasy Points", "")
                }
            
            # Update points in Ethereum
            tx = contract.functions.updateFantasyPoints(name, json_data[name].get("Fantasy Points", "")).buildTransaction({
                'from': sender_address,
                'nonce': w3.eth.getTransactionCount(sender_address),
                'gas': 2000000,
                'gasPrice': w3.toWei('20', 'gwei')
            })

            signed_tx = w3.eth.account.signTransaction(tx, private_key)
            tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            print(w3.toHex(tx_hash))
        
        else:
            print(f"Invalid Player: {name}")
            
    # Construct a response
    response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps(player_data)
        }

    return response
