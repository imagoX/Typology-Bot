import logging
import os
import time

import openai
from aiogram import executor
from aiogram import types
from aiogram.dispatcher.filters import AdminFilter, IsReplyFilter
from aiogram.types import ParseMode
from aiogram.utils.exceptions import (
    ChatAdminRequired,
    UserIsAnAdministratorOfTheChat,
    CantRestrictSelf,
)
from datetime import datetime, timedelta
from config import adminId, OPENAI_API_KEY, groupId, groupId2, testGroupId
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from pytube import YouTube
import time
import re
import openai

# from random import randint
from tests.misc import bot, dp


# Send admin message about bot started
async def send_adm(*args, **kwargs):
    await bot.send_message(chat_id=adminId, text="بات Typology Bot اجرا شد!")


@dp.message_handler(commands=["chatinfo"])
async def get_chat_id(message: types.Message):
    chat_id = message.chat.id
    await message.reply(f"The chat ID is: {chat_id}")


@dp.message_handler(commands=["help"])
async def send_welcome(message: types.Message):
    await message.reply(
        f"درود، "
        f"{message.from_user.full_name}\n\n"
        f"من Typology Bot v1.5 هستم.\n\n"
        f"برای استفاده، من را به گروه خود با دسترسی های معمولی ادمین "
        f"اضافه کنید، "
        f"در غیر این صورت قادر به عملکرد نخواهم بود.\n\n"
        f"دستورات برای ادمین ها:\n\n"
        f"<code>!بن</code> (دلیل) - بن کردن کاربر و حذف او از گروه\n"
        f"<code>!آنبن</code> - آنبن کردن\n"
        f"<code>!میوت</code> - میوت کردن\n"
        f"<code>!میوت 10m</code> -"
        f" میوت کردن کاربر در زمان مشخص شده"
        f" - 30m, 2h, 1d\n"
        f"<code>!حذف</code> - حذف پیام\n"
        f"<code>!گزارش</code> - گزارش به ادمین ها\n"
        f"<code>!پین</code> - سنجاق کردن پیام\n"
        f"<code>!آنپین</code> - از سنجاق خارج کردن\n"
        f"<code>!آنپین_همه</code> - از سنجاق خارج کردن همه پیام ها\n"
        f"توجه: تمام دستورات به جز آخری باید با پاسخ به پیام کاربر ارسال شوند!\n\n"
        f"<code>!ادمین</code> - نمایش همه ادمین ها\n\n"
        f"<code>/chat</code> - چت با بات\n"
        f"با فرستادن لینک یوتیوب، به صورت خودکار دانلود می شود.\n\n"
        f"<i>توسعه داده شده توسط ایماگو</i>"
    )
    if (
        message.chat.id != groupId
        and message.chat.id != testGroupId
        and message.chat.id != groupId2
    ):
        await message.reply("غیر از اون، این گروه، گروه تایپولوژی نیست.")


#################<-MODERATION->###################
# info tour
@dp.message_handler(commands=["start"])
async def welcome_send_info(message: types.Message):
    await message.answer(
        "در حال اجرا هستم. برای راهنمایی بیشتر دستور /help را وارد کنید."
    )


# new chat member
@dp.message_handler(content_types=["new_chat_members"])
async def new_chat_member(message: types.Message):
    # await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
    if (
        message.chat.id != groupId
        and message.chat.id != testGroupId
        and message.chat.id != groupId2
    ):
        await message.reply("این گروه، گروه تایپولوژی نیست.")
    else:
        chat_id = message.chat.id
        await bot.send_message(
            chat_id=chat_id,
            text=f"درود "
            f"[{message.new_chat_members[0].full_name}]"
            f"(tg://user?id={message.new_chat_members[0].id})"
            f"، به گروه تایپولوژی خوش آمدید.",
            parse_mode=types.ParseMode.MARKDOWN,
        )


