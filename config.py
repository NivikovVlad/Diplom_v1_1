import os
from dotenv import load_dotenv


load_dotenv()


token = os.getenv('TOKEN')
host = os.getenv('HOST')
user = os.getenv('USER')
password = os.getenv('PASSWORD')
database = os.getenv('DB_NAME')
port = os.getenv('PORT')