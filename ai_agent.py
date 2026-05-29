from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

from database import get_recent_messages
from products.system_prompt import SYSTEM_PROMPT

load_dotenv()

model = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")
)


def ask_ai(user_number, user_message):

    try:

        history = get_recent_messages(user_number)

        conversation = ""

        # Add system prompt
        conversation += f"{SYSTEM_PROMPT}\n\n"

        # Add chat history
        for role, message in history:

            if role == "user":
                conversation += f"User: {message}\n"

            elif role == "assistant":
                conversation += f"Assistant: {message}\n"

        # Add current message
        conversation += f"User: {user_message}"

        response = model.invoke(conversation)

        return response.content

    except Exception as e:
        return f"AI Error: {str(e)}"