# member leave chat
@dp.message_handler(content_types=["left_chat_member"])
@dp.message_handler(content_types=["ban_chat_member"])
async def left_chat_member(message: types.Message):
    if (
        message.chat.id != groupId
        and message.chat.id != testGroupId
        and message.chat.id != groupId2
    ):
        await message.reply("این گروه، گروه تایپولوژی نیست.")
    else:
        chat_id = message.chat.id
        left_member = message.left_chat_member
        await bot.send_message(
            chat_id=chat_id,
            text=f"بدرود "
            f"[{left_member.full_name}]"
            f"(tg://user?id={left_member.id})"
            f" عزیز.",
            parse_mode=types.ParseMode.MARKDOWN,
        )


# delete message user leave chat
# @dp.message_handler(content_types=["left_chat_member"])
# async def leave_chat(message: types.Message):
#     await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


# user get info about him
@dp.message_handler(
    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=["me"]
)
async def welcome(message: types.Message):
    if (
        message.chat.id != groupId
        and message.chat.id != testGroupId
        and message.chat.id != groupId2
    ):
        await message.reply("این گروه، گروه تایپولوژی نیست.")
    else:
        if message.from_user.username is None:
            await message.reply(
                f"Name - {message.from_user.full_name}\nID - {message.from_user.id}\n"
            )
        else:
            await message.reply(
                f"Name - {message.from_user.full_name}\n"
                f"ID - <code>{message.from_user.id}</code>\n"
                f"Username - @{message.from_user.username}\n"
            )


# ban user
@dp.message_handler(
    AdminFilter(is_chat_admin=True),
    IsReplyFilter(is_reply=True),
    commands=["بن"],
    commands_prefix="!",
    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP],
)
async def ban(message: types.Message):
    if (
        message.chat.id != groupId
        and message.chat.id != testGroupId
        and message.chat.id != groupId2
    ):
        await message.reply("این گروه، گروه تایپولوژی نیست.")
    else:
        replied_user = message.reply_to_message.from_user
        admin_id = message.from_user.id
        try:
            # Check if the bot is trying to ban itself
            if replied_user.id == (await bot.me).id:
                await bot.send_message(
                    chat_id=message.chat.id, text="من نمی‌توانم خودم را بن کنم."
                )
                return

            # Try to perform the ban
            await bot.kick_chat_member(chat_id=message.chat.id, user_id=replied_user.id)
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"کاربر "
                f"[{replied_user.full_name}](tg://user?id={replied_user.id})"
                f" توسط ادمین "
                f"[{message.from_user.full_name}](tg://user?id={admin_id})"
                f" بن شد.",
                parse_mode=types.ParseMode.MARKDOWN,
            )
        except ChatAdminRequired:
            # Handle the exception if the bot is not an admin or does not have enough rights to kick members
            await bot.send_message(
                chat_id=message.chat.id,
                text="من نمی‌توانم کاربر را بن کنم. لطفاً از دسترسی من اطمینان حاصل کنید.",
            )
        except UserIsAnAdministratorOfTheChat:
            # Handle the exception when trying to kick an administrator
            await bot.send_message(
                chat_id=message.chat.id, text="من نمی‌توانم یک ادمین را بن کنم."
            )


# unban user


# unban user
@dp.message_handler(
    AdminFilter(is_chat_admin=True),
    IsReplyFilter(is_reply=True),
    commands=["آنبن"],
    commands_prefix="!",
    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP],
)
async def unban(message: types.Message):
    if (
        message.chat.id != groupId
        and message.chat.id != testGroupId
        and message.chat.id != groupId2
    ):
        await message.reply("این گروه، گروه تایپولوژی نیست.")
    else:
        replied_user = message.reply_to_message.from_user
        admin_id = message.from_user.id
        try:
            # Check if the bot is trying to unban itself
            if replied_user.id == (await bot.me).id:
                await bot.send_message(
                    chat_id=message.chat.id, text="نمی توانم خودم را آنبن کنم."
                )
                return

            # Try to perform the unban
            await bot.unban_chat_member(
                chat_id=message.chat.id, user_id=replied_user.id
            )
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"کاربر "
                f"[{replied_user.full_name}](tg://user?id={replied_user.id})"
                f" توسط ادمین "
                f"[{message.from_user.full_name}](tg://user?id={admin_id})"
                f" آنبن شد.",
                parse_mode=types.ParseMode.MARKDOWN,
            )
        except ChatAdminRequired:
            # Handle the exception if the bot is not an admin or does not have enough rights to unban members
            await bot.send_message(
                chat_id=message.chat.id,
                text="من نمی‌توانم کاربر را بن کنم. لطفاً از دسترسی من اطمینان حاصل کنید.",
            )
        except UserIsNotABannedMemberOfTheChat:
            # Handle the exception when trying to unban a user who is not banned
            await bot.send_message(chat_id=message.chat.id, text="این کاربر بن نیست.")


