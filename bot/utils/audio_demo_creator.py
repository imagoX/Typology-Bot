from pydub import AudioSegment
from telegram import Update, InputFile
from telegram.ext import CallbackContext
import os
import time
import logging
from tqdm import tqdm
import asyncio
import subprocess

DOWNLOAD_PATH = 'downloads/'

cooldown_users_audio = {}
COOLDOWN_TIME_AUDIO = 10

MAX_VOICE_SIZE = 50 * 1024 * 1024
MAX_FILE_SIZE = 20 * 1024 * 1024

last_demo_messages = {}

def sanitize_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()

def create_audio_demo(file_path, start_time, duration):
    try:
        audio = AudioSegment.from_file(file_path)
    except:
        temp_wav = file_path + ".wav"
        try:
            subprocess.run(["ffmpeg", "-i", file_path, temp_wav], check=True, capture_output=True)
            audio = AudioSegment.from_wav(temp_wav)
        finally:
            if os.path.exists(temp_wav):
                os.remove(temp_wav)

    start_ms = start_time * 1000
    duration_ms = duration * 1000
    demo_audio = audio[start_ms:start_ms + duration_ms]
    demo_path = file_path.rsplit('.', 1)[0] + f"_demo_{start_time}s.ogg"
    demo_audio.export(demo_path, format="ogg")
    demo_size = os.path.getsize(demo_path)
    return demo_path, demo_size

async def handle_audio_file(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id in cooldown_users_audio and (time.time() - cooldown_users_audio[user_id]) < COOLDOWN_TIME_AUDIO:
        remaining_time = COOLDOWN_TIME_AUDIO - (time.time() - cooldown_users_audio[user_id])
        await update.message.reply_text(f"لطفاً {remaining_time:.0f} ثانیه صبر کنید.")
        return

    if update.message.audio:
        file = update.message.audio
        title = file.title or file.performer or file.file_name or f"audio_{file.file_id}"
    elif update.message.document and update.message.document.mime_type == 'audio/mpeg':
        file = update.message.document
        title = file.file_name
    else:
        await update.message.reply_text("لطفاً یک فایل صوتی ارسال کنید.")
        return

    file_id = file.file_id
    file_name = sanitize_filename(title + os.path.splitext(file.file_name)[-1])
    file_path = f"{DOWNLOAD_PATH}/{file_name}"

    if file.file_size > MAX_FILE_SIZE:
        await update.message.reply_text("این فایل بسیار بزرگ است. لطفاً یک فایل کوچکتر ارسال کنید.")
        return

    try:
        file_obj = await context.bot.get_file(file_id)
        await file_obj.download_to_drive(custom_path=file_path)
        
        await create_audio_demo_handler(update, context, file_path, title)
    except Exception as e:
        logging.error(f"Error downloading or processing file: {e}")
        await update.message.reply_text(f"خطا در دانلود یا پردازش فایل: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

async def create_audio_demo_handler(update: Update, context: CallbackContext, file_path: str, title: str) -> None:
    try:
        demo_path, demo_size = create_audio_demo(file_path, start_time=0, duration=30)

        first_message_after_creating = await update.message.reply_text("در حال آپلود فایل صوتی...")

        uploader = ProgressUploader(demo_path)
        if demo_size <= MAX_VOICE_SIZE:
            demo_message = await uploader.upload(
                context.bot,
                update.message.chat_id,
                caption=f"{title}",
                as_voice=True
            )
        else:
            demo_message = await uploader.upload(
                context.bot,
                update.message.chat_id,
                caption=f"{title} (فایل صوتی بزرگتر از 50 مگابایت است.)",
                as_voice=False
            )

        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=first_message_after_creating.message_id)

        last_demo_messages[update.effective_user.id] = demo_message.message_id

        cooldown_users_audio[update.message.from_user.id] = time.time()

    except Exception as e:
        logging.error(f"Error creating audio demo: {e}")
        await update.message.reply_text(f"خطا در ایجاد فایل صوتی: {e}")
    finally:
        if os.path.exists(demo_path):
            os.remove(demo_path)

class ProgressUploader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)
        self.uploaded = 0
        self.pbar = tqdm(total=self.file_size, unit='B', unit_scale=True, desc="Uploading")

    async def upload(self, bot, chat_id, caption=None, as_voice=False):
        with open(self.file_path, 'rb') as file:
            input_file = InputFile(file)
            try:
                if as_voice:
                    message = await bot.send_voice(
                        chat_id=chat_id,
                        voice=input_file,
                        caption=caption,
                        read_timeout=300,
                        write_timeout=300
                    )
                else:
                    message = await bot.send_document(
                        chat_id=chat_id,
                        document=input_file,
                        caption=caption,
                        read_timeout=300,
                        write_timeout=300
                    )
                
                chunk_size = 1024 * 1024
                while self.uploaded < self.file_size:
                    self.uploaded = min(self.uploaded + chunk_size, self.file_size)
                    self.pbar.update(min(chunk_size, self.file_size - self.pbar.n))
                    await asyncio.sleep(0.1)
                
                return message
            finally:
                self.pbar.close()
