import os
import openai
from openai import OpenAI
from config import BOT_TOKEN, OPENAI_KEY, OPENAI_KEY_2

# # Set the API key as an environment variable
# os.environ["OPENAI_API_KEY"] = OPENAI_KEY_2
#
# # Initialize the OpenAI client without specifying the API key
# client = openai.OpenAI()
#
# # print(chat_completion.choices[0].message.content)
#
# messages = []
#
# while True:
#     message = input("user: ")
#     if message:
#         messages.append({
#             "role": "user",
#             "content": message,
#         })
#         result = client.chat.completions.create(
#             messages=messages,
#             model="gpt-3.5-turbo",
#         )
#     reply = result.choices[0].message.content
#     print(reply)


# import os
# from typing import Final, Deque, Dict, Union
# from collections import deque
# import os
# import openai
# from openai import OpenAI
# from telegram import Update
# from telegram.ext import (
#     Application,
#     ApplicationBuilder,
#     CallbackContext,
#     CommandHandler,
#     ContextTypes,
#     MessageHandler,
#     filters,
# )
# from datetime import datetime, timedelta
# from config import BOT_TOKEN, OPENAI_KEY_2, testGroupId
#
# # Set the API key as an environment variable
# os.environ["OPENAI_API_KEY"] = OPENAI_KEY_2
#
# # Initialize the OpenAI client without specifying the API key
# client = openai.OpenAI()
#
# chat_history_dict = {}
#
# cooldown_time = timedelta(seconds=10)  # 30 seconds cooldown
# last_message_time = None
#
#
# def get_chat_history(chat_id):
#     # Retrieve chat history for the given chat_id, or create a new one if not exists
#     chat_history = chat_history_dict.get(chat_id, deque(maxlen=10))  # Adjust the maximum length as needed
#     chat_history_dict[chat_id] = chat_history
#     return chat_history
#
#
# async def chat_command(update: Update, context: CallbackContext):
#     global last_message_time
#     current_time = datetime.now()
#
#     # Check if the message is from the target group
#     if update.effective_chat.id != testGroupId:
#         return
#
#     # Check for cooldown
#     if last_message_time and current_time - last_message_time < cooldown_time:
#         await update.message.reply_text("لطفا صبر کنید. دستور قبلی در حال اجرا است.")
#         return
#
#     # Extract the user's message without the "/chat" command
#     user_message = update.message.text[6:].strip()
#
#     # Call the OpenAI API
#     await handle_response(testGroupId, user_message)
#
#     # Update the last message time
#     last_message_time = current_time
#
#
# async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("من بات تایپولوژی هستم. ایماگو منو ساخته. بگو چکار کنم؟")
#
#
# async def handle_response(chat_id: Union[int, str], text: str) -> str:
#     # Get the chat history
#     chat_history = list(get_chat_history(testGroupId))
#
#     # Create a user message
#     user_message = {"role": "user", "content": text}
#
#     # Add the user message to the chat history
#     chat_history.append(user_message)
#
#     # Use the OpenAI API to generate the bot's response
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=chat_history,
#         temperature=1,
#         max_tokens=256,
#         top_p=1,
#         frequency_penalty=0,
#         presence_penalty=0,
#     )
#
#     # Extract the bot's response from the response object
#     bot_response = response.choices[0].message.content
#
#     # Add the bot's response to the conversation history
#     chat_history.append({"role": "assistant", "content": bot_response})
#
#     return bot_response
#
#
# async def handle_response_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # Extract chat_id and text from the update
#     chat_id = testGroupId
#     text = update.message.text
#
#     # Call the original handle_response function and await its result
#     bot_response = await handle_response(chat_id, text)
#
#     # Send the bot's response
#     await update.message.reply_text(bot_response)
#
#
# if __name__ == "__main__":
#     app = Application.builder().token(BOT_TOKEN).build()
#
#     # Add command handlers
#     app.add_handler(CommandHandler("chat", chat_command))
#     app.add_handler(CommandHandler("help", help_command))
#
#     # Add message handler
#     app.add_handler(MessageHandler(filters.TEXT, callback=handle_response_wrapper))
#
#     # Start the Telegram bot
#     print("Bot started...")
#     app.run_polling(poll_interval=1)
#
# import os
# from collections import deque
# import openai
# from typing import Union
# from aiogram import Bot, Dispatcher, types
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Command
# from aiogram.utils.executor import start_polling
# from datetime import datetime, timedelta
# from config import BOT_TOKEN, OPENAI_KEY_2, testGroupId
#
# # Set the API key as an environment variable
# os.environ["OPENAI_API_KEY"] = OPENAI_KEY_2
#
# # Initialize the OpenAI client without specifying the API key
# client = openai.OpenAI()
#
# chat_history_dict = {}
#
# cooldown_time = timedelta(seconds=10)  # 30 seconds cooldown
# last_message_time = None
#
#
# def get_chat_history(chat_id):
#     # Retrieve chat history for the given chat_id, or create a new one if not exists
#     chat_history = chat_history_dict.get(chat_id, deque(maxlen=10))  # Adjust the maximum length as needed
#     chat_history_dict[chat_id] = chat_history
#     return chat_history
#
#
# async def chat_command(message: types.Message):
#     global last_message_time
#     current_time = datetime.now()
#
#     # Check if the message is from the target group
#     if message.chat.id != testGroupId:
#         return
#
#     # Check for cooldown
#     if last_message_time and current_time - last_message_time < cooldown_time:
#         await message.answer("Please wait. The previous command is still executing.")
#         return
#
#     # Extract the user's message without the "/chat" command
#     user_message = message.text[6:].strip()
#
#     # Call the OpenAI API
#     await handle_response(message.chat.id, user_message)
#
#     # Update the last message time
#     last_message_time = current_time
#
#
# async def help_command(message: types.Message):
#     await message.answer("I am a Typology bot. I was made by Imago. What should I do?")
#
#
# async def handle_response(chat_id: Union[int, str], text: str) -> str:
#     # Get the chat history
#     chat_history = list(get_chat_history(testGroupId))
#
#     # Create a user message
#     user_message = {"role": "user", "content": text}
#
#     # Add the user message to the chat history
#     chat_history.append(user_message)
#
#     # Use the OpenAI API to generate the bot's response
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=chat_history,
#         temperature=1,
#         max_tokens=256,
#         top_p=1,
#         frequency_penalty=0,
#         presence_penalty=0,
#     )
#
#     # Extract the bot's response from the response object
#     bot_response = response.choices[0].message.content
#
#     # Add the bot's response to the conversation history
#     chat_history.append({"role": "assistant", "content": bot_response})
#
#     return bot_response
#
#
# async def handle_response_wrapper(message: types.Message):
#     # Extract chat_id and text from the message
#     chat_id = testGroupId
#     text = message.text
#
#     # Call the original handle_response function and await its result
#     bot_response = await handle_response(chat_id, text)
#
#     # Send the bot's response
#     await message.answer(bot_response)
#
#
# if __name__ == "__main__":
#     bot = Bot(token=BOT_TOKEN)
#     dp = Dispatcher(bot, storage=MemoryStorage())
#
#     # Add command handlers
#     dp.register_message_handler(chat_command, commands=['chat'])
#     dp.register_message_handler(help_command, commands=['help'])
#
#     # Add message handler
#     dp.register_message_handler(handle_response_wrapper, content_types=types.ContentType.TEXT)
#
#     # Start the Telegram bot
#     print("Bot started...")
#     start_polling(dp, skip_updates=True)