# mute user in chat
@dp.message_handler(
    AdminFilter(is_chat_admin=True),
    IsReplyFilter(is_reply=True),
    commands=["میوت"],
    commands_prefix="!",
    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP],
)
async def mute(message: types.Message):
    if (
        message.chat.id != groupId
        and message.chat.id != testGroupId
        and message.chat.id != groupId2
    ):
        await message.reply("این گروه، گروه تایپولوژی نیست.")
    else:

        args = message.text.split()

        if len(args) > 1:
            till_date = message.text.split()[1]
        else:
            till_date = "نامتناهی"

        if till_date[-1] == "m":
            ban_for = int(till_date[:-1]) * 60
        elif till_date[-1] == "h":
            ban_for = int(till_date[:-1]) * 3600
        elif till_date[-1] == "d":
            ban_for = int(till_date[:-1]) * 86400
        else:
            ban_for = 60 * 60 * 24 * 365

        replied_user = message.reply_to_message.from_user
        admin_id = message.from_user.id

        try:
            # Check if the bot is trying to mute itself
            if replied_user.id == (await bot.me).id:
                await bot.send_message(
                    chat_id=message.chat.id, text="من نمی‌توانم خودم را میوت کنم."
                )
                return

            # Try to perform the mute
            now_time = int(time.time())
            await bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=replied_user.id,
                permissions=types.ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                ),
                until_date=now_time + ban_for,
            )
            await bot.send_message(
                text=f"کاربر "
                f"[{replied_user.full_name}](tg://user?id={replied_user.id})"
                f" به مدت "
                f"{till_date}"
                f" میوت شد.",
                chat_id=message.chat.id,
                parse_mode=types.ParseMode.MARKDOWN,
            )
        except CantRestrictSelf:
            # Handle the exception if the bot is trying to mute itself
            await bot.send_message(
                chat_id=message.chat.id, text="من نمی‌توانم خودم را میوت کنم."
            )
        except ChatAdminRequired:
            # Handle the exception if the bot is not an admin or does not have enough rights to restrict members
            await bot.send_message(
                chat_id=message.chat.id,
                text="من نمی‌توانم کاربر را میوت کنم. لطفاً از دسترسی من اطمینان حاصل کنید.",
            )
        except UserIsAnAdministratorOfTheChat:
            # Handle the exception when trying to mute an administrator
            await bot.send_message(
                chat_id=message.chat.id, text="من نمی‌توانم یک ادمین را میوت کنم."
            )


