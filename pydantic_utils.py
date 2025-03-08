from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

# Models available
class ModelName(str, Enum):
  llama = "llama-3.3-70b-versatile"
  GPT = "gpt-40"

# /chat QueryInput
class QueryInput(BaseModel):
  question: str
  session_id: str = Field(default=None)
  model: ModelName = Field(default=ModelName.llama)
  
# /chat QueryResponse
class QueryResponse(BaseModel):
  answer: str
  session_id: str
  model: ModelName
  
# /list-doc Response
class DocumentInfo(BaseModel):
  id : str
  filename: str
  upload_timestamp: datetime
  
# /delete_doc Request
class DeleteFileRequest(BaseModel):
  file_id: str
  
