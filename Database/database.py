# import psycopg2
from sqlalchemy.orm import sessionmaker

from config import *
from sqlalchemy import create_engine


engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
Session = sessionmaker(bind=engine)
session = Session()


