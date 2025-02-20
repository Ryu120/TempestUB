import os
import time
import math
import asyncio

from functools import partial
from datetime import datetime

from pyrogram.types import (
    Message, 
    User, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
    )

from pyrogram.raw import functions
from pyrogram.errors import PeerIdInvalid

from Tempest import app, gen



date_dict = []




app.CMD_HELP.update(
    {"profile" : (
        "profile",
        {
        "whois [reply to message]" : "get a small piece of information of a user.",
        "id" : "Get chat or user id",
        "block [username] or [reply to user]" : "Block a user from sending message in your pm.",
        "unblock [username] or [reply to user]" : "Unblock a user and exclude him to send messages in your pm.",
        "repo" : "Get Tempest Userbot official repository link.",
        "rem [lname] | [bio] | [pfp] | [uname]" : "Remove last name or username from profile.",
        "set [fname] | [lname ] | [uname] | [bio] & [text]" : "Choose a option from command and set anything in your profile.",
        "uinfo [reply to user]" : "Get Full Info Of A Specific User.\nThis Command Includes More Details.",
        "sc [reply to user]" : "Find Out Groups Of A Specific User, Reply To That User. @tgscanrobot",
        "sg [reply to user]" : "Get name & username history of a particular user in groups or private chats. @sangmatainfo_bot",
        "men [username] [text]" : "Mention a user in a specific text.",
        }
        )
    }
)




men = partial("<a href='tg://user?id={}'>{}</a>".format)


infotext = """
**NAME:** `{}`
**USER ID:** `{}`
**Mention:** [{}](tg://user?id={})
**USERNAME:** {}
**DC ID:** `{}`
"""




def FullName(user: User):
    return user.first_name + " " + user.last_name if user.last_name else user.first_name




@app.on_message(gen("whois", exclude = ["sudo"]))
async def whois(_, m: Message):
    reply = m.reply_to_message
    cmd = m.command
    await app.send_edit("Finding details . . .", text_type=["mono"])

    if reply:
        get_user = reply.from_user.id
    elif not reply and app.long() > 1:
        get_user = cmd[1]
    else:
        get_user = None

    try:
        if get_user:
            user = await app.get_users(get_user)
    except PeerIdInvalid:
        return await app.send_edit("I don't know that User.", text_type=["mono"], delme=3)

    async for x in app.get_chat_photos(user.id):
        pfp = x.file_id
        break

    if not pfp:
        await app.send_edit(
            infotext.format(
                FullName(user),
                user.id,
                user.first_name,
                user.id,
                f"@{user.username}" if user.username else "",
                user.dc_id
            ),
        disable_web_page_preview=True,
        )
    else:
        await app.send_cached_media(
            m.chat.id, 
            file_id = pfp,
            caption=infotext.format(
                FullName(user),
                user.id,
                user.first_name,
                user.id,
                f"@{user.username}" if user.username else  "",
                user.dc_id
            )
        )
        await m.delete()




@app.on_message(gen("id", exclude = ["sudo"]))
async def id(_, m: Message):
    await app.send_edit("Getting id . . .", text_type=["mono"])
    cmd = m.command
    reply = m.reply_to_message

    if not reply and len(cmd) == 1:
        get_user = m.from_user.id
    elif reply and len(cmd) == 1:
        get_user = reply.from_user.id
    elif len(cmd) > 1:
        get_user = cmd[1]

    try:
        user = await app.get_users(get_user)
        chat = await app.get_chat(m.chat.id)
    except PeerIdInvalid:
        return await app.send_edit("I don't know that User.", text_type=["mono"])

    u_name = user.first_name if user.first_name else None
    c_name = chat.first_name if chat.first_name else chat.title

    await app.send_edit(f"**{u_name}:** `{user.id}`\n**{c_name}:** `{chat.id}`")




@app.on_message(gen(["men", "mention"], exclude = ["sudo"]))
async def mention_user(_, m: Message):
    if app.long() < 3:
        return await app.send_edit("Incorrect command use.\n\n**Example** : `.men @beastzx Tronuserbot`")

    try:
        user = await app.get_users(m.command[1])
    except Exception as e:
        await app.send_edit("User not found !", text_type=["mono"])
        return await app.error(e)

    mention = men(user.id, " ".join(m.command[2:]))
    await app.send_edit(mention)




