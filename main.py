import uvicorn
import numpy as np
import database_operations
from connect_database import database,connection
from fastapi import FastAPI, File, UploadFile, Form
from file_operations import Extract, Uploadfile

app = FastAPI()

global faceset,nameset,meta_data
faceset= [] # stores encodings
nameset= {} # stores names
meta_data = [] # meta data (id,name,version,location,date)

@app.on_event("startup")
async def startup():
    global faceset
    global nameset
    global meta_data
    await database.connect()
    print("connected")
    
    # maintain lists
    
    cache = connection.execute("select * from faces").fetchall()
    print("cache size: "+ str(len(cache)))
    faceset = [np.array(row[2]) for row in cache]

    print("faceset size: "+ str(len(faceset)))
    meta_data = [{
            'id': row[0],
            'name': row[1],
            'version': row[3],
            'location': row[4],
            'date': row[5]
        } for row in cache]
    nameset = set(i['name'] for i in meta_data)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/search_faces/")
async def search_faces(k: int = Form(..., description="Number of best matches to provide (within strictness range)"),
                       strictness: float = Form(..., description="Can range from 0-100. Ideal value = 66.67"),
                       file: UploadFile = File(..., description="An image file, possible containing multiple human faces.")):
    

    uploadObj = Uploadfile(file,'./uploads/find')
    uploadObj.uploadfiles()
    
    global faceset,meta_data
    filepath = './uploads/find/'+ str(file.filename)
    res = database_operations.find_k_matches(int(k),strictness,filepath,faceset,meta_data)

    return res


@app.post("/add_face/")
async def add_face(name: str = Form(...),
                   location: str = Form(None ),
                   file: UploadFile = File(..., description="An image file having a single human face.")):
   
   # upload file locally
   uploadObj = Uploadfile(file,'./uploads/single')
   uploadObj.uploadfiles()

   global faceset,nameset,meta_data
   
   filepath = './uploads/single/'+ str(file.filename)
   
   # check and add to database
   res = database_operations.add_single_face(name,location,filepath,faceset,meta_data,nameset)

   return res


@app.post("/add_faces_in_bulk/")
async def add_faces_in_bulk(file: UploadFile = File(..., description="A ZIP file containing multiple face images.")):
   
   filename = file.filename

   # upload file
   UPLOAD_DIR = "./uploads/bulk"
   uploadObj = Uploadfile(file,UPLOAD_DIR)
   uploadObj.uploadfiles()
   
   # extract data in this format directory
   DATA_DIR = "./uploads/bulk/_"+filename

   # extracted on local pc
   extractObj = Extract(UPLOAD_DIR+"/"+filename,DATA_DIR)

   global faceset,nameset,meta_data
   # add to database
   changecount = database_operations.add_to_database_bulk(DATA_DIR,faceset,meta_data,nameset)

   return {"status": "OK", "body": f"{changecount} entries added to database"}


@app.post("/get_face_info/")
async def get_face_info(api_key: str = Form(...,description="A key for validation. Here = 1234"), 
                        face_id: int = Form(...)):
   
   # check auth key
   if api_key != "1234":
       # invalid auth key
       return {"status": "ERROR", "body": "invalid api key"}

   # checking id in meta_data (contains all database info)
   global meta_data
   
   # to store the result
   face_info = []

   query = await database.fetch_one("select * from faces where id = :id",{"id":face_id})
#    for d in meta_data:
#        if d["id"]== face_id:
#            face_info = database_operations.without_ids(d)
#            break

   if query:
       return query

   # given id not present in database
   return{"status":"ERROR","body":"give face id does not exist"}


@app.get("/cleanup")
async def clean_testdata():

    res = await database.execute("delete from faces where id > 13000")
    return {"Status":"OK"}

if __name__ == "__main__":
    uvicorn.run('main:app',host="127.0.0.1",port = 8000,reload=True)