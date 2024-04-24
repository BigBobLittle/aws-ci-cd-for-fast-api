from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt
from jose.exceptions import JWTError
import requests

# Replace these with your actual Cognito user pool values
REGION = "your-cognito-region"
USER_POOL_ID = "your-cognito-user-pool-id" # 
APP_CLIENT_ID = "your-cognito-app-client-id" # "

user_pool_client_name = "your-user-name"
security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    # Get JWKS (JSON Web Key Set) from Cognito
    url = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"
    jwks = requests.get(url).json()

    # Decode and verify JWT token
    try:
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        if rsa_key:
            payload = jwt.decode(token, rsa_key, algorithms=["RS256"], audience=APP_CLIENT_ID)
            return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or token expired")



from datetime import datetime

def get_current_user(token: str = Depends(security)):
    # Your existing code to validate and decode JWT token
    payload = jwt.decode(token, rsa_key, algorithms=["RS256"], audience=APP_CLIENT_ID)

    # Check token expiration time
    expiration_time = payload.get('exp')
    current_time = datetime.utcnow().timestamp()
    if expiration_time and current_time > expiration_time:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    
    return payload



import uuid

def get_current_user(token: str = Depends(security)):
    # Your existing code to validate and decode JWT token
    payload = jwt.decode(token, rsa_key, algorithms=["RS256"], audience=APP_CLIENT_ID)

    # Generate session ID
    session_id = str(uuid.uuid4())

    # Store session ID in DynamoDB
    store_session_id_in_dynamodb(payload['sub'], session_id)

    return payload


import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UserSessionsTable')  # Assuming you have a table to store user sessions

def store_session_id_in_dynamodb(user_id: str, session_id: str):
    # Check if the session ID already exists for the user
    response = table.query(
        KeyConditionExpression=Key('userId').eq(user_id)
    )
    items = response['Items']
    if items:
        # Update existing session ID
        table.update_item(
            Key={'userId': user_id},
            UpdateExpression='SET sessionId = :session_id',
            ExpressionAttributeValues={':session_id': session_id}
        )
    else:
        # Insert new session ID
        table.put_item(
            Item={'userId': user_id, 'sessionId': session_id}
        )
