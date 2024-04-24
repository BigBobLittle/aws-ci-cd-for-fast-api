from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
import boto3
import os
import boto3

app = FastAPI()
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
table = dynamodb.Table('TextsTable')


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TextsTable')

class TextRequest(BaseModel):
    text: str

@app.post("/save_text")
def save_text(text_request: TextRequest, user: dict = Depends(get_current_user)):
    item = {
        'userId': user['sub'],
        'text': text_request.text,
        'timestamp': int(time.time())
    }
    table.put_item(Item=item)
    return {"message": "Text saved successfully"}

@app.get("/show_texts")
def show_texts(user: dict = Depends(get_current_user)):
    response = table.query(
        KeyConditionExpression=Key('userId').eq(user['sub'])
    )
    texts = response['Items']
    return {"texts": texts}
