import asyncio
import telegram
from config import BOT_TOKEN, CHAT_ID


async def send_new_coin_notice(coin_name):
    bot = telegram.Bot(BOT_TOKEN)
    async with bot:
        await bot.send_message(chat_id=CHAT_ID,text=f'{coin_name} has been mint!')

async def send_migration_notice(coin_name):
    bot = telegram.Bot(BOT_TOKEN)
    async with bot:
        await bot.send_message(chat_id=CHAT_ID,text=f'{coin_name} has been migrate to raydium!')