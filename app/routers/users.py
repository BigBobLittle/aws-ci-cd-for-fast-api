from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import boto3
from ..utilities.db import DynamoDBManager
router = APIRouter()
congnito_client = boto3.client('cognito-idp', region_name='eu-west-2')

dynamodb = DynamoDBManager()
class User(BaseModel):
    email: str
    password: str
    
@router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/me")
async def read_user_me():
    return {"username": "fakecurrentuser"}


@router.get("/{username}")
async def read_user(username: str):
    return {"username": username}

@router.post("/register")
def register_user(user: User):
    try:
        response = congnito_client.sign_up(
            ClientId='468tmt14qk5orusat4ob4vg1vh',
            Username=user.email,
            Password=user.password
        )
        return {"message": "User registered successfully"}
    except congnito_client.exceptions.UsernameExistsException:
        raise HTTPException(status_code=400, detail="Email already exists")
        
    except congnito_client.exceptions.InvalidPasswordException:
        raise HTTPException(status_code=400, detail="Invalid password")
    except Exception as e:
        return {"message": f"An error occurred: {str(e)}"}
    

@router.post("/login")
def login_user(user: User):
    try:
        response = congnito_client.initiate_auth(
            ClientId='468tmt14qk5orusat4ob4vg1vh',
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': user.email,
                'PASSWORD': user.password
            }
        )
        # create session in dynamodb
        t = dynamodb.create_session(user.email)
        print(t)
        return {"message": "User logged in successfully", "token": response.get('AuthenticationResult').get('AccessToken')}
    except congnito_client.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    except congnito_client.exceptions.UserNotFoundException:
        raise HTTPException(status_code=404, detail="User not found")
    except congnito_client.exceptions.UserNotConfirmedException:
        raise HTTPException(status_code=400, detail="User not confirmed")
    except Exception as e:
        print(e)
        return {"message": f"An error occurred: {str(e)}"}
    