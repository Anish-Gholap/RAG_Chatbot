import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional


# Initialise firebase
cred = credentials.Certificate("ragchatbot-62811-firebase-adminsdk-fbsvc-ae41064583.json")
firebase_admin.initialize_app(cred)

# Initiliase firebase db client
db = firestore.client()

# Define the input log model
class ChatLog(BaseModel):
  session_id: str
  user_query: str
  llm_response: str
  model: str
  created_at: Optional[datetime] = None
  
  # To allow the use of firebase timestamps
  class Config:
    arbitrary_types_allowed = True
    
  @field_validator('session_id')
  def session_id_not_empty(cls, v):
    if not v or not v.strip():
      raise ValueError('session id cannot be empty')
    return v
  
  # Convert Log from Pydantic Model to dict for saving in firebase
  def to_dict(self):
    data = self.model_dump(exclude_none=True)
    
    # Add the firebase time stamp
    data["created_at"] = firestore.SERVER_TIMESTAMP
    
    return data


# Add the chat history to db collection
def insert_chat_logs(session_id, user_query, llm_response, model):
  try:
    log_entry = ChatLog(
      session_id=session_id,
      user_query=user_query,
      llm_response=llm_response,
      model=model,
    ).to_dict()
    
    # reference to chat_logs collection
    logs_ref = db.collection('chat_logs')
    
    # add to collection 'chat_logs
    logs_ref.add(log_entry)
    
  except ValueError as e:
    print(f"Validation error: {e}")
    
# Get chat history from db collection
def get_chat_history(session_id):
  # Query the collection by session id in the order of timestamps
  logs_ref = db.collection('chat_logs')
  query = logs_ref.where('session_id', '==', session_id).order_by('created_at')
  
  messages = []
  for doc in query.stream():
    data = doc.to_dict()
    
    # chat history format Human Message and AI Message
    messages.extend([
      {"role": "human", "content": data['user_query']},
      {"role": "ai", "content": data["llm_response"]}
    ])
    
  return messages
  
# Add document to db collection
def insert_document_record(filename):
  try:
    # Create document with proper structure
    doc_data = {
      "filename": filename,
      "upload_date": firestore.SERVER_TIMESTAMP
    }
    
    # Reference and set data
    doc_ref = db.collection('document_store').document()
    doc_ref.set(doc_data)
    
    return doc_ref.id

  except Exception as e:
    print(f"Error inserting document record: {e}")
    return None
  
# Delete document from db collection
def delete_document_record(file_id):
  try:
    doc_ref = db.collection('document_store').document(file_id)
    doc_ref.delete()
    
    print(f"Document with ID {file_id} successfully deleted")
    return True

  except Exception as e:
    print(f"Error deleting document: {e}")
    return False
  
# Get all documents from db collection:
def get_all_documents():
  try:
    # Reference to the documents collection
    docs_ref = db.collection('document_store').order_by('upload_date', direction=firestore.Query.DESCENDING)
    
    # Get all documents
    docs = docs_ref.stream()
    
    # Convert to list of dictionaries with specific fields only
    documents = []
    for doc in docs:
        doc_data = doc.to_dict()
        # Create a dict with just the fields we want, matching SQL version
        documents.append({
            'id': doc.id,
            'filename': doc_data.get('filename'),
            'upload_timestamp': doc_data.get('upload_date')
        })
    
    return documents
          
  except Exception as e:
    print(f"Error retrieving documents: {e}")
    return []
  
