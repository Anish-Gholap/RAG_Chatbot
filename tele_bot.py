from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp
import os
from dotenv import load_dotenv
from enum import Enum
import logging
import sys

# Streamlined logging setup - only important information
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    handlers=[
        logging.FileHandler("telegram_bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.INFO)

logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = "http://localhost:8000/chatbot/chat"
BOT_USERNAME = "@FakeOrNotBot"

class ModelName(str, Enum):
    llama = "llama-3.3-70b-versatile"
    GPT = "gpt-4o"

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.id} started a new session")
    user = update.effective_user
    context.user_data['session_id'] = None
    await update.message.reply_text(f"Hello {user.name}, how may I help you?")
  
async def handle_response(message: str, context: ContextTypes.DEFAULT_TYPE):
    try:
        session_id = context.user_data.get('session_id')
        
        request = {
            "question": message,
            "model": ModelName.llama
        }
        
        if session_id:
            request['session_id'] = session_id    
            
        logger.info(f"Sending request to API with session ID: {session_id}")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(API_URL, json=request) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        
                        if 'session_id' in response_data:
                            context.user_data['session_id'] = response_data['session_id']
                            
                        return response_data.get("answer", "Sorry, I couldn't process that")
                    else:
                        error_text = await response.text()
                        logger.error(f"API error: Status {response.status}")
                        return f"Error: Received status code {response.status}. Please try again later."
            except aiohttp.ClientError as e:
                logger.error(f"HTTP request error: {str(e)}")
                return f"Sorry, I couldn't connect to the API service. Please try again later."
                
    except Exception as e:
        logger.error(f"Unexpected error in handle_response: {str(e)}")
        return f"Sorry, an error occurred. Please try again later."
  
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # First, check if the message is valid
        if not update.message or not update.message.text:
            return
            
        message_type = update.message.chat.type
        message = update.message.text
        
        # Log only essential information about the incoming message
        logger.info(f"Received message from user {update.effective_user.id} in {message_type} chat")
        
        # Show typing while bot processes input
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING
            )
        except Exception:
            pass
        
        # Process message based on chat type
        if message_type in ["group", "supergroup"]:
            # Check if the bot is mentioned by username
            if BOT_USERNAME.lower() in message.lower():
                # Remove the mention and get the actual message - case insensitive
                clean_message = message.lower().replace(BOT_USERNAME.lower(), '').strip()
                response = await handle_response(clean_message, context)
            else:
                return
        else:
            response = await handle_response(message, context)

        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error in handle_message: {str(e)}")
        try:
            await update.message.reply_text("Sorry, an error occurred while processing your message.")
        except:
            pass
  
async def clear_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to clear the current session"""
    try:
        logger.info(f"User {update.effective_user.id} cleared session")
        context.user_data['session_id'] = None
        await update.message.reply_text("Session cleared. Starting a new conversation.")
    except Exception as e:
        logger.error(f"Error in clear_session: {str(e)}")
        await update.message.reply_text("Sorry, an error occurred while clearing your session.")

async def error_handler(update, context):
    """Log errors caused by updates."""
    logger.error(f"Update caused error: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("An error occurred while processing your request.")

def main():
    logger.info("Starting telegram bot")
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Register error handler
        app.add_error_handler(error_handler)
        
        # Commands
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('clear', clear_session))
        
        # Messages
        app.add_handler(MessageHandler(filters.TEXT, handle_message))
        
        logger.info("Bot started, polling for messages")
        app.run_polling()
    except Exception as e:
        logger.critical(f"Failed to start bot: {str(e)}")
  
if __name__ == "__main__":
    main()