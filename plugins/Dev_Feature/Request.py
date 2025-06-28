# This code has been modified by @Safaridev
# Please do not remove this credit
from fuzzywuzzy import process
from imdb import IMDb
from utils import temp
from info import REQ_CHANNEL, GRP_LNK
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import get_search_results, get_all_files

imdb = IMDb()

async def ai_spell_check(chat_id, wrong_name):
    try:  
        async def search_movie(wrong_name):
            search_results = imdb.search_movie(wrong_name)
            movie_list = [movie['title'] for movie in search_results]
            return movie_list

        movie_list = await search_movie(wrong_name)

        if not movie_list:
            return None

        for _ in range(5):
            closest_match = process.extractOne(wrong_name, movie_list)

            if not closest_match or closest_match[1] <= 80:
                return None

            movie = closest_match[0]
            files, offset, total_results = await get_search_results(chat_id=chat_id, query=movie)

            if files:
                return movie

            movie_list.remove(movie)

        return None

    except Exception as e:
        print(f"Error in ai_spell_check: {e}")
        return None


@Client.on_message(filters.command(["request", "Request"]) & filters.private | filters.regex("#request") | filters.regex("#Request"))
async def requests(client, message):
    search = message.text
    requested_movie = search.replace("/request", "").replace("/Request", "").strip()
    user_id = message.from_user.id

    if not requested_movie:
        await message.reply_text("🙅 (ஒரு திரைப்படத்தைக் கோர, தயவுசெய்து படத்தின் பெயரையும் வருடத்தையும் எழுதுங்கள்\nஇது போன்ற ஒன்றை எழுதுங்கள். 👇\n<code>/request Pushpa 2021</code>")
        return

    files, offset, total_results = await get_search_results(chat_id=message.chat.id, query=requested_movie)

    if files: 
        file_name = files[0]['file_name']
        await message.reply_text(f"🎥 {file_name}\n\nநீங்கள் கோரிய திரைப்படம் குழுவில் கிடைக்கிறது\n\nகுழு இணைப்பில் = {GRP_LNK}")
    else:
        closest_movie = await ai_spell_check(chat_id=message.chat.id, wrong_name=requested_movie)
        if closest_movie:
            files, offset, total_results = await get_search_results(chat_id=message.chat.id, query=closest_movie)
            if files:
                file_name = files[0]['file_name']
                await message.reply_text(f"🎥 {file_name}\n\nநீங்கள் கோரிய திரைப்படம் குழுவில் கிடைக்கிறது\n\nகுழு இணைப்பில் = {GRP_LNK}")
            else:
                await message.reply_text(f"✅ உங்கள் திரைப்படம் <b>{closest_movie}</b> இது எங்கள் நிர்வாகிக்கு அனுப்பப்பட்டுள்ளது.\n\n🚀 படம் பதிவேற்றப்பட்டவுடன் நாங்கள் உங்களுக்கு செய்தி அனுப்புவோம்.\n\n📌 குறிப்பு - நிர்வாகி தனது வேலையில் மும்முரமாக இருப்பதால் படம் பதிவேற்றம் செய்ய நேரம் ஆகலாம்.")
                await client.send_message(
                    REQ_CHANNEL,
                    f"☏ #𝙍𝙀𝙌𝙐𝙀𝙎𝙏𝙀𝘿_𝘾𝙊𝙉𝙏𝙀𝙉𝙏 ☎︎\n\nʙᴏᴛ - {temp.B_NAME}\nɴᴀᴍᴇ - {message.from_user.mention} (<code>{message.from_user.id}</code>)\nRᴇǫᴜᴇꜱᴛ - <code>{closest_movie}</code>",
                    reply_markup=InlineKeyboardMarkup(
                        [[
                            InlineKeyboardButton('ɴᴏᴛ ᴏᴛᴛ ʀᴇʟᴇᴀsᴇ 📅', callback_data=f"not_release:{user_id}:{requested_movie}"),
                            InlineKeyboardButton('ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ 🙅', callback_data=f"not_available:{user_id}:{requested_movie}")
                        ],[
                            InlineKeyboardButton('ᴜᴘʟᴏᴀᴅᴇᴅ ✅', callback_data=f"uploaded:{user_id}:{requested_movie}")
                        ],[
                            InlineKeyboardButton('ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ🙅', callback_data=f"series:{user_id}:{requested_movie}"),
                            InlineKeyboardButton('sᴇʟʟ ᴍɪsᴛᴇᴋ✍️', callback_data=f"spelling_error:{user_id}:{requested_movie}")
                        ],[
                            InlineKeyboardButton('⦉ ᴄʟᴏsᴇ ⦊', callback_data=f"close_data")]
                        ])
                )
        else:
            await message.reply_text(f"✅ உங்கள் திரைப்படம் <b>{requested_movie}</b> இது எங்கள் நிர்வாகிக்கு அனுப்பப்பட்டுள்ளது.\n\n🚀 படம் பதிவேற்றப்பட்டவுடன் நாங்கள் உங்களுக்கு செய்தி அனுப்புவோம்.\n\n📌 குறிப்பு - நிர்வாகி தனது வேலையில் மும்முரமாக இருப்பதால் படம் பதிவேற்றம் செய்ய நேரம் ஆகலாம்.")
            await client.send_message(
                REQ_CHANNEL,
                f"📝 #REQUESTED_CONTENT 📝\n\nʙᴏᴛ - {temp.B_NAME}\nɴᴀᴍᴇ - {message.from_user.mention} (<code>{message.from_user.id}</code>)\nRᴇǫᴜᴇꜱᴛ - <code>{requested_movie}</code>",
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton('ɴᴏᴛ ᴏᴛᴛ ʀᴇʟᴇᴀsᴇ 📅', callback_data=f"not_release:{user_id}:{requested_movie}"),
                        InlineKeyboardButton('ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ 🙅', callback_data=f"not_available:{user_id}:{requested_movie}")
                    ],[
                        InlineKeyboardButton('ᴜᴘʟᴏᴀᴅᴇᴅ ✅', callback_data=f"uploaded:{user_id}:{requested_movie}")
                    ],[
                        InlineKeyboardButton('ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ🙅', callback_data=f"series:{user_id}:{requested_movie}"),
                        InlineKeyboardButton('sᴇʟʟ ᴍɪsᴛᴇᴋ✍️', callback_data=f"spelling_error:{user_id}:{requested_movie}")
                    ],[
                        InlineKeyboardButton('⦉ ᴄʟᴏsᴇ ⦊', callback_data=f"close_data")]
                    ])
            )
