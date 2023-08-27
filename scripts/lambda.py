import json
import requests
import boto3

s3 = boto3.client('s3')


def isMatchingPlayer(playerJson, team, league, season):
    if playerJson['League'] == league and playerJson['Season'] == season and playerJson['Team'] == team:
        return True
    return False


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
        player_name = query_parameters.get("playerName", "")
        league = query_parameters.get("league", "")
        team = query_parameters.get("team", "")
        season = query_parameters.get("season", "")

        player_data = {}
        if (player_name) in json_data:
            if isMatchingPlayer(json_data[player_name], team, league, season):
                player_data[player_name] = {
                    "Fantasy Points": json_data[player_name].get("Fantasy Points", "")
                }
        else:
            print("Invalid Input!")

        # Construct a response
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps(player_data)
        }

        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': 'Internal Server Error'
        }
