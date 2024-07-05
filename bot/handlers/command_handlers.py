from datetime import datetime, timedelta
from telegram import Update, ChatPermissions
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    ContextTypes,
)
from telegram.constants import ChatMemberStatus
from telegram.error import BadRequest, TelegramError
import logging
import os

from misc import (
    GROUP_ID,
    TEST_GROUP_ID,
    GROUP_ID2,
)
from bot.utils.chatgpt_integration import generate_chat_response
from bot.utils.audio_demo_creator import create_audio_demo
from bot.utils.audio_demo_creator import ProgressUploader
from bot.utils.audio_demo_creator import DOWNLOAD_PATH
from bot.utils.audio_demo_creator import last_demo_messages


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

ALLOWED_GROUP_IDS = [GROUP_ID, GROUP_ID2, TEST_GROUP_ID]


async def is_user_admin(chat_id: int, user_id: int, context: CallbackContext) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except Exception as e:
        logging.error(f"Error checking admin status: {e}")
        return False


def is_allowed_group(chat_id: int) -> bool:
    return chat_id in ALLOWED_GROUP_IDS


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "در حال اجرا هستم. برای راهنمایی بیشتر دستور /help را وارد کنید."
    )


async def help(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        f"درود، {update.message.from_user.full_name}\n\n"
        f"من Typology Bot v2 هستم.\n\n"
        f"برای استفاده، من را به گروه خود با دسترسی‌های معمولی ادمین "
        f"اضافه کنید، "
        f"در غیر این صورت، نمی‌توانم کار کنم.\n\n\n"
        f"دستورات برای ادمین‌ها:\n\n"
        f"<code>/ban</code> (دلیل) - بن کردن کاربر و حذف او از گروه\n\n"
        f"<code>/unban</code> - آنبن کردن\n\n"
        f"<code>/mute</code> - میوت کردن\n\n"
        f"<code>/mute 10m</code> - میوت کردن کاربر در زمان مشخص شده - 30m, 2h, 1d\n\n"
        f"<code>/unmute</code> - آنمیوت کردن\n\n"
        f"<code>/del</code> - حذف پیام\n\n"
        f"<code>/del 10</code> - حذف 10 پیام\n\n"
        f"<code>/report</code> - گزارش به ادمین‌ها\n\n"
        f"<code>/pin</code> - سنجاق کردن پیام\n\n"
        f"<code>/unpin</code> - از سنجاق خارج کردن\n\n"
        f"<code>/unpin_all</code> - از سنجاق خارج کردن همه پیام‌ها\n\n"
        f"توجه: تمام دستورات به جز آخری باید با پاسخ به پیام کاربر ارسال شوند!\n\n"
        f"<code>/admins</code> - نمایش همه ادمین‌ها\n\n\n"
        f"<code>/chat</code> - چت با بات\n\n"
        f"با فرستادن لینک یوتیوب، به صورت خودکار دانلود می شود.\n\n\n"
        f"<i>توسعه داده شده توسط ایماگو</i>",
        parse_mode="HTML",
    )

    if not is_allowed_group(update.message.chat.id):
        await update.message.reply_text("غیر از اون، این گروه، گروه تایپولوژی نیست.")
        return


async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "لطفاً این دستور را در پاسخ به پیام کاربر مورد نظر استفاده کنید."
        )
        return

    replied_user = update.message.reply_to_message.from_user
    admin = update.effective_user

    if not await is_user_admin(
        update.message.chat.id, update.message.from_user.id, context
    ):
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return

    if replied_user.id == context.bot.id:
        await update.message.reply_text("من نمی‌توانم خودم را بن کنم.")
        return

    reason = " ".join(context.args) if context.args else "بدون دلیل"

    try:
        await context.bot.ban_chat_member(
            chat_id=update.effective_chat.id, user_id=replied_user.id
        )
        await update.message.reply_text(
            f"کاربر [{replied_user.full_name}](tg://user?id={replied_user.id}) "
            f"توسط ادمین [{admin.full_name}](tg://user?id={admin.id}) بن شد.\n"
            f"دلیل: {reason}",
            parse_mode="Markdown",
        )
    except BadRequest as e:
        if "administrator" in str(e).lower():
            await update.message.reply_text("من نمی‌توانم یک ادمین را بن کنم.")
        else:
            await update.message.reply_text(
                "من نمی‌توانم کاربر را بن کنم. لطفاً از دسترسی من اطمینان حاصل کنید."
            )