@app.on_message(gen("uinfo", exclude = ["sudo"]))
async def get_full_user_info(_, m: Message):
    await app.send_edit("scrapping info . . .", text_type=["mono"])
    reply = m.reply_to_message

    if reply:
        user = reply.from_user
    elif not reply:
        user = m.from_user

    p_id = False

    async for x in app.get_chat_photos(user.id):
        p_id = x.file_id
        

    try:
        duo = f"**1. ID:** `{user.id}`\n"
        duo += f"**2. NAME:** `{user.first_name}`\n"
        duo += f"**3. DC ID:** `{user.dc_id}`\n"
        duo += f"**4. BOT:** `{user.is_bot}`\n"
        duo += f"**5. NAME:** `{user.first_name}`\n"
        duo += f"**6. STATUS:** `{user.status}`\n"
        duo += f"**7. RESTRICTED:** `{user.is_restricted}`\n"

        if p_id:
            await app.send_cached_media(
                m.chat.id, 
                file_id=p_id, 
                caption=duo
            )
            await m.delete()
        elif p_id is False:
            await app.send_edit(duo)
    except Exception as e:
        await app.send_edit("Some error occured !", text_type=["mono"])
        await app.error(e)




@app.on_message(gen(["sc", "scan"], exclude = ["sudo"]))
async def tgscan_handler(_, m: Message):
    if m.reply_to_message:
        await app.send_edit("Checking database . . .")
        await app.forward_messages(
            "@tgscanrobot", 
            m.chat.id, 
            m.reply_to_message.id
            )
        time.sleep(0.5)
        msg = await app.get_chat_history(
            "@tgscanrobot", 
            limit=1
            )
        if msg:
            user = "**INFO: **" + msg[0].text.split("\n\n1. ")[0]
            await app.send_edit(user)
        else:
            await app.send_edit("No information found !", text_type=["mono"])

    else:
        await app.send_edit("reply to someone's message . . .", delme=3, text_type=["mono"])




@app.on_message(gen("block", exclude = ["sudo"]))
async def block_handler(_, m: Message):
    reply = m.reply_to_message

    if app.long() >= 2 and not reply:
        user = m.command[1]
        try:
            await app.block_user(user)
            await app.send_edit("Blocked User 🚫", text_type=["mono"], delme=3)
        except Exception as e:
            await app.error(e)
    elif reply:
        user = reply.from_user.id
        try:
            await app.block_user(user)
            await app.send_edit("Blocked User 🚫", text_type=["mono"], delme=3)
        except Exception as e:
            await app.error(e)




@app.on_message(gen("unblock", exclude = ["sudo"]))
async def unblock_handler(_, m: Message):
    reply = m.reply_to_message

    if app.long() >= 2 and not reply:
        user = m.command[1]
        try:
            await app.unblock_user(user)
            await app.send_edit("Unblocked User 🎉", text_type=["mono"], delme=3)
        except Exception as e:
            await app.error(e)
    elif reply:
        user = reply.from_user.id
        try:
            await app.unblock_user(user)
            await app.send_edit("Unblocked User 🎉", text_type=["mono"], delme=3)
        except Exception as e:
            await app.error(e)




@app.on_message(gen("sg", exclude = ["sudo"]))
async def usernamehistory_handler(_, m: Message):
    reply = m.reply_to_message

    if not reply:
        await app.send_edit("Reply to a user to get history of name / username.", text_type=["mono"], delme=2)

    elif reply:
        await app.send_edit("Checking History . . .", text_type=["mono"])
        await app.forward_messages(
            "@SangMataInfo_bot", 
            m.chat.id, 
            reply.id
            )
        is_no_record = False
        for x in range(8):
            time.sleep(1)
            msg = await app.get_chat_history(
                "@SangMataInfo_bot", 
                limit=3
                )
            if msg[0].text == "No records found":
                await app.send_edit("No records found")
                is_no_record = True
                await app.read_chat_history("@SangMataInfo_bot")
                break
            if msg[0].from_user.id == 461843263 and msg[1].from_user.id == 461843263 and msg[2].from_user.id == 461843263:
                await app.read_chat_history("@SangMataInfo_bot")
                break
            else:
                print("Failed, try again ({})".format(x+1))
                continue
        if is_no_record:
            return
        history_name = "1. " + msg[2].text.split("\n\n1. ")[1]
        username_history = "1. " + msg[1].text.split("\n\n1. ")[1]
        text = "**Name History for** [{}](tg://user?id={}) (`{}`)\n\n".format(m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.id, m.reply_to_message.from_user.id) + history_name
        if app.textlen() <= 4096 and len(text) + len("\n\n**Username History**\n\n") + len(username_history) <= 4906:
            text += "\n\n**Username History**\n\n" + username_history
            await app.send_edit(text)
        else:
            await app.send_edit(text)
            await app.send_edit("\n\n**Username History**\n\n" + username_history)