# import os
# from aiogram import Bot, Dispatcher, types
# from openai import OpenAI
# import aiogram
# import openai
# from aiogram import Bot, types
# from aiogram.dispatcher import Dispatcher
# from aiogram.types import ParseMode
# from aiogram import executor
#
# TOKEN = BOT_TOKEN
#
# bot = Bot(token=TOKEN)
# dp = Dispatcher(bot)
#
# os.environ["OPENAI_API_KEY"] = OPENAI_KEY_2
# client = openai.OpenAI()
#
#
# @dp.message_handler(commands=['help'])
# async def send_welcome(message: types.Message):
#     await message.reply("درود. لطفا پرسش خود را به همراه دستور /chat ایجاد نمایید.")
#
#
# @dp.message_handler(lambda message: message.text.startswith('/chat'))
# async def chat_handler(message: types.Message):
#     # Extract the user's message after "/chat"
#     user_message = message.text[len('/chat'):].strip()
#
#     if user_message:
#         # Call OpenAI API to generate a response
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": user_message},
#             ],
#             temperature=1,
#             max_tokens=256,
#             top_p=1,
#             frequency_penalty=0,
#             presence_penalty=0,
#         )
#         # Send the generated response to the user
#         await message.reply(response.choices[0].message.content, parse_mode=ParseMode.MARKDOWN)
#
#     else:
#         await message.reply("لطفا بعد از دستور /chat سوال خود را مطرح کنید.")
#
#
# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True)













