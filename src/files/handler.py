import os
import shutil
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


def shift_file(username, filename, oldDirectory, newDirectory):
    # Create a new directory if it doesn't exist yet,
    # and shift the files over
    oldDirectory = os.path.join(oldDirectory, username)
    newDirectory = os.path.join(newDirectory, username)
    os.makedirs(newDirectory, exist_ok=True)
    
    # Remove old file with same name if exists
    newDirectoryFile = os.path.join(newDirectory, filename)
    if os.path.exists(newDirectoryFile):
        os.remove(newDirectoryFile)

    # Move the file over
    shutil.move(os.path.join(oldDirectory, filename),
                newDirectory)