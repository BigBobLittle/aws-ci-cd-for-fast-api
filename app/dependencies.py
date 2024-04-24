from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends, Header, status
from jose import jwt, jwk, JWTError
from typing import Dict, List, Optional
import requests
import os 
from jose.utils import base64url_decode 
from .utilities.db import DynamoDBManager

dynamodb_manager = DynamoDBManager()
security = HTTPBearer()

JWK = Dict[str, str]
JWKS = Dict[str, List[JWK]]


def get_jwks() -> JWKS:
    return requests.get(
        f"https://cognito-idp.{os.environ.get('COGNITO_REGION')}.amazonaws.com/"
        f"{os.environ.get('COGNITO_POOL_ID')}/.well-known/jwks.json"
    ).json()
# function to decode jwt 

def get_hmac_key(token: str, jwks: JWKS) -> Optional[JWK]:
    kid = jwt.get_unverified_header(token).get("kid")
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key

def decode_token(token: str) -> Optional[dict]:
    try:
        key = get_hmac_key(token, get_jwks())
        
        return jwt.decode(token, key=key, algorithms=["RS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def verify_jwt(token: str, jwks: JWKS) -> bool:
    hmac_key = get_hmac_key(token, jwks)

    if not hmac_key:
        raise ValueError("No pubic key found!")

    hmac_key = jwk.construct(get_hmac_key(token, jwks))

    message, encoded_signature = token.rsplit(".", 1)
    decoded_signature = base64url_decode(encoded_signature.encode())

    return hmac_key.verify(message.encode(), decoded_signature)

# Middleware to authenticate and authorize requests
async def authenticate_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    if creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=403, detail="Invalid authentication scheme")
    token = creds.credentials
    
    jwks = get_jwks()
    webtoken = verify_jwt(token=token, jwks=jwks)
    if not webtoken:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    # # decode token if it is valid 
    decoded_token = decode_token(token=token)
    print('decoded', decoded_token)
    username = decoded_token.get("username")
    sub = decoded_token.get("sub")
    cognito_groups = decoded_token.get("cognito:groups") or []
    
    return {"username": username, "sub": sub, "cognito_groups": cognito_groups}
     

# Custom dependency to check session validity
def check_session(session_id: Optional[str] = Header(None)):
    if not session_id or not dynamodb_manager.is_session_valid(session_id):
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    return session_id  

async def get_session_id(authorization: str = Header(...)):
    try:
        _, session_id = authorization.split()
        return session_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
async def authenticate_user(session_id: str = Depends(get_session_id)):
    if not dynamodb_manager.is_session_valid(session_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired, please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"session_id": session_id}

