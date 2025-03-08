from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from typing import List
from chroma_utils import vector_store
from pydantic_utils import ModelName
import os
import config
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if config.LANGCHAIN_API_KEY:
  os.environ["LANGCHAIN_API_KEY"] = config.LANGCHAIN_API_KEY
  os.environ["LANGCHAIN_PROJECT"] = config.LANGCHAIN_PROJECT
  os.environ["LANGCHAIN_TRACING_V2"] = str(config.LANGCHAIN_TRACING_V2).lower()

# Initialise vector store retriever
retriever = vector_store.as_retriever(search_kwargs={"k":2})

# Initialise Output Parser
output_parser = StrOutputParser()

# Set up System Prompts
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Use the following context to answer the user's question."),
    ("system", "Context: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])
# Web search system prompt
web_search_system_prompt = """You are an AI assistant with the ability to search the web for information. When a user asks a question that could benefit from web information, you should:

1. Determine if searching the web would enhance your response.
2. If yes, explicitly mention that you'll search the web to provide better information.
3. When analyzing information from the web, extract key information and provide clear citations.

When you need to search for information:
- Use specific search terms and proper keywords
- Specify file types when appropriate (example: "climate change reports filetype:pdf")
- Always provide attribution for information you retrieve

You maintain conversation history within each chat context separately. Each conversation is isolated from others. When the user clears their session, start fresh with no memory of previous interactions.

Remember: Users rely on you for accurate information. Be transparent about the sources of your knowledge and when you're uncertain about something. Always prioritize quality of information over quantity."""

web_search_prompt = ChatPromptTemplate.from_messages([
    ("system", web_search_system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# Create RAG Chain
# User query → Retriever → Documents → create_stuff_documents_chain → Formats prompt with {context} filled → LLM → Response
def get_rag_chain(model: str):
  if model == "gpt-4o":
    llm = ChatOpenAI(model=model)
  else: 
    llm = ChatGroq(model=model)
    
  history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
  
  question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
  
  rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
  
  return rag_chain



