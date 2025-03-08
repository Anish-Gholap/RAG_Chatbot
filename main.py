from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from backend import router
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Setup LangSmith
os.environ["LANGSMITH_TRACING_V2"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = 'https://api.smith.langchain.com'
os.environ["LANGSMITH_PROJECT"] = "RAG_Chatbot"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

app = FastAPI()

app.include_router(router=router)

@app.get("/")
async def root():
    content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>API Health Check</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f5f5f5;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    color: #333;
                }
                .container {
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    padding: 2rem;
                    width: 80%;
                    max-width: 700px;
                }
                h1 {
                    color: #2c3e50;
                    margin-bottom: 0.5rem;
                    text-align: center;
                }
                .status {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 1.5rem 0;
                }
                .status-indicator {
                    width: 15px;
                    height: 15px;
                    border-radius: 50%;
                    background-color: #2ecc71;
                    margin-right: 10px;
                }
                .info {
                    background-color: #f8f9fa;
                    border-radius: 4px;
                    padding: 1rem;
                    margin: 1rem 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>API Health Status</h1>
                <div class="status">
                    <div class="status-indicator"></div>
                    <span>API is running properly</span>
                </div>
                <div class="info">
                    <p><strong>Environment:</strong> Production</p>
                    <p><strong>Status:</strong> Online</p>
                    <p><strong>Last Check:</strong> <script>document.write(new Date().toLocaleString())</script></p>
                </div>
            </div>
        </body>
    </html>
    """

    return HTMLResponse(content=content,status_code=200)