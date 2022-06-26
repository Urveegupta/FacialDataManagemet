import pytest
from main import app
import main
from asgi_lifespan import LifespanManager
from connect_database import faces,engine,database
from httpx import AsyncClient
import face_recognition

@pytest.mark.order(4)
@pytest.mark.asyncio
async def test_getinfo():
    async with LifespanManager(app):
        async with AsyncClient(app=app,base_url="http://0.0.0.0/") as client:

            # test case 1 => correct face id

            responsetemp = await client.post("/add_face/",      data = {
                                                                      "name":"for_id_check_name",
                                                                      "location": None
                                                                   },
                                                                   files = {"file": open("./test/for_id_check.png","rb")}
            )
            newid = int(responsetemp.json()["id"])

            ## TEST STARTING HERE
            response = await client.post("/get_face_info/",data = {
                                                                      "api_key":"1234",
                                                                      "face_id": newid
                                                                   }
            )
            #assert response == face_info
            json = response.json()
            assert json["name"]=="for_id_check_name"

            # test case 2 => incorrect face id
            response = await client.post("/get_face_info/",data = {
                                                                      "api_key":"1234",
                                                                      "face_id": 10000000
                                                                   }
            )
            json = response.json()
            assert json == { "status": "ERROR",
                             "body": "give face id does not exist"
                           }

            # test case 3 => incorrect api key
            response = await client.post("/get_face_info/",data = {
                                                                      "api_key":"1111",
                                                                      "face_id": 34
                                                                   }
            )
            json = response.json()
            assert json == { "status": "ERROR",
                             "body": "invalid api key"
                           }

@pytest.mark.order(3)
@pytest.mark.asyncio
async def test_search():
    async with LifespanManager(app):
        async with AsyncClient(app=app,base_url="http://0.0.0.0/") as client:

            # test case 1 => contains one or multiple faces
            response = await client.post("/search_faces/",  data = {
                                                                      "k":3,
                                                                      "strictness": 66.67
                                                                   },
                                                                   files = {"file": open("./test/tom_zendaya.jpg","rb")}
            )
            json = response.json()
           
            assert json == {
                              "face 1": [
                                    {
                                      "name": "zendaya",
                                      "version": "1",
                                      "location": None,
                                      "date": None
                                    },
                                    {
                                      "additional info": "only 1 matches found within strictness limit"
                                    }
                                  ],
                                  "face 2": [
                                    {
                                      "name": "tom_holland",
                                      "version": "1",
                                      "location": None,
                                      "date": None
                                    },
                                    {
                                      "additional info": "only 1 matches found within strictness limit"
                                    }
                                  ]
                            }

            # test case 2 => contains no face
            response = await client.post("/search_faces/",  data = {
                                                                      "k":3,
                                                                      "strictness": 90
                                                                   },
                                                                   files = {"file": open("./test/no_face.png","rb")}
            )
            json = response.json()
           
            assert json == {"Status":"Error","Body":"No face found in uploaded image"}


@pytest.mark.order(2)
@pytest.mark.asyncio
async def test_uploadone():
    async with LifespanManager(app):
        async with AsyncClient(app=app,base_url="http://0.0.0.0/") as client:

            # test case 1 => image with one face
            response = await client.post("/add_face/",      data = {
                                                                      "name":"test_name1",
                                                                      "location": None
                                                                   },
                                                                   files = {"file": open("./test/addonetest_johnk.png","rb")}
            )
            json = response.json()
            assert json["Body"] == "Face added"

            #test case 2 => multiple faces in image
            response = await client.post("/add_face/",data = {
                                                                      "name":"test_name2",
                                                                      "location": None
                                                                   },
                                                                   files = {"file": open("./test/addonetest_multiple.png","rb")}
            )
            json = response.json()
            assert json["Body"] =="Please upload images with a single face"

            #test case 2 => no faces in image
            response = await client.post("/add_face/",data = {
                                                                      "name":"test_name3",
                                                                      "location": None
                                                                   },
                                                                   files = {"file": open("./test/no_face.png","rb")}
            )
            json = response.json()
            assert json["Body"] =="No face found in the image"

           

@pytest.mark.order(1)
@pytest.mark.asyncio
async def test_uploadbulk():
    async with LifespanManager(app):
        async with AsyncClient(app=app,base_url="http://0.0.0.0/") as client:

            # test case 1 => tgz compressed file
            response = await client.post("/add_faces_in_bulk/",files = {
                                                                      "file":open("./test/testtar.tar","rb")
                                                                   }
            )
            json = response.json()
            assert json == {"status": "OK",
                            "body": "2 entries added to database"
                            }

            # test case 1 => zip compressed file
            response = await client.post("/add_faces_in_bulk/",files = {
                                                                      "file":open("./test/testzip.zip","rb")
                                                                   }
            )
            json = response.json()
            assert json == {"status": "OK",
                            "body": "2 entries added to database"
                            }



@pytest.mark.order(5)
@pytest.mark.asyncio
async def test_cleanup():
    async with LifespanManager(app):
        async with AsyncClient(app=app,base_url="http://0.0.0.0/") as client:

          response = await client.get("/cleanup")
          json = response.json()
          assert json["Status"] == "OK"

