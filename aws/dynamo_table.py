import boto3

client = boto3.client('dynamodb')

response = client.create_table(
    TableName='TextsTable',
    KeySchema=[
        {
            'AttributeName': 'userId',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'timestamp',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'userId',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'timestamp',
            'AttributeType': 'N'
        }
    ],
    BillingMode='PAY_PER_REQUEST'
)

table_name = 'TextsTable'
