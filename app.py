from fastapi import FastAPI
from ai_agent import ask_ai

from routes.webhook_routes import router as webhook_router

from database import create_database

from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount(
    "/products", 
    StaticFiles(directory="products"), 
    name="products"
)

create_database()

app.include_router(webhook_router)


@app.get("/")

def home():

    return {
        "message": "WhatsApp AI Chatbot Running"
    }


@app.get("/chat")

def chat(message: str):

    ai_response = ask_ai(message)

    return {
        "user_message": message,
        "ai_response": ai_response
    }