# unmute user in chat
@dp.message_handler(
    AdminFilter(is_chat_admin=True),
    IsReplyFilter(is_reply=True),
    commands_prefix="!",
    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP],
    commands=["آنمیوت"],
)
async def un_mute_user(message: types.Message):
    if (
        message.chat.id != groupId
        and message.chat.id != testGroupId
        and message.chat.id != groupId2
    ):
        await message.reply("این گروه، گروه تایپولوژی نیست.")
    else:

        replied_user = message.reply_to_message.from_user
        admin_id = message.from_user.id

        try:
            # Try to perform unmute
            await bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=replied_user.id,
                permissions=types.ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                ),
            )
            await bot.send_message(
                text=f"خب، "
                f"[{replied_user.full_name}](tg://user?id={replied_user.id})"
                f" اکنون می‌توانید در چت پیام بنویسید.",
                chat_id=message.chat.id,
                parse_mode=types.ParseMode.MARKDOWN,
            )
        except ChatAdminRequired:
            # Handle the exception if the bot is not an admin or does not have enough rights to restrict members
            await bot.send_message(
                chat_id=message.chat.id,
                text="من نمی‌توانم کاربر را آنمیوت کنم. لطفاً از دسترسی من اطمینان حاصل کنید.",
            )
        except UserIsAnAdministratorOfTheChat:
            # Handle the exception when trying to unmute an administrator
            await bot.send_message(
                chat_id=message.chat.id, text="من نمی‌توانم یک ادمین را آنمیوت کنم."
            )
        except CantRestrictSelf:
            # Handle the exception when trying to unmute itself
            await bot.send_message(
                chat_id=message.chat.id, text="من نمی‌توانم خودم را آنمیوت کنم."
            )


# pin chat message
@dp.message_handler(
    AdminFilter(is_chat_admin=True),
    IsReplyFilter(is_reply=True),
    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP],
    commands=["پین"],
    commands_prefix="!",
)
async def pin_message(message: types.Message):
    if (
        message.chat.id != groupId
        and message.chat.id != testGroupId
        and message.chat.id != groupId2
    ):
        await message.reply("این گروه، گروه تایپولوژی نیست.")
    else:
        msg_id = message.reply_to_message.message_id
        await bot.pin_chat_message(message_id=msg_id, chat_id=message.chat.id)


# unpin chat message
@dp.message_handler(
    AdminFilter(is_chat_admin=True),
    IsReplyFilter(is_reply=True),
    commands_prefix="!",
    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP],
    commands=["آنپین"],
)
async def unpin_message(message: types.Message):
    if (
        message.chat.id != groupId
        and message.chat.id != testGroupId
        and message.chat.id != groupId2
    ):
        await message.reply("این گروه، گروه تایپولوژی نیست.")
    else:
        msg_id = message.reply_to_message.message_id
        await bot.unpin_chat_message(message_id=msg_id, chat_id=message.chat.id)


# unpin all pins
@dp.message_handler(commands=["آنپین_همه"], is_chat_admin=True, commands_prefix="!")
async def unpin_all_messages(message: types.Message):

    if (
        message.chat.id != groupId
        and message.chat.id != testGroupId
        and message.chat.id != groupId2
    ):
        await message.reply("این گروه، گروه تایپولوژی نیست.")
    else:
        try:
            await bot.unpin_all_chat_messages(chat_id=message.chat.id)
        except Exception as e:
            print(f"An error occurred: {e}")


# delete user message
@dp.message_handler(
    AdminFilter(is_chat_admin=True),
    IsReplyFilter(is_reply=True),
    commands_prefix="!",
    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP],
    commands=["حذف"],
)
async def delete_message(message: types.Message):
    if (
        message.chat.id != groupId
        and message.chat.id != testGroupId
        and message.chat.id != groupId2
    ):
        await message.reply("این گروه، گروه تایپولوژی نیست.")
    else:
        msg_id = message.reply_to_message.message_id
        await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


# get chat admins list
@dp.message_handler(
    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP],
    commands=["ادمین"],
    commands_prefix="!/",
)
async def get_admin_list(message: types.Message):
    if (
        message.chat.id != groupId
        and message.chat.id != testGroupId
        and message.chat.id != groupId2
    ):
        await message.reply("این گروه، گروه تایپولوژی نیست.")
    else:
        admins = await message.chat.get_administrators()
        msg = str("ادمین:\n")

        for admin in admins:
            # {admin.user.id}
            msg += f"{admin.user.full_name}\n"

        await message.reply(msg, parse_mode=types.ParseMode.MARKDOWN)


