# pip install boto3 # Instalar en terminal esta libreria
# pip install python-dotenv # Instalar. 

# Las claves tienen que estar en un documento sin nombre .env y ternerlo .gitignore para que no se hagan publicas las claves de AWS. Este fichero lo creo yo con los compañeros. Tiene que estar en la misma carperta que este código.
import os
from dotenv import load_dotenv
import boto3


load_dotenv()
AWS_SERVER_PUBLIC_KEY = os.getenv('AWS_SERVER_PUBLIC_KEY')
AWS_SERVER_SECRET_KEY = os.getenv('AWS_SERVER_SECRET_KEY')


session = boto3.Session(
    aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
    aws_secret_access_key=AWS_SERVER_SECRET_KEY,
)
s3 = session.resource('s3')


obj = s3.Object(bucket_name='proyectotfm', key='caracteristicas_palas_padel.json')
response = obj.get()
df_caracteristicas = response['Body'].read()

print(df_caracteristicas)

