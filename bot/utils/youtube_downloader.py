from pytube import YouTube
import re
import yt_dlp
import os
import time
import logging
from telegram import Update, InputFile
from telegram.ext import CallbackContext
import asyncio
from tqdm import tqdm

DOWNLOAD_PATH = 'downloads/'

cooldown_users = {}
COOLDOWN_TIME = 60

def sanitize_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()

def download_youtube_video(url, download_path):
    ydl_opts = {
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'timeout': 60,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info_dict)
            sanitized_title = sanitize_filename(info_dict.get('title', 'video'))
            extension = os.path.splitext(video_path)[1]
            new_video_path = os.path.join(download_path, f"{sanitized_title}{extension}")
            
            counter = 1
            while os.path.exists(new_video_path):
                new_video_path = os.path.join(download_path, f"{sanitized_title}_{counter}{extension}")
                counter += 1

            os.rename(video_path, new_video_path)
            return new_video_path, sanitized_title
    except Exception as e:
        logging.error(f"Error downloading video: {e}")
        raise e

YT_LINK_REGEX = r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"

def is_youtube_link(text):
    return re.match(YT_LINK_REGEX, text) is not None

async def download_youtube_video_handler(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id in cooldown_users and (time.time() - cooldown_users[user_id]) < COOLDOWN_TIME:
        remaining_time = COOLDOWN_TIME - (time.time() - cooldown_users[user_id])
        await update.message.reply_text(f"لطفاً {remaining_time:.0f} ثانیه صبر کنید.")
        return

    url = update.message.text
    if is_youtube_link(url):
        try:
            start_msg = await update.message.reply_text("در حال دانلود ویدیو...")

            video_path, video_title = download_youtube_video(url, DOWNLOAD_PATH)
            
            file_size = os.path.getsize(video_path)
            if file_size > 50 * 1024 * 1024:
                await update.message.reply_text("ویدیو باید کمتر از 50 مگابایت باشد. لطفا ویدیو کوچکتری انتخاب کنید.")
                return
            
            uploader = ProgressUploader(video_path)
            await uploader.upload(
                context.bot,
                update.message.chat_id,
                caption=f"این هم ویدیوی شما.\n\n{video_title}\n\n{url}\n\n@Typology_Theories_Bot"
            )
            
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=start_msg.message_id)

            cooldown_users[user_id] = time.time()
            
        except asyncio.TimeoutError:
            await update.message.reply_text("خطا در ارسال ویدیو. لطفا دوباره تلاش کنید.")
        except Exception as e:
            logging.error(f"Error downloading or sending video: {e}")
            await update.message.reply_text(f"ویدیو دانلود نشد. لطفا دوباره تلاش کنید.")
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)

class ProgressUploader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)
        self.uploaded = 0
        self.pbar = tqdm(total=self.file_size, unit='B', unit_scale=True, desc="Uploading")

    async def upload(self, bot, chat_id, caption=None):
        with open(self.file_path, 'rb') as file:
            input_file = InputFile(file)
            try:
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
