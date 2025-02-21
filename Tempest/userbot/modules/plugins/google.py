import os
import re
import time
import json
import random
import asyncio
import shutil
import urllib
import requests
import http.cookiejar

from bs4 import BeautifulSoup
from bing_image_downloader import downloader as bing_downloader
from pyrogram.types import Message

from Tempest import app, gen




app.CMD_HELP.update(
    {"google" : (
        "google",
        {
        "img [number of pic] [query]" : "uploads searched images on telegram using bing.com",
        "sauce [reply to pic]" : "Get the source link of that image",
        "pic [query]" : "Get Images from @bing bot.",
        }
        )
    }
)




search_url = "http://www.google.com"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
}

def get_soup(url,header):
    return BeautifulSoup(urllib.request.urlopen(urllib.request(url,headers=header)),'html.parser')




@app.on_message(gen("sauce", exclude =["sudo"]))
async def imagesauce_handler(_, m: Message):
    try:
        reply = m.reply_to_message
        if not reply:
            return await app.send_edit("Reply to some media.", text_type=["mono"], delme=4)

        if reply.photo:
            await app.send_edit("⏳ • Hold on ...")
            savename = "photo_{}_{}.png".format(
                reply.photo.file_id, 
                reply.photo.date
                )
            await app.download_media(
                reply,
                file_name="./downloads/" + savename
                )
        elif reply.animation:
            await app.send_edit("⏳ • Hold on ...")
            savename = "giphy_{}-{}.gif".format(
                reply.animation.date,
                reply.animation.file_size
                )
            await app.download_media(
                reply,
                file_name="./downloads/" + savename
                )
        else:
            return await app.send_edit("Only photo & animation media's are supported.", text_type=["mono"], delme=4)

        searchUrl = 'http://www.google.co.id/searchbyimage/upload'
        filePath = './downloads/{}'.format(savename)
        multipart = {'encoded_image': (filePath, open(filePath, 'rb')), 'image_content': ''}
        response = requests.post(searchUrl, files=multipart, exclude_redirects=False)
        fetchUrl = response.headers['Location']
        await app.send_edit("Results: [Tap Here]({})".format(fetchUrl), disable_web_page_preview = True)
    except Exception as e:
        await app.error(e)




@app.on_message(gen("pic", exclude =["sudo"]))
async def yandeximages_handler(_, m: Message):
    if app.long() == 1:
        return await app.send_edit("Usage: `.pic cat`", delme=4)

    try:
        if app.long() > 1:
            await app.send_edit("Getting image . . .", text_type=["mono"])
            photo = m.text.split(None, 1)[1]
            result = await app.get_inline_bot_results(
                "@pic", 
                photo
            )
            await m.delete()
            saved = await app.send_inline_bot_result(
                m.chat.id, 
                query_id=result.query_id, 
                result_id=result.results[random.randint(0, len(result.results))].id, 
            )
        else:
            await app.send_edit("Failed to get the image, try again later !", text_type=["mono"], delme=4)
    except Exception as e:
        await app.error(e)




@app.on_message(gen("img", exclude =["sudo"]))
async def imagesearch_handler(_, m: Message):
    cmd = m.command
    if app.long() == 1:
        return await app.send_edit("Please give me some query.", text_type=["mono"], delme=4)

    if app.long() > 2 and cmd[1].isdigit():
        limit = int(cmd[1])
        query = m.text.split(None, 2)[2]
    else:
        limit = 3 # default
        query = m.text.split(None, 1)[1]

    try:
        await app.send_edit(f"**Getting images:** `{query}`")
        bing_downloader.download(query, limit=limit,  output_dir="images", adult_filter_off=True, force_replace=False, timeout=60, verbose=False)
        img_dir = os.path.exists("./images")

        if img_dir:
            for img in os.listdir(f"./images/{query}"):
                await app.send_photo(m.chat.id, f"./images/{query}/{img}")
        else:
            await app.send_edit("No images found !", text_type=["mono"], delme=4)

        if os.path.exists(f"./images/{query}/"):
            shutil.rmtree(f"./images") # remove folder

        await m.delete()

    except Exception as e:
        await app.error(e)


