from fastapi import FastAPI, Depends
from mangum import Mangum
from dotenv import load_dotenv
from .utilities.cognito_setup import cognito_eu
from fastapi_cognito import CognitoToken
from .routers import items, users

app = FastAPI()
load_dotenv()



# print("dynamodb", dynamodb)
@app.get("/hi")
async def root(auth:CognitoToken= Depends(cognito_eu.auth_required)):
    return {"message": "Hello World1"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


app.include_router(items.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


handler = Mangum(app=app)



