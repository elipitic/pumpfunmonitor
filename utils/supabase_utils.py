from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from utils.logger import get_logger

logger = get_logger(__name__)

supabase: Client = create_client(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)


def insert_new_coin(coin_info):
    try:
        supabase.table("new_coins").insert(coin_info).execute()
        logger.info(f"Inserted new coin: {coin_info}")
    except Exception as err:
        logger.error(f"Error inserting new coin: {str(err)}")
        return False
    
def insert_new_raydium(coin_info):
    try:
        supabase.table("raydium").insert(coin_info).execute()
        logger.info(f"Inserted new coin: {coin_info}")
    except Exception as err:
        logger.error(f"Error inserting new coin: {str(err)}")
        return False