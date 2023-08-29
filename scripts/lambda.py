import json
import boto3

s3 = boto3.client('s3')

# ===================== Utility Functions =====================

def is_matching_player(player_json_entry, team, league, season):
    """Check if the player matches the specified criteria."""
    return player_json_entry['League'] == league and player_json_entry['Season'] == season and player_json_entry['Team'] == team

def fetch_player_data_from_s3(bucket_name, file_key):
    """Retrieve player data from the S3 bucket."""
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    return json.loads(response['Body'].read().decode('utf-8'))

# ===================== Lambda Handler =====================

def lambda_handler(event, context):
    """Main AWS Lambda handler function."""
    bucket_name = 'hodlersports'
    file_key = 'hodlerfc.json'

    try:
        # Retrieve player data
        player_data = fetch_player_data_from_s3(bucket_name, file_key)
        
        # Extract query parameters
        query_parameters = event.get("queryStringParameters", {})
        player_name = query_parameters.get("playerName", "")
        league = query_parameters.get("league", "")
        team = query_parameters.get("team", "")
        season = query_parameters.get("season", "")

        response_data = {}
        if player_name in player_data:
            for entry in player_data[player_name]:
                if is_matching_player(entry, team, league, season):
                    response_data[player_name] = {
                        "Fantasy Points": entry.get("Fantasy Points", "")
                    }
                    break  # Exit the loop once the matching entry is found
            else:
                print("Matching criteria not found for player!")
        else:
            print("Invalid Input or Player not found!")

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps(response_data)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': 'Internal Server Error'
        }