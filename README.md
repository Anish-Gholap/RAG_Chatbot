# RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that allows users to chat with their documents through a FastAPI backend and Telegram interface.

## Project Overview

This project implements a conversational AI system that:

1. Allows users to upload, list, and delete documents (PDF, DOCX, HTML)
2. Indexes documents using vector embeddings (ChromaDB)
3. Retrieves relevant context when answering user questions
4. Maintains conversation history for contextual responses
5. Integrates with Telegram as a chat interface

## Architecture

The system consists of several components:

- **FastAPI Backend**: Provides REST API endpoints for chat, document management
- **Vector Database**: ChromaDB for storing document embeddings
- **LLM Integration**: Supports OpenAI (GPT-4o) and Groq (Llama) models
- **Firebase**: Stores chat history and document metadata
- **Telegram Bot**: Provides a conversational interface to end users

## Features

- **Document Processing**: Upload PDFs, DOCXs, and HTML files
- **Conversation Memory**: Maintains chat history for contextual understanding
- **Document Management**: List and delete documents from the vector store
- **Context-Aware Responses**: Uses RAG to provide document-grounded answers
- **Multi-Model Support**: Compatible with both OpenAI and Groq LLMs

## Setup and Installation

### Prerequisites

- Python 3.9+
- uv (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd rag-chatbot
   ```

2. Create a virtual environment and install dependencies:
   ```
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GROQ_API_KEY=your_groq_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   LANGCHAIN_API_KEY=your_langchain_api_key  # Optional for tracing
   LANGCHAIN_PROJECT=default
   LANGCHAIN_TRACING_V2=true
   ```

4. Set up Firebase:
   - Create a Firebase project
   - Generate a service account key
   - Save as `ragchatbot-62811-firebase-adminsdk-fbsvc-ae41064583.json` in the project root

## Usage

### Starting the FastAPI Server

```
uvicorn main:app --reload
```

This will start the FastAPI server on http://localhost:8000

### Starting the Telegram Bot

```
python tele_bot.py
```

### API Endpoints

- **POST /chatbot/chat**: Chat with the RAG system
- **POST /chatbot/upload-doc**: Upload and index a document
- **GET /chatbot/list-docs**: List all indexed documents
- **DELETE /chatbot/delete-doc**: Delete a document from the index

### Telegram Bot Commands

- **/start**: Begin a new conversation
- **/clear**: Clear the current conversation history
- Direct messages to the bot will be processed as questions

## System Components

### 1. Backend (backend.py)
Contains the FastAPI routes and endpoints for all chatbot functionality.

### 2. Chroma Utils (chroma_utils.py)
Handles document processing, embedding, and vector store operations.

### 3. Database (database.py)
Manages Firebase interactions for chat history and document metadata.

### 4. LangChain Utils (langchain_utils.py)
Sets up the LLM chains, retrievers, and prompts for the RAG system.

### 5. Telegram Bot (tele_bot.py)
Implements the Telegram interface for the chatbot.

### 6. Models (pydantic_utils.py)
Contains Pydantic models for API request/response structures.

## Development

### Adding New Document Types

To add support for new document types:
1. Update the allowed extensions in `backend.py`
2. Add a new document loader in `chroma_utils.py`

### Adding New LLM Models

To add new LLM providers:
1. Add the model to the `ModelName` enum in `pydantic_utils.py`
2. Update the model selection logic in `langchain_utils.py`
