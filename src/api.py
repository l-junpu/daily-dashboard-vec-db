import os
from threading import Thread, Event
from flask import Flask, jsonify, request
from flask_cors import CORS

from src.files.handler import save_files

class ApiHandler:
    def __init__(self, name, rootDir):
        # Init
        self.app = Flask(name)
        self.app.config["UPLOAD_FOLDER"] = os.path.join(rootDir, "uploads", "users")
        self.app.config["EMBEDDED_FOLDER"] = os.path.join(rootDir, "uploads", "embedded-documents")
        
        # Enable CORS
        CORS(self.app)

        # Register API Requests
        self.app.add_url_rule("/database/api/upload-files/", methods=["POST"], view_func=self.receive_uploaded_files)
    

    def receive_uploaded_files(self):
        # Check if we have all details
        if "files[]" not in request.files or "username" not in request.form or "tag" not in request.form:
            return jsonify({"error": "Missing form data"}), 400

        # Start a thread to run our handler on its own
        saveEvent = Event()
        thread = Thread(target=self.process_uploaded_files, 
                        args=(request.form.get("username"), 
                              request.form.get("tag"), 
                              request.files.getlist("files[]"),
                              saveEvent)
                        )
        thread.start()
        saveEvent.wait()


        # Return immediately so other Users can send an Upload Request
        return jsonify({'message': 'Data received'}), 201
    

    def process_uploaded_files(self, username, tag, files, saveEvent):
        print("Files: ", files)
        print("Username: ", username)
        print("Tag: ", tag)

        print("Saving files...")
        save_files(username, self.app.config["UPLOAD_FOLDER"], files)
        saveEvent.set()

        print("Chunking files...")
        # fn here

        print("Embedding files...")
        # fn here
    

    def run(self):
        self.app.run(debug=True)