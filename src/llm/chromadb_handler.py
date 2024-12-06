import os
import nltk
import chromadb
from typing import List
from src.llm.chunker import Chunker
from src.llm.embedding_func import CustomSentenceTransformerEmbeddingFunction

class ChromaDBHandler:
    def __init__(self, host, port, collectionName):
        self.client = chromadb.HttpClient(host=host, port=port)
        self.chunker = Chunker(chunkSize=100, chunkOverlap=15)
        
        self.custom_ef = CustomSentenceTransformerEmbeddingFunction( self.GetModelDirectory() )
        self.collection = self.client.get_or_create_collection(name=collectionName, embedding_function=self.custom_ef)
    

    def EmbedDocument(self, requester: str, tag: str, directory: str):
        chunks = self.chunker.ChunkDocument(directory, tag)
        if len(chunks) == 0: return False
        self.collection.upsert(documents=[chunk.contents for chunk in chunks],
                                ids=[chunk.uid for chunk in chunks],
                                metadatas=[{'source': c.source, 'tag': c.tag, 'requester': requester} for c in chunks])
        return True
    
    def retrieve_tags_and_docs(self):
        metadata = self.collection.get()["metadatas"];

        docs = []
        tags = []
        user = []
        for d in metadata:
            if d["tag"] not in tags: tags.append(d["tag"])
            if d["source"] not in docs: docs.append(d["source"])
            if d["requester"] not in user: user.append(d["requester"])
        
        return tags, docs, user

    
    def Filter(self, tags: list[str], users: list[str], page: int, rows: int):
        # Apply our filter based on tags / users
        filter = {}
        if len(tags) > 0 and len(users) > 0:
            filter = {
                "$and": [
                    {"tag": {"$in": tags}},
                    {"requester": {"$in": users}}
                ]
            }
        elif len(tags) > 0:
            filter = {"tag": {"$in": tags}}
        elif len(users) > 0:
            filter = {"requester": {"$in": users}}

        print(filter)

        # If there is a valid filter, apply it
        metadatas = []
        if filter != {}:
            metadatas = self.collection.get(limit=None, where=filter)["metadatas"]
        # Else we just query all
        else:
            metadatas = self.collection.get(limit=None)["metadatas"]
        
        # Retrieve all unique document names
        sources = []
        for md in metadatas:
            if not any(source["source"] == md["source"] for source in sources):
                sources.append({ "source": md["source"],
                                 "tag": md["tag"],
                                 "user": md["requester"],
                                 "date": "TBD" })

        # Filter "row" elements per page, and also returns the max number of pages for this filter
        return sources[page*rows : (page+1)*rows], len(sources) // rows


    def UpdateTag(self, previousTag: str, newTag: str):
        pass


    def DeleteTags(self, tags: list[str]):
        self.collection.delete(where={"tag": {"$in": tags}})


    def DeleteDocument(self, documentSource: str):
        self.collection.delete(where={"source": {"$eq": documentSource}})


    # Our models path is located in src/models/
    def GetModelDirectory(self):
        current_path = os.path.abspath(__file__)
        current_path = os.path.dirname(current_path)
        model_directory = os.path.join(current_path, '../all-mpnet-base-v2/')
        return model_directory
    

if __name__ == "__main__":
    chromadb = ChromaDBHandler(host="localhost", port=8000, collectionName="vectordb")
    f = chromadb.Filter([], [], 0, 10)
    print(f)
