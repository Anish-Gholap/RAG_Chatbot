from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialise Text Splitter
text_splitter = RecursiveCharacterTextSplitter(
  chunk_size=1000,
  chunk_overlap=200,
  length_function=len
)

# Initialise Embedding Function
embedding_function = OpenAIEmbeddings()

# Intialiase Chroma Vector Db
vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)


"""
Indexing Documents: 
1. Load documents using document loaders
2. Split documents into chunks using text splitters
3. Embed and store chunks into vector store
"""

def load_and_split_documents(file_path: str) -> List[Document]:
  # Choose respective loader
  if file_path.endswith('.pdf'):
    document_loader = PyPDFLoader(file_path)
  
  elif file_path.endswith('.docx'):
    document_loader = Docx2txtLoader(file_path)
    
  elif file_path.endswith('.html'):
    document_loader = UnstructuredHTMLLoader(file_path)

  else:
    raise ValueError(f"Unsupported File Type: {file_path}")
  
  # Load documents
  documents = document_loader.load()
  
  # Split documents into chunks
  chunks = text_splitter.split_documents(documents)
  
  return chunks

def index_documents_to_chroma(file_path: str, file_id: int) -> bool:
  try:
    chunks = load_and_split_documents(file_path)
    
    # Add file_id to the metadata for each chunk
    for chunk in chunks:
      chunk.metadata['file_id'] = file_id
    
    # Add chunks to vector store
    vector_store.add_documents(chunks)    
    
    return True
  
  except Exception as e:
    print(f"Error indexing documents: {e}")
    return False
  
  
def delete_document(file_id: int):
  try:
    # Find document using file id
    docs = vector_store.get(where={'file_id': file_id})
    print(f"Found {len(docs['ids'])} document chunks for file id {file_id}")
    
    # Delete document
    vector_store._collection.delete(where={'file_id': file_id})
    print(f"Deleted all documents with file_id {file_id}")

    return True
  
  except Exception as e: 
    print(f"Error deleting document with file_id {file_id} from Chroma: {str(e)}")
    return False