import os
from pathlib import Path
from typing import List, Optional
from pypdf import PdfReader
from docx2python import docx2python

# Splitter
from langchain_core.documents import Document
from langchain.text_splitter import (Language, RecursiveCharacterTextSplitter)

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
    def __init__(self, chunkSize: int, chunkOverlap: int, minWords: int = 20):
        self.chunkSize = chunkSize
        self.chunkOverlap = chunkOverlap
        self.minWords = minWords


    def ChunkDocument(self, documentPath: str, tag: str) -> List[Chunk]:
        filename = Path(documentPath).name
        contents = self.ReadDocumentContents(documentPath)
        if len(contents) <= self.minWords: return []
        chunks = self.RecurisveSplitter(contents)
        return [Chunk(contents=chunk.page_content, 
                      source=filename, 
                      tag=tag, 
                      uid=f"{filename}_{i}") 
                      for i, chunk in enumerate(chunks)]
    

    def RecurisveSplitter(self, contents: str, programmingLanguage: Optional[Language] = None) -> List[Document]:
        separators = ["\n\n", "\n", " ", ""]
        if programmingLanguage is not None:
            try:
                separators = RecursiveCharacterTextSplitter.get_separators_for_language(
                    programmingLanguage
                )
            except (NameError, ValueError) as e:
                print(f"No separators found for language {programmingLanguage}. Using defaults.")

        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base", # Tokenization scheme used by OpenAI
            chunk_size=self.chunkSize,
            chunk_overlap=self.chunkOverlap,
            separators=separators)

        return splitter.split_documents( [Document(page_content=contents)] )
    
    
    def ReadDocumentContents(self, documentPath: str):
        ext = Path(documentPath).suffix
        contents = ""

        match ext:
            case ".txt":
                with open(documentPath, "r") as file:
                    contents = file.read()
            case ".pdf":
                reader = PdfReader(documentPath)
                for i in range(len(reader.pages)):
                    page = reader.pages[i]
                    contents += page.extract_text() + "\n"
            case ".docx":
                doc = docx2python(documentPath)
                contents = doc.text
        return contents