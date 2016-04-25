import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from tuneful import app
from .database import session
from .utils import upload_path


@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
    """ Get a list of songs """
    
    #Get the songs from the database
    songs=session.query(models.Song).order_by(models.Song.id)
    
    #Convert the songs to JSON and return a response
    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application/json")
    
@app.route("/api/songs", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def songs_post():
    """Add a new song"""
    data=request.json
    
    #Add the song to the database
    
    file=models.File(name="name")
    song=models.Song(filename=file)
    session.add_all([song,file])
    session.commit()
    
    
    #Return a 201 Created, containing the post as JSON and with the 
    #Location header set to the location of the post
    data=json.dumps(song.as_dictionary())
    headers={"Location": url_for("songs_get", id=song.id)} #why songs_get and not song_get
    return Response(data, 201, headers=headers, mimetype="application/json")
    

@app.route("/api/songs/<int:id>", methods=["PUT"])
@decorators.accept("application/json")
@decorators.require("application/json")
def songs_put():
    """edit existing song"""
    data=request.json
    
    
    file=session.query(models.File).get(id)
    file.name=data["name"]
    file.id=id
    
    session.add(file)
    session.commit()
    
    
    #Return a 201 Created, containing the post as JSON and with the 
    #Location header set to the location of the post
    data=json.dumps(file.as_dictionary())
    headers={"Location": url_for("songs_get", id=file.id)} 
    return Response(data, 201, headers=headers, mimetype="application/json")
    
    
    
    
    
    
