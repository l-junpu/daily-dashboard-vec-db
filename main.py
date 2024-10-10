import chromadb
chroma_client = chromadb.HttpClient(host='localhost', port=8000)

# chroma_client.delete_collection("my_collection")

# switch `create_collection` to `get_or_create_collection` to avoid creating a new collection every time
collection = chroma_client.get_or_create_collection(name="my_collection")

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

results = collection.query(
    query_texts=["This is a query document about florida"], # Chroma will embed this for you
    n_results=2, # how many results to return
    where={"tag": {"$in": ["vrlink"]}}
)

print(results)