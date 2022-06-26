import sqlalchemy
import databases
import json


filePTR = open('config.json')
config = json.load(filePTR)
URL = config['url']

filePTR.close()
metadata = sqlalchemy.MetaData()
database = databases.Database(URL)
engine = sqlalchemy.create_engine(URL)
connection = engine.connect()

# Table
faces = sqlalchemy.Table(
    "faces",
    metadata,
    sqlalchemy.Column("id" , sqlalchemy.Integer , primary_key=True,autoincrement=True) ,
    sqlalchemy.Column("name" , sqlalchemy.String(500)) ,
    sqlalchemy.Column("data" , sqlalchemy.ARRAY(sqlalchemy.Float)) ,
    sqlalchemy.Column("version", sqlalchemy.String(500)),
    sqlalchemy.Column("location" , sqlalchemy.String(500)) ,
    sqlalchemy.Column("date" , sqlalchemy.DateTime())
)

# Adds Schema into table if doest exist
metadata.create_all(engine)