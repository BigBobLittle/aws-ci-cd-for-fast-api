import os 
import boto3
from datetime import datetime, timedelta
import uuid
from decimal import Decimal

class DynamoDBManager:
    def __init__(self):
            # Create a DynamoDB resource
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=os.environ.get('COGNITO_REGION'),
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_KEY')
            )

            # Get or create the DynamoDB table for items
            self.table_name = 'items_table_one'
            self.table = self.get_or_create_table(
                self.table_name,
                
                key_schema=[
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'}, 
                    {'AttributeName': 'text', 'KeyType': 'RANGE'},
                   
                ],
                attribute_definitions=[
                    {'AttributeName': 'user_id', 'AttributeType': 'S'}, 
                    {'AttributeName': 'text', 'AttributeType': 'S'},
                     {'AttributeName': 'created_at', 'AttributeType': 'N'}, 
                    {'AttributeName': 'updated_at', 'AttributeType': 'N'}
                ],
                
            )

            # Get or create the DynamoDB table for user sessions
            self.session_table_name = 'user_sessions'
            self.session_table = self.get_or_create_table(
                self.session_table_name,
                key_schema=[
                    {'AttributeName': 'session_id', 'KeyType': 'HASH'}
                ],
                attribute_definitions=[
                    {'AttributeName': 'session_id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    {'AttributeName': 'login_time', 'AttributeType': 'N'}
                ]
            )



    def get_or_create_table(self, table_name, key_schema, attribute_definitions):
        # Check if the table already exists
        existing_tables = self.dynamodb.tables.all()
        for table in existing_tables:
            if table.name == table_name:
                return table

       
        # Define the table schema
        table_schema = {
            'TableName': table_name,
            'KeySchema': key_schema,
            'AttributeDefinitions': attribute_definitions,
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,  
                'WriteCapacityUnits': 5  
            }
        }

        # Create the DynamoDB table
        return self.dynamodb.create_table(**table_schema)

    def create_session(self, user_id):
        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        # Record the login time
        # login_time = datetime.now().timestamp()
        login_time = Decimal(str(datetime.now().timestamp()))
        print('session id', session_id, "userId", user_id, "login time", login_time)

        # Save session information in DynamoDB
        session = self.session_table.put_item(
            Item={
                'session_id': session_id,
                'user_id': user_id,
                'login_time': login_time,
                'text': "not_needed"
            }
        )

        # print('session', session)
        return session_id

    def is_session_valid(self, session_id):
        # Get session information from DynamoDB
        response = self.session_table.get_item(Key={'session_id': session_id})
        if 'Item' in response:
            login_time = response['Item'].get('login_time')
            # Check if login time is within the timeout period (3 minutes)
            # if login_time and datetime.now().timestamp() - login_time < 180:
            if login_time and Decimal(str(datetime.now().timestamp())) - Decimal(str(login_time)) < Decimal('180'):
                return True
            else:
                # Delete session if timeout exceeds or if login time is missing
                self.session_table.delete_item(Key={'session_id': session_id})
                return False
        else:
            return False
