from telethon import TelegramClient

from config import *

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
bot.disconnect()
bot = TelegramClient('bot', api_id, api_hash)

async def send_files(user, files):
  if not bot.is_connected():
    await bot.connect()

  i = 0
  while i < len(files):
    try:
      await bot.send_file(user, files[i])
      i+=1
    except:
      continue