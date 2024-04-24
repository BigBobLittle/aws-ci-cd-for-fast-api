import os
from jose import jwt, jwk
from jose.utils import base64url_decode
from typing import Dict, List, Optional

import requests

JWK = Dict[str, str]
JWKS = Dict[str, List[JWK]]


def get_jwks() -> JWKS:
    return requests.get(
        f"https://cognito-idp.{os.environ.get('COGNITO_REGION')}.amazonaws.com/"
        f"{os.environ.get('COGNITO_POOL_ID')}/.well-known/jwks.json"
    ).json()
    


def get_public_hmac(token:str, jwks: JWKS) -> Optional[JWK]:
    kid = jwt.get_unverified_header(token).get('kid')
    for key in jwks.get('keys', []):
        if key.get('kid') == kid:
            return key
    
    
def verify_jwt(token:str, jwks:JWKS) -> bool: 
    hmac_key = get_public_hmac(token, jwks)
    
    if not hmac_key:
        raise ValueError("No public key found")
    
    hmac_key = jwk.construct(get_public_hmac(token, jwks))
    
    message, encoded_signature = str(token).rsplit('.', 1)
    decoded_signature = base64url_decode(encoded_signature.encode())   
    return hmac_key.verify(message.encode(), decoded_signature)
    
# test = get_jwks()
# print(test) 
