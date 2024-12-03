from collections import defaultdict
import os
from threading import Thread, Event
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS, cross_origin

from src.llm.chromadb_handler import ChromaDBHandler
from src.files.handler import save_files, shift_file

class ApiHandler:
    def __init__(self, name, rootDir):
        # Init
        self.app = Flask(name)
        self.app.config["UPLOAD_FOLDER"] = os.path.join(rootDir, "uploads", "users")
        self.app.config["EMBEDDED_FOLDER"] = os.path.join(rootDir, "uploads", "embedded-documents")
        self.app.config["UNHANDLED_FOLDER"] = os.path.join(rootDir, "uploads", "unhandled-documents")
        self.chromadb = ChromaDBHandler(host="localhost", port=8000, collectionName="vectordb")

        self.user_sid = defaultdict(str)
        self.last_status = defaultdict(str)
        self.tags, self.docs, self.users = self.chromadb.retrieve_tags_and_docs()
        
        # Enable CORS
        CORS(self.app, origins=["http://localhost:5173"])

        # Register API Requests
        self.app.add_url_rule("/database/api/upload-files/", methods=["POST"], view_func=self.receive_uploaded_files)
        self.app.add_url_rule("/database/api/retrieve-relevant-docs/", methods=["POST"], view_func=self.retrieve_filtered_docs)
        self.app.add_url_rule("/database/api/retrieve-tags-and-docs/", methods=["GET"], view_func=self.retrieve_tags_and_docs)

        # Set up Socket Io
        self.socketio = SocketIO(self.app, cors_allowed_origins='*')
        self.socketio.on_event("connect", self.handle_connect)
        self.socketio.on_event("disconnect", self.handle_disconnect)


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
        return jsonify({'message': 'Data received'}), 200
    

    def process_uploaded_files(self, username, tag, files, saveEvent):
        # Save files locally
        self.emit_status_update(username, "Saving files...")
        save_files(username, self.app.config["UPLOAD_FOLDER"], files)
        self.emit_status_update(username, "Files have been successfully saved...")
        saveEvent.set()

        # Update username list if its a new uploader
        if username not in self.users: self.users.append(username)

        # Process each file
        uploadPath = os.path.join(self.app.config["UPLOAD_FOLDER"], username)
        savedFiles = os.listdir(uploadPath)
        for i, file in enumerate(savedFiles):
            self.emit_status_update(username, f"Processing file {i}/{len(savedFiles)}: {file}")
            success = self.chromadb.EmbedDocument(username, tag, os.path.join(uploadPath, file))
            if success:
                shift_file(username, file, self.app.config["UPLOAD_FOLDER"], self.app.config["EMBEDDED_FOLDER"])
                if tag not in self.tags: self.tags.append(tag)
                if file not in self.docs: self.docs.append(file)
            else:
                shift_file(username, file, self.app.config["UPLOAD_FOLDER"], self.app.config["UNHANDLED_FOLDER"])
            
        self.emit_status_update(username, "Completed processing")


    def retrieve_filtered_docs(self):
        req = request.get_json()
        sources, maxPages = self.chromadb.Filter(req['tags'], req['users'], req['page'], req['rows'])
        return jsonify({ 'sources': sources, 'maxPages': maxPages }), 200


    def retrieve_tags_and_docs(self):
        return jsonify({ 'tags': self.tags, 'docs': self.docs, 'users': self.users }), 200

    
    def handle_connect(self, auth):
        # If this fails, check our Frontend to ensure it sends the auth parameter
        if not auth or 'username' not in auth:
            return False
        # Tie our <username : sid>
        username = auth['username']
        self.user_sid[username] = request.sid
        emit('connected', {'status': self.last_status[username]}, room=request.sid)


    def handle_disconnect(self):
        # Remove <username : sid> item from mapping
        for username, sid in list(self.user_sid.items()):
            if sid == request.sid:
                del self.user_sid[username]
        emit('disconnected', {'status': 'Disconnected'}, room=request.sid)


    def emit_status_update(self, username, message):
        self.socketio.emit('status_update', {'status': message}, room=self.user_sid[username])
        self.last_status[username] = message
    

    def run(self):
        #self.app.run(debug=True)
        self.socketio.run(self.app, debug=True)