# num_messages = int(context.args[0]) if context.args else 1

#     if update.message.reply_to_message:
#         replied_user = update.message.reply_to_message.from_user
#         if replied_user.id == context.bot.id:
#             await context.bot.send_message(
#                 chat_id=update.effective_chat.id,
#                 text="من نمی‌توانم پیام‌های خودم را حذف کنم."
#             )
#             return

#         try:
#             await update.message.reply_to_message.delete()
#         except BadRequest as e:
#             logging.error(f"Error deleting replied message: {e}")
#             await context.bot.send_message(
#                 chat_id=update.effective_chat.id,
#                 text="خطایی در حذف پیام رخ داد."
#                 )

#         deleted_count = 1
#         for i in range(num_messages - 1):
#             try:
#                 message_id = update.message.reply_to_message.message_id - num_messages + i - 1
#                 await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
#                 deleted_count += 1
#             except BadRequest as e:
#                 logging.error(f"Error deleting message: {e}")
#                 break
#             except TelegramError as e:
#                 logging.error(f"Telegram error deleting message: {e}")

#         if deleted_count > 1:
#             await context.bot.send_message(
#                 chat_id=update.effective_chat.id,
#                 text=f"پیام کاربر [{replied_user.full_name}](tg://user?id={replied_user.id}) و {deleted_count - 1} پیام قبلی "
#                 f"توسط ادمین [{admin.full_name}](tg://user?id={admin.id}) حذف شد.",
#                 parse_mode='Markdown'
#             )
#         else:
#             await context.bot.send_message(
#                 chat_id=update.effective_chat.id,
#                 text=f"پیام کاربر [{replied_user.full_name}](tg://user?id={replied_user.id}) توسط ادمین [{admin.full_name}](tg://user?id={admin.id}) حذف شد.",
#                 parse_mode='Markdown'
#             )
#     else:
#         deleted_count = 1
#         for i in range(num_messages - 1):
#             try:
#                 message_id = update.message.message_id - num_messages + i - 1
#                 await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
#                 deleted_count += 1
#             except BadRequest as e:
#                 logging.error(f"Error deleting message: {e}")
#                 break
#             except TelegramError as e:
#                 logging.error(f"Telegram error deleting message: {e}")
        
#         if deleted_count > 0:
#             if deleted_count > 1:
#                 await context.bot.send_message(
#                     chat_id=update.effective_chat.id,
#                     text=f"{deleted_count} پیام اخیر توسط ادمین [{admin.full_name}](tg://user?id={admin.id}) حذف شد.",
#                     parse_mode='Markdown'
#                 )
#             else:
#                 await context.bot.send_message(
#                     chat_id=update.effective_chat.id,
#                     text=f"پیام اخیر توسط ادمین [{admin.full_name}](tg://user?id={admin.id}) حذف شد.",
#                     parse_mode='Markdown'
#                 )
#         else:
#             await context.bot.send_message(
#                 chat_id=update.effective_chat.id,
#                 text="خطایی در حذف پیام‌ها رخ داد. لطفاً از دسترسی من اطمینان حاصل کنید.",
#                 parse_mode='Markdown'
#             )