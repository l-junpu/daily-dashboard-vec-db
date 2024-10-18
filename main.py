# import chromadb
# chroma_client = chromadb.HttpClient(host='localhost', port=8000)

# # switch `create_collection` to `get_or_create_collection` to avoid creating a new collection every time
# collection = chroma_client.get_or_create_collection(name="my_collection")

# # switch `add` to `upsert` to avoid adding the same documents every time
# collection.upsert(
#     documents=[
#         "This is a document about pineapple",
#         "This is a document about nuggets",
#         "This is a document about oranges"
#     ],
#     metadatas=[{"source": "me", "tag": "vrforce"}, {"source": "me", "tag": "vrforce"}, {"source": "me", "tag": "vrlink"}],
#     ids=["id1", "id2", "id3"]
# )

# # Test deletion of tagged documents only
# #collection.delete(where={"tag": {"$eq": "vrforce"}})

# results = collection.query(
#     query_texts=["This is a query document about florida"], # Chroma will embed this for you
#     n_results=2, # how many results to return
#     where={"tag": {"$eq": "vrforce"}}
# )

# print(results)

from flask import Flask, request, jsonify
from flask_cors import CORS

# Create an instance of Flask and enable CORS
app = Flask(__name__)
CORS(app)

@app.route("/database/api/upload-files/", methods=["POST"])
def ReceiveUploadedFiles():
    print("Received shit")
    if 'files[]' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    files = request.files.getlist('files[]')
    print(files)

    return jsonify({'message': 'Data received'}), 201

if __name__ == "__main__":
    app.run(debug=True)