async def unban(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "لطفاً این دستور را در پاسخ به پیام کاربر مورد نظر استفاده کنید."
        )
        return

    replied_user = update.message.reply_to_message.from_user
    admin = update.effective_user

    if not await is_user_admin(
        update.message.chat.id, update.message.from_user.id, context
    ):
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return

    if replied_user.id == context.bot.id:
        await update.message.reply_text("من نمی‌توانم خودم را بن کنم.")
        return

    try:
        await context.bot.unban_chat_member(
            chat_id=update.effective_chat.id, user_id=replied_user.id
        )
        await update.message.reply_text(
            f"کاربر [{replied_user.full_name}](tg://user?id={replied_user.id}) "
            f"توسط ادمین [{admin.full_name}](tg://user?id={admin.id}) آنبن شد.",
            parse_mode="Markdown",
        )
    except BadRequest as e:
        if "administrator" in str(e).lower():
            await update.message.reply_text("من نمی‌توانم یک ادمین را آنبن کنم.")
        else:
            await update.message.reply_text(
                "من نمی‌توانم کاربر را آنبن کنم. لطفاً از دسترسی من اطمینان حاصل کنید."
            )


async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "لطفاً این دستور را در پاسخ به پیام کاربر مورد نظر استفاده کنید."
        )
        return

    replied_user = update.message.reply_to_message.from_user
    admin = update.effective_user

    chat_member = await context.bot.get_chat_member(update.effective_chat.id, admin.id)
    if chat_member.status not in [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    ]:
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return

    if replied_user.id == context.bot.id:
        await update.message.reply_text("من نمی‌توانم خودم را میوت کنم.")
        return

    mute_duration = None
    if len(context.args) > 0:
        try:
            mute_duration = int(context.args[0])
            until_date = datetime.now() + timedelta(minutes=mute_duration)
        except ValueError:
            await update.message.reply_text(
                "لطفاً یک عدد صحیح برای مدت میوت وارد کنید (به دقیقه)."
            )
            return
    else:
        until_date = None

    try:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=replied_user.id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
            ),
            until_date=until_date,
        )

        duration_text = (
            f" به مدت {mute_duration} دقیقه" if mute_duration else " به صورت نامحدود"
        )
        await update.message.reply_text(
            f"کاربر [{replied_user.full_name}](tg://user?id={replied_user.id}) "
            f"توسط ادمین [{admin.full_name}](tg://user?id={admin.id}){duration_text} میوت شد.",
            parse_mode="Markdown",
        )
    except BadRequest as e:
        if "user is an administrator" in str(e).lower():
            await update.message.reply_text("من نمی‌توانم یک ادمین را میوت کنم.")
        else:
            logging.error(f"Error muting user: {e}")
            await update.message.reply_text(
                "خطایی در میوت کردن کاربر رخ داد. لطفاً از دسترسی من اطمینان حاصل کنید."
            )


async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "لطفاً این دستور را در پاسخ به پیام کاربر مورد نظر استفاده کنید."
        )
        return

    replied_user = update.message.reply_to_message.from_user
    admin = update.effective_user

    chat_member = await context.bot.get_chat_member(update.effective_chat.id, admin.id)
    if chat_member.status not in [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    ]:
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return

    if replied_user.id == context.bot.id:
        await update.message.reply_text("من نمی‌توانم خودم را آنمیوت کنم.")
        return

    try:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=replied_user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_polls=False,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
            ),
        )
        await update.message.reply_text(
            f"کاربر [{replied_user.full_name}](tg://user?id={replied_user.id}) "
            f"توسط ادمین [{admin.full_name}](tg://user?id={admin.id}) آنمیوت شد.",
            parse_mode="Markdown",
        )
    except BadRequest as e:
        if "user is an administrator" in str(e).lower():
            await update.message.reply_text("من نمی‌توانم یک ادمین را آنمیوت کنم.")
        else:
            logging.error(f"Error unmuting user: {e}")
            await update.message.reply_text(
                "خطایی در آنمیوت کردن کاربر رخ داد. لطفاً از دسترسی من اطمینان حاصل کنید."
            )


async def delete_message(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    admin = update.effective_user
    chat_member = await context.bot.get_chat_member(update.effective_chat.id, admin.id)

    if chat_member.status not in [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    ]:
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return

    if update.message.reply_to_message:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.reply_to_message.message_id,
            )
        except TelegramError as e:
            logging.error(f"Error deleting message: {e}")
            await update.message.reply_text("خطایی در حذف پیام رخ داد.")


