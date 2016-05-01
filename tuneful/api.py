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
    
@app.route("/api/songs/<int:id>", methods=["GET"])
@decorators.accept("application/json")
def song_get(id):
    """ Single song endpoint """
    #Get the post from the database
    song = session.query(models.Song).get(id)
    
    #Check whether the song exists
    #if not return a 404 with a helpful message
    if not song:
        message = "Could not find song with id {}". format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")
        
    #Return the song as JSON
    data = json.dumps(song.as_dictionary())
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
def songs_put(id):
    """edit existing song"""
    data=request.json
    
    file=session.query(models.File).get(id)
    file.name=data["file"]["name"]
    file.id=id
   
    session.add(file)
    session.commit()
    
    
    #Return a 201 Created, containing the post as JSON and with the 
    #Location header set to the location of the post
    data=json.dumps(file.as_dictionary())
    headers={"Location": url_for("song_get", id=file.id)} 
    return Response(data, 201, headers=headers, mimetype="application/json")
    
    
@app.route("/api/songs/<int:id>", methods=["DELETE"])
@decorators.accept("application/json")
@decorators.require("application/json")
def songs_delete(id):
    """delete existing song"""
    
    file = session.query(models.File).get(id)

    # delete file
    session.delete(file)
    session.commit()
    print(file)
    
    return Response('', 204)
    
    
@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)
    
    
@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
@decorators.accept("application/json")
def file_post():
    file=request.files.get("file")
    if not file:
        data =  {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")
        
    filename = secure_filename(file.filename)
    db_file = models.File(name=filename)
    session.add(db_file)
    session.commit()
    file.save(upload_path(filename))
    
    
    data= db_file.as_dictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")
