import os
from pathlib import Path
from typing import List
from pypdf import PdfReader
from docx2python import docx2python
from mattsollamatools import chunker

"""
    Define a Chunk class containing data required to create a
    single Embedding
"""
class Chunk:
    def __init__(self, contents: str, source: str, tag: str, uid: str):
        self.contents = contents
        self.source = source
        self.tag = tag
        self.uid = uid


"""
    Define a Chunker class to perform the actual Chunking of data,
    returning a list of Chunks when passed a document path
"""
class Chunker:
    def __init__(self, chunkSize: int, minWords: int = 20):
        self.chunkSize = chunkSize
        self.minWords = minWords
        pass


    def ChunkDocument(self, documentPath: str, tag: str) -> List[Chunk]:
        filename = Path(documentPath).name
        contents = self.ReadDocumentContents(documentPath)
        if len(contents) <= self.minWords: return []
        chunks = chunker(contents, max_words_per_chunk = self.chunkSize)
        return [Chunk(contents=chunk, 
                      source=filename, 
                      tag=tag, 
                      uid=f"{filename}_{i}") 
                      for i, chunk in enumerate(chunks)]
    
    
    def ReadDocumentContents(self, documentPath: str):
        ext = Path(documentPath).suffix
        contents = ""

        match ext:
            case ".txt":
                with open(documentPath, "r") as file:
                    contents = file.read
            case ".pdf":
                reader = PdfReader(documentPath)
                for i in range(len(reader.pages)):
                    page = reader.pages[i]
                    contents += page.extract_text() + "\n"
            case ".docx":
                doc = docx2python(documentPath)
                contents = doc.text
        
        return contents