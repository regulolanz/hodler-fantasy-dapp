import json
import requests
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = 'hodlerfc'
    file_key = 'hodlerfc.json'
    try:
        # Download the JSON file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_key)

        # Parse the JSON content
        json_data = json.loads(response['Body'].read().decode('utf-8'))
        
    # Parse query parameters
    query_parameters = event.get("queryStringParameters", {})
    playerNames = query_parameters.get("playerNames", {})
    splitPlayerNames = playerNames.split(',')
    
    player_data = {}
    for name in splitPlayerNames:
        if name in json_data:
            player_data[name] = {
                    "Matchday Key": json_data[name].get("Matchday Key", ""),
                    "Fantasy Points": json_data[name].get("Fantasy Points", "")
                }
        
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