from dotenv import load_dotenv
import os
load_dotenv()
from app import app

app.config['SQLALCHEMY_DATABASE_URI']=os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_TRACK']=os.getenv('SQLALCHEMY_DATABASE_TRACK')
app.config['SECRET_KEY']=os.getenv('SECRET_KEY')