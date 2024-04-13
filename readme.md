
> uvicorn api.main:app --reload 

## manual deployment

> pip3 install -t dependencies -r requirements.txt


> (cd dependencies; zip ../aws_lambda_artifact.zip -r .)

single file 
> zip aws_lambda_artifact.zip -u main.py  

folder and subdirectories 

> zip -r aws_lambda_artifact.zip api/*
