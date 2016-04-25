import unittest
import os
import shutil
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Py2 compatibility
from io import StringIO

import sys; print(list(sys.modules.keys()))
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())

    def test_get_no_songs(self):
        """Getting songs from an empty database """
        response = self.client.get("/api/songs", headers=[("Accept", "application/json")])
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data,[])

    def test_get_songs(self):
        """ Getting songs from a populated database """
        fileA=models.File(name="Shady_Grove.mp3")
        #songA = models.Song(file_id=fileA.id) gave this error sqlalchemy.exc.IntegrityError: 
        #(psycopg2.IntegrityError) null value in column "file_id" violates not-null constraint
        #DETAIL:  Failing row contains (1, null).
        #[SQL: 'INSERT INTO songs (file_id) VALUES (%(file_id)s) RETURNING songs.id'] [parameters: {'file_id': None}]
        
        songA=models.Song(filename=fileA)
        session.add_all([songA,fileA])
        session.commit()
        
        
        response = self.client.get("/api/songs", headers=[("Accept", "application/json")]) 
        
        #Was request to endpoint successful?
        self.assertEqual(response.status_code, 200)
        #Was the response a JSON object
        self.assertEqual(response.mimetype, "application/json")
        
        #decode data 
        data = json.loads(response.data.decode("ascii"))
        #check to see if it is only one song in data
        self.assertEqual(len(data),1)
        
        songA=data[0]
        self.assertEqual(fileA.name, "Shady_Grove.mp3")
        self.assertEqual(songA["id"], 1)
        

#Traceback (most recent call last):
  #File "/home/ubuntu/workspace/tuneful/tests/api_tests.py", line 67, in test_get_songs
   # self.assertEqual(fileA["name"], "Shady_Grove.mp3")
#TypeError: 'File' object is not subscriptable

    def test_post_song(self):
        """Testing post songs endpoint"""
        
        file=models.File(name="Shady_Grove.mp3")
        session.add(file)
        session.commit()
        
        data = {
            "file": {
                "id":1
                  }
                }

        #Check request to endpoint is succesful
        response = self.client.post("/api/songs",data=json.dumps(data),
        content_type="application/json",headers=[("Accept", "application/json")]
        )
        
    
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        
        self.assertEqual(urlparse(response.headers.get("Location")).path,"/api/songs")
        
        data=json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"],1)
        self.assertEqual(file.name,"Shady_Grove.mp3" )
        #song=models.Song(filename=file)
        
        
    def test_put_song(self):
        file=models.File(name="Shady_Grove.mp3")
        session.add(file)
        session.commit()
        
        data = {
                "name":"gees.mp3"
                    }
            

        #Check request to endpoint is succesful
        response = self.client.put("/api/songs/{}".format(file.id),data=json.dumps(data),
        content_type="application/json",headers=[("Accept", "application/json")]
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        
        self.assertEqual(urlparse(response.headers.get("Location")).path,"/api/songs/{}".format(file.id))
        
        


    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())


