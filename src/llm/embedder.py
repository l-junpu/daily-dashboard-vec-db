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


    def UpdateTag(self, previousTag: str, newTag: str):
        pass


    def DeleteTag(self, tag: str):
        pass


    def DeleteDocument(self, document: str):
        pass


    # Our models path is located in src/models/
    def GetModelDirectory(self):
        current_path = os.path.abspath(__file__)
        current_path = os.path.dirname(current_path)
        model_directory = os.path.join(current_path, '../all-mpnet-base-v2/')
        return model_directory