@app.on_message(gen("set"))
async def setprofile_handler(_, m: Message):
    cmd = m.command

    if app.long() < 3:
        return await app.send_edit("Please use text and suffix after command suffix: `fname`, `lname`, `bio`, `uname`")

    # set -> fname, lname, bio & uname
    if app.long() > 2:
        text = m.text.split(None, 2)[2]

        if cmd[1] in ["fname", "lname", "bio"]:
            await setprofile(m, cmd[1], text)
        elif cmd[1] in ["uname"]:
            await app.update_username(text)

    else:
        return await app.send_edit(f"Please specify a correct suffix.", text_type=["mono"], delme=3)




@app.on_message(gen("rem"))
async def remprofile_handler(_, m: Message):
    if app.long() > 1:
        cmd = m.command

    elif app.long(m) == 1:
        return await app.send_edit("what do you want to remove ? suffix: `lname`, `bio`, `pfp`, `uname`", delme=3)

    try:
        if cmd[1] in ["lname", "bio", "pfp", "uname"]:
            await rmprofile(m, cmd[1])
        else:
            await app.send_edit("please use from the list:\n\n`lname`\n`bio`\n`pfp`\n`uname`", delme=3)
    except Exception as e:
        await app.error(e)




# set your profile stuffs 
async def setprofile(m: Message, mode, kwargs):
    # set first name
    if mode == "fname":
        try:
            await app.update_profile(
                first_name = f"{kwargs}"
                )
            await app.send_edit(
                f"✅ Updated first name to [ {kwargs} ]"
                )
        except Exception as e:
            await app.error(e)
    # set last name
    elif mode == "lname":
        try:
            await app.update_profile(
                last_name = f"{kwargs}"
            )
            await app.send_edit(
                f"✅ Updated last name to [ {kwargs} ]"
                )
        except Exception as e:
            await app.error(e)
    # set bio
    elif mode == "bio":
        try:
            await app.update_profile(
                bio = f"{kwargs}"
                )
            await app.send_edit(
                f"✅ Updated bio to [ {kwargs}]"
                )
        except Exception as e:
            await app.error(e)
    else:
        await app.send_edit("Please give correct format.", delme=2)




# lost everything
async def rmprofile(m: Message, args):
    # delete last name
    if args == "lname":
        await app.update_profile(
            last_name = ""
            )
        await app.send_edit(
            "✅ Removed last name from profile."
            )
    # delete bio
    elif args == "bio":
        await app.update_profile(
            bio = "")
        await app.send_edit(
            "✅ Removed bio from profile."
            )
    # delete profile picture
    elif args == "pfp":
        photos = await app.get_profile_photos("me")
        if photos:
            await app.delete_profile_photos([p.file_id for p in photos[1:]])
            await app.send_edit(
                "✅ Deleted all photos from profile."
                )
        else:
            await app.send_edit("❌ There are no photos in your profile.")
    # delete username
    elif args == "uname":
        await app.update_username("")
        await app.send_edit(
            "✅ Removed username from profile."
            )
    else:
        await app.send_edit("Give correct format.", delme=3)




@app.on_message(gen("repo", exclude = ["sudo"]))
async def repolink_handler(_, m: Message):
    await app.send_edit("**Tempest UB Repo: [Press Here](https://github.com/TempestNetwork/TempestUB)**", disable_web_page_preview=True)


