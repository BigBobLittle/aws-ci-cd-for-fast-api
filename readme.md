
> uvicorn api.main:app --reload 

## manual deployment

> pip3 install -t dependencies -r requirements.txt
> pip3 install -r requirements.txt --platform manylinux2014_x86_64 --target dependencies --only-binary=:all:

> (cd dependencies; zip ../aws_lambda_artifact.zip -r .)

single file 
> zip aws_lambda_artifact.zip -u main.py  

folder and subdirectories 

> zip -r aws_lambda_artifact.zip app/*


## other alternatives 

> cd fastapi-venv/lib/python3.11/site-packages 

> zip -r9 ../../../../functions.zip .

> cd ../../../../

> zip -g ./functions.zip -r app


export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export COGNITO_POOL_ID=
