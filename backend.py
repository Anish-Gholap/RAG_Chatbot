import os
import uuid
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from pydantic_utils import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest
from database  import get_chat_history, insert_chat_logs, insert_document_record, delete_document_record, get_all_documents
from langchain_utils import get_rag_chain
from chroma_utils import index_documents_to_chroma

""""
API EndPoints

/chat: Chat with llm and get back answer. Takes question, session id and model to use.
Returns answer, session id and model name for database storage
If no session id server should return a session id for the new chat

/upload_doc: Uploads and indexes document into vector db. Return id

/list_doc: List all documents in vector db. Return id, filename, and timestamp of upload

/delete_doc: Delete document from vector db
"""

router = APIRouter(
  prefix="/chatbot",
  tags=["chatbot"]
)

# /chat
@router.post("/chat")
async def get_llm_response(query: QueryInput):
  """
  1. If no session_id, create one
  2. Get chat history from db using session id
  3. Get rag_chain and invoke using question and chathistory
  4. Store into chat history db
  5. return the session_id, answer and model  
  """
  
  if not query.session_id:
    session_id = str(uuid.uuid4())
  else:
    session_id = query.session_id

  chat_history = get_chat_history(session_id=session_id)
  
  rag_chain = get_rag_chain(model=query.model.value)
  
  answer = rag_chain.invoke({"input": query.question, "chat_history": chat_history})["answer"]
  
  insert_chat_logs(
    session_id=session_id,
    user_query=query.question,
    llm_response=answer,
    model=query.model.value
  )
  
  return QueryResponse(
    answer=answer,
    session_id=session_id,
    model=query.model
  )


# /upload_doc 
@router.post("/upload-doc")
async def upload_and_index_document(file: UploadFile = File(...)):
  """
  1. Check if doc type is allowed
  2. Save incoming file stream into temp file
  3. Index and save to Vector Db
  4. Remove temp file and return saved file id
  """
  
  allowed_extensions = ['.pdf', '.docx', '.html']
  file_extension = os.path.splitext(file.filename)[1].lower()
  
  if file_extension not in allowed_extensions:
    raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}")
  
  temp_file_path = f"temp_{file.filename}"
  
  try:
    with open(temp_file_path, 'wb') as f:
      shutil.copyfileobj(file.file, f)
      
    file_id = insert_document_record(file.filename)
    success = index_documents_to_chroma(temp_file_path, file_id)
    
    if success:
      return {"message": f"File {file.filename} has been successfully uploaded and indexed.", "file_id": file_id}
    else:
      delete_document_record(file_id)
      raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")
  
  finally:
    if os.path.exists(temp_file_path):
      os.remove(temp_file_path)
      
      
# /list-docs
@router.get("/list-docs", response_model=list[DocumentInfo])
async def list_documents():
  return get_all_documents()

# /delete-doc
@router.delete("/delete-doc")
async def delete_document(request: DeleteFileRequest):
  # Delete from Chroma Db
  chroma_delete = delete_document(request.file_id)
  
  if chroma_delete:
    # Delete from document store
    db_delete = delete_document_record(request.file_id)
    
    if db_delete:
      return {"message": f"Successfully deleted document with file_id {request.file_id} from the system."}
    else:
      return {"error": f"Deleted from Chroma but failed to delete document with file_id {request.file_id} from the database."}
    
  else:
    return {"error": f"Failed to delete document with file_id {request.file_id} from Chroma."}