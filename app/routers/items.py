from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import authenticate_user, check_session
# from ..dependencies import get_token_header
from boto3.dynamodb.conditions import Key
import datetime
import boto3
import os 
import uuid 
import time 
from datetime import datetime
from decimal import Decimal
# from ..main import dynamodb
from ..utilities.db import DynamoDBManager

dynamodb = DynamoDBManager()
router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(authenticate_user), Depends(check_session)],
    responses={404: {"description": "Not found"}},
)


fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get("/fetch_my_items")
async def read_items(current_user=Depends(authenticate_user) ):
    
    # session_id:str = Depends(check_session)
    user_id = current_user.get("sub")
    try:
        response = dynamodb.table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)  
        )
        items = response['Items']
        return items
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error retrieving items")

@router.get("/fetch_all_items")
async def read_all_items(current_user=Depends(authenticate_user)):
     # Check if user is in the admin group
    print('user', current_user)
    if "cognito_groups" in current_user and "admin" in current_user["cognito_groups"]:
        
        response = dynamodb.table.scan()
        items = response['Items']
        return items
    else:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # If the response is paginated, continue scanning until all items are retrieved
    # while 'LastEvaluatedKey' in response:
    #     response = dynamodb.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    #     items.extend(response['Items'])

    # # Process the items
    # for item in items:
    #     print(item)
    
    return items



@router.post("/create_item")
async def save_item(text:str, current_user:dict=Depends(authenticate_user)):
    user_id = current_user.get("sub")
    timestamp= datetime.now().isoformat()
    
    try:
        textTable = dynamodb.table.put_item(
            Item={
                
                "user_id": user_id,
                "timestamp": timestamp,
                "text": text,
                # Add timestamps
                'created_at': Decimal(str(datetime.now().timestamp()))
                #  'updated_at': Decimal(str(datetime.now().timestamp()))
                    }
        )
        print(textTable)
        return {"message": "Text saved successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error saving text")


    
# @router.get("/{item_id}")
# async def read_item(item_id: str):
#     if item_id not in fake_items_db:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return {"name": fake_items_db[item_id]["name"], "item_id": item_id}


# @router.put(
#     "/{item_id}",
#     tags=["custom"],
#     responses={403: {"description": "Operation forbidden"}},
# )
# async def update_item(item_id: str):
#     if item_id != "plumbus":
#         raise HTTPException(
#             status_code=403, detail="You can only update the item: plumbus"
#         )
#     return {"item_id": item_id, "name": "The great Plumbus"}