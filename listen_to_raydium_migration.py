import websockets
import asyncio
import json
import base64
from solders.pubkey import Pubkey
from utils.noticer import send_migration_notice
from utils.supabase_utils import insert_new_coin
import sys
import os


from utils.logger import get_logger
from config import WSS_ENDPOINT, PUMP_LIQUIDITY_MIGRATOR

logger = get_logger(__name__)

def process_initialize2_transaction(data):
    """Process and decode an initialize2 transaction"""
    try:
        signature = data['transaction']['signatures'][0]
        account_keys = data['transaction']['message']['accountKeys']
        
        # Check raydium_amm_idl.json for the account keys
        # The token address is typically the 19th account (index 18)
        # The liquidity pool address is typically the 3rd account (index 2)
        if len(account_keys) > 18:
            token_address = account_keys[18]
            liquidity_address = account_keys[2]
            send_migration_notice(liquidity_address)
            logger.info(f"\nSignature: {signature}")
            logger.info(f"Token Address: {token_address}")
            logger.info(f"Liquidity Address: {liquidity_address}")
            logger.info("=" * 50)
        else:
            logger.error(f"\nError: Not enough account keys (found {len(account_keys)})")
        
    except Exception as e:
        logger.error(f"\nError: {str(e)}")

async def listen_for_events():
    while True:
        try:
            async with websockets.connect(WSS_ENDPOINT) as websocket:
                subscription_message = json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "blockSubscribe",
                    "params": [
                        {"mentionsAccountOrProgram": str(PUMP_LIQUIDITY_MIGRATOR)},
                        {
                            "commitment": "confirmed",
                            "encoding": "json",
                            "showRewards": False,
                            "transactionDetails": "full",
                            "maxSupportedTransactionVersion": 0
                        }
                    ]
                })
                
                await websocket.send(subscription_message)
                response = await websocket.recv()
                logger.info(f"Subscription response: {response}")
                logger.info("\nListening for Raydium pool initialization events...")

                while True:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=30)
                        data = json.loads(response)
                        
                        if 'method' in data and data['method'] == 'blockNotification':
                            if 'params' in data and 'result' in data['params']:
                                block_data = data['params']['result']
                                if 'value' in block_data and 'block' in block_data['value']:
                                    block = block_data['value']['block']
                                    if 'transactions' in block:
                                        for tx in block['transactions']:
                                            logs = tx.get('meta', {}).get('logMessages', [])
                                            
                                            # Check for initialize2 instruction
                                            for log in logs:
                                                if "Program log: initialize2: InitializeInstruction2" in log:
                                                    logger.info("Found initialize2 instruction!")
                                                    process_initialize2_transaction(tx)
                                                    break
                                        
                    except asyncio.TimeoutError:
                        logger.error("\nChecking connection...")
                        logger.error("Connection alive")
                        continue
                        
        except Exception as e:
            logger.error(f"\nConnection error: {str(e)}")
            logger.error("Retrying in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(listen_for_events())