async def pin_message(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    if not await is_user_admin(
        update.message.chat.id, update.message.from_user.id, context
    ):
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return

    if update.message.reply_to_message:
        try:
            await update.message.reply_to_message.pin()
        except Exception as e:
            logging.error(f"Error pinning message: {e}")
            await update.message.reply_text("خطایی در سنجاق کردن پیام رخ داد.")
    else:
        await update.message.reply_text(
            "این دستور باید با ریپلای به پیام کاربر ارسال شود."
        )


async def unpin_message(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    if not await is_user_admin(
        update.message.chat.id, update.message.from_user.id, context
    ):
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return

    try:
        await update.message.chat.unpin_all_messages()
    except Exception as e:
        logging.error(f"Error unpinning messages: {e}")
        await update.message.reply_text("خطایی در از سنجاق خارج کردن پیام رخ داد.")


async def unpin_all_messages(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    if not await is_user_admin(
        update.message.chat.id, update.message.from_user.id, context
    ):
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return

    try:
        await update.message.chat.unpin_all_messages()
    except Exception as e:
        logging.error(f"Error unpinning messages: {e}")
        await update.message.reply_text("خطایی در از سنجاق خارج کردن پیام‌ها رخ داد.")


async def report(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "این دستور باید با ریپلای به پیام کاربر ارسال شود."
        )
        return

    reported_user = update.message.reply_to_message.from_user
    reported_by = update.message.from_user

    reported_user_chat_member = await context.bot.get_chat_member(
        update.effective_chat.id, reported_user.id
    )
    if reported_user_chat_member.status in ("administrator", "creator"):
        await update.message.reply_text("نمی‌توانید یک ادمین را گزارش دهید.")
        return

    if reported_user.id == reported_by.id:
        await update.message.reply_text("نمی‌توانید خودتان را گزارش دهید.")
        return

    admins = await context.bot.get_chat_administrators(update.effective_chat.id)

    admin_mentions = [
        f"[ ](tg://user?id={admin.user.id})"
        for admin in admins
        if not admin.user.is_bot
    ]

    try:
        admin_mentions_text = "".join(admin_mentions)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{admin_mentions_text}\n"
            f"کاربر "
            f"[{reported_user.full_name}](tg://user?id={reported_user.id}) گزارش شد.",
            parse_mode="Markdown",
        )
        await update.message.reply_text("گزارش شما ارسال شد.")
    except Exception as e:
        logging.error(f"Error reporting user: {e}")
        await update.message.reply_text("خطایی در گزارش کاربر رخ داد.")


async def get_admins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        admins = await context.bot.get_chat_administrators(update.effective_chat.id)
        admin_info = []
        for admin in admins:
            status = "creator" if admin.status == "creator" else "admin"
            admin_info.append(f"{admin.user.full_name} - {status}")
        admin_list = "\n".join(admin_info)
        await update.message.reply_text(f"ادمین‌های در گروه:\n{admin_list}")
    except Exception as e:
        logging.error(f"Error getting admins: {e}")
        await update.message.reply_text("خطایی در نمایش ادمین‌ها رخ داد.")


async def my_info(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        f"نام: {update.message.from_user.full_name}\n"
        f"آیدی: {update.message.from_user.id}\n"
        f"زبان: {update.message.from_user.language_code}\n"
        f"نام کاربری: {update.message.from_user.username}"
    )

async def chat_info(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        f"نام گروه: {update.message.chat.title}\n"
        f"آیدی گروه: {update.message.chat.id}\n"
        f"نوع گروه: {update.message.chat.type}"
    )

async def chat(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    user_message = " ".join(context.args)
    if not user_message:
        await update.message.reply_text("لطفاً یک پیام برای چت وارد کنید.")
        return

    response = await generate_chat_response(user_message)

    await update.message.reply_text(response)

async def from_command(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return
    
    if not update.message.reply_to_message or not update.message.reply_to_message.audio:
        await update.message.reply_text("لطفاً این دستور را با ریپلای به یک فایل صوتی ارسال کنید. مثال: /from 10")
        return

    try:
        start_time = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("لطفاً یک عدد صحیح برای زمان شروع وارد کنید. مثال: /from 10")
        return

    audio = update.message.reply_to_message.audio
    duration = audio.duration

    if start_time >= duration:
        await update.message.reply_text(f"زمان شروع نمی‌تواند بیشتر از مدت زمان فایل ({duration}s) باشد.")
        return

    file_id = audio.file_id
    file_name = audio.file_name or f"audio_{file_id}.mp3"
    title = audio.title or audio.performer or os.path.splitext(file_name)[0]

    file = await context.bot.get_file(file_id)
    file_path = f"{DOWNLOAD_PATH}/{file_name}"
    await file.download_to_drive(custom_path=file_path)

    loading_message = await update.message.reply_text("در حال ایجاد فایل صوتی...")
    demo_duration = min(30, duration - start_time)
    demo_path, demo_size = create_audio_demo(file_path, start_time, demo_duration)

    if update.effective_user.id in last_demo_messages:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=last_demo_messages[update.effective_user.id]
            )
        except Exception as e:
            logging.error(f"Error deleting previous demo: {e}")

    uploader = ProgressUploader(demo_path)
    demo_message = await uploader.upload(
        context.bot,
        update.message.chat_id,
        caption=f"دموی {title} (from {start_time}s)",
        as_voice=True
    )
    
    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=loading_message.message_id)

    last_demo_messages[update.effective_user.id] = demo_message.message_id

    os.remove(file_path)
    os.remove(demo_path)