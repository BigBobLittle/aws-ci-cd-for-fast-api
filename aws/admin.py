from fastapi import APIRouter, Depends
from typing import List
from boto3.dynamodb.conditions import Key

admin_router = APIRouter()

@admin_router.get("/admin/show_texts/{user_id}")
def admin_show_texts(user_id: str, user: dict = Depends(get_current_admin_user)):
    # Check if the user exists
    if not user_exists(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Retrieve texts for the specified user
    response = table.query(
        KeyConditionExpression=Key('userId').eq(user_id)
    )
    texts = response['Items']
    return {"texts": texts}
