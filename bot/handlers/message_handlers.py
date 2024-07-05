from telegram import Update
from telegram.ext import CallbackContext
from bot.utils.youtube_downloader import is_youtube_link
from bot.utils.youtube_downloader import download_youtube_video_handler
from bot.utils.audio_demo_creator import handle_audio_file

async def greet_new_member(update: Update, context: CallbackContext) -> None:
    if context.bot.username in update.message.text:
        await update.message.reply_text("خوش آمدم!")
        return
    
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            await update.message.reply_text(
                f"درود {member.full_name} به گروه {update.message.chat.title} خوش آمدید."
            )


async def say_goodbye(update: Update, context: CallbackContext) -> None:
    if context.bot.username in update.message.text:
        await update.message.reply_text("بدرود!")
        return
    
    if update.my_chat_member.new_chat_member:
        if update.my_chat_member.new_chat_member.status in ["kicked", "left"]:
            await update.message.reply_text(
                f"بدرود {update.my_chat_member.new_chat_member.user.full_name}!"
            )


async def handle_message(update: Update, context: CallbackContext) -> None:
    if update.message.text:
        text = update.message.text
        if is_youtube_link(text):
            await download_youtube_video_handler(update, context)
    elif update.message.audio or (update.message.document and update.message.document.mime_type == 'audio/mpeg'):
        await handle_audio_file(update, context)