# report about spam or something else
@dp.message_handler(
    chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP],
    commands=["گزارش"],
    commands_prefix="!/",
)
async def report_by_user(message: types.Message):
    if (
        message.chat.id != groupId
        and message.chat.id != testGroupId
        and message.chat.id != groupId2
    ):
        await message.reply("این گروه، گروه تایپولوژی نیست.")
    else:
        if message.reply_to_message is None:
            await message.reply(
                "شما در حال گزارش نامعتبر هستید. لطفاً به یک پیام ریپلای کنید."
            )
            return

        msg_id = message.reply_to_message.message_id
        user_id = message.from_user.id
        admins_list = await message.chat.get_administrators()

        for admin in admins_list:
            try:
                if message.chat.username:
                    group_link = f"https://t.me/{message.chat.username}/{msg_id}"
                else:
                    chat_id = str(message.chat.id)[2:]
                    group_link = f"https://t.me/c/{chat_id}/{msg_id}"

                await bot.send_message(
                    text=f"کاربر: {message.from_user.full_name}\n"
                    f"گزارش درباره پیام زیر:\n"
                    f"[پیام گزارش شده]({group_link})",
                    chat_id=admin.user.id,
                    parse_mode=types.ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )

            except Exception as e:
                logging.debug(f"امکان ارسال گزارش وچود ندارد.\n" f"{e}")

        await message.reply("گزارش شما به ادمین‌های تایپولوژی ارسال شد، ممنون!")


# # delete links and tags from users, allow for admins
# @dp.message_handler(AdminFilter(is_chat_admin=True), content_types=['text'])
# async def delete_links(message: types.Message):
#     for entity in message.entities:
#         if entity.type in ["url", "text_link", "mention"]:
#             await bot.delete_message(message.chat.id, message.message_id)


#################<-CHATGPT->###################

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = openai.OpenAI()

# Define a cooldown period (e.g., 10 seconds)
ChatGPT_cooldown_period = timedelta(seconds=10)
# Initialize a variable to store the time when the bot becomes available to process the next command
next_available_time = datetime.now()


@dp.message_handler(
    lambda message: message.text.startswith("/chat")
    and (
        message.chat.id == groupId
        or message.chat.id == testGroupId
        or message.chat.id == groupId2
    )
)
async def chat_handler(message: types.Message):
    global next_available_time
    current_time = datetime.now()

    # Check if the bot is currently processing another command
    if current_time < next_available_time:
        # If so, inform the user to wait until the bot is available again
        wait_seconds = (next_available_time - current_time).total_seconds()
        await message.reply(
            f"درخواست شما لغو شد. بعد از "
            f"{wait_seconds:.0f}"
            f" ثانیه دوباره تلاش کنید."
        )
        return

    # Extract the user's message after "/chat"
    user_message = message.text[len("/chat") :].strip()
    if user_message:
        # Set the next available time to the current time plus the cooldown period
        next_available_time = current_time + ChatGPT_cooldown_period

        # Inform the user that the request is being processed
        processing_message = await message.reply("در حال پردازش. لطفا صبر کنید...")

        try:
            # Call OpenAI API to generate a response
            response = openai.Completion.create(
                model="gpt-3.5-turbo",
                prompt=user_message,
                temperature=1,
                max_tokens=150,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            # Send the generated response to the user
            await processing_message.delete()
            await message.reply(
                text=response.choices[0].text.strip(), parse_mode=ParseMode.MARKDOWN
            )
        except openai.error.OpenAIError as e:
            # If there's an OpenAI error, handle it and log it
            next_available_time = datetime.now()  # Reset cooldown
            await processing_message.edit_text("درخواست شما با خطا مواجه شد.")
            print(f"OpenAI Error: {e}")
        except Exception as e:
            # If there's a general error, handle it and log it
            await processing_message.edit_text("درخواست شما با خطا مواجه شد.")
            print(f"General Error: {e}")
    else:
        await message.reply("لطفا با دستور /chat درخواست خود را وارد کنید.")


# Polling
if __name__ == "__main__":
    executor.start_polling(dp, on_startup=send_adm, skip_updates=True)
