import os
from werkzeug.utils import secure_filename

def create_upload_directory(username, uploadDir):
    # Merge directory paths
    uploadDir = os.path.join(uploadDir, username)
    # Create if directory does not exist
    os.makedirs(uploadDir, exist_ok=True)


def move_embedded_files(tag, completedFolderPath, embeddedFilePath):
    # Merge directory paths
    permDir = os.path.join(completedFolderPath, tag)
    # Create if directory does not exist
    os.makedirs(permDir, exist_ok=True)

    # Perform movement tasks - to be called by embedder


def save_files(username, uploadDir, files):
    # Create Upload Directory for User
    create_upload_directory(username, uploadDir)
    
    for file in files:
        if file.filename == "":
            continue
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(uploadDir, username, filename))