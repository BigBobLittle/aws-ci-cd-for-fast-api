import boto3

client = boto3.client('cognito-idp')

response = client.create_user_pool(
    PoolName='MyUserPool',
    AutoVerifiedAttributes=['email'],
    Policies={
        'PasswordPolicy': {
            'MinimumLength': 8,
            'RequireUppercase': True,
            'RequireLowercase': True,
            'RequireNumbers': True,
            'RequireSymbols': True
        }
    },
    UsernameAttributes=['email']
)

user_pool_id = response['UserPool']['Id']
