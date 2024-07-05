import openai
from openai import OpenAI
from misc import OPENAI_API

client = OpenAI(api_key=OPENAI_API)

async def generate_chat_response(user_message: str) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message['content'].strip()
