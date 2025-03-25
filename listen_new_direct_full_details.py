import asyncio
import json
import websockets
import base58
import base64
import struct
from solders.pubkey import Pubkey
from utils.logger import get_logger
from utils.noticer import send_new_coin_notice
from utils.supabase_utils import insert_new_coin
import datetime


logger = get_logger(__name__)
from config import (
    WSS_ENDPOINT, 
    PUMP_PROGRAM,
    SYSTEM_TOKEN_PROGRAM as TOKEN_PROGRAM_ID,
    SYSTEM_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM as ATA_PROGRAM_ID
)

def find_bonding_curve(mint: Pubkey) -> Pubkey:
    derived_address, _ = Pubkey.find_program_address(
        [
            bytes("bonding-curve".encode()),
            bytes(mint),
        ],
        PUMP_PROGRAM
    )
    return derived_address

def find_associated_bonding_curve(mint: Pubkey, bonding_curve: Pubkey) -> Pubkey:
    """
    Find the associated bonding curve for a given mint and bonding curve.
    This uses the standard ATA derivation.
    """
    derived_address, _ = Pubkey.find_program_address(
        [
            bytes(bonding_curve),
            bytes(TOKEN_PROGRAM_ID),
            bytes(mint),
        ],
        ATA_PROGRAM_ID
    )
    return derived_address

# Load the IDL JSON file
with open('./idl/pump_fun_idl.json', 'r') as f:
    idl = json.load(f)

# Extract the "create" instruction definition
create_instruction = next(instr for instr in idl['instructions'] if instr['name'] == 'create')

async def parse_create_instruction(data):
    if len(data) < 8:
        return None
    offset = 8
    parsed_data = {}
    # parsed_data['timestamp'] = datetime.datetime.now()
    # Parse fields based on CreateEvent structure
    fields = [
        ('name', 'string'),
        ('symbol', 'string'),
        ('uri', 'string'),
        ('mint', 'publicKey'),
        ('bondingCurve', 'publicKey'),
        ('user', 'publicKey'),
    ]

    try:
        for field_name, field_type in fields:
            if field_type == 'string':
                length = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                value = data[offset:offset+length].decode('utf-8')
                offset += length
            elif field_type == 'publicKey':
                value = base58.b58encode(data[offset:offset+32]).decode('utf-8')
                offset += 32

            parsed_data[field_name] = value
        logger.info(f"New token: {parsed_data}")
        await send_new_coin_notice(parsed_data["name"])
        insert_data = {}
        for key in parsed_data.keys():
            insert_data[key.lower()] = parsed_data[key]
        insert_new_coin(insert_data)
        return parsed_data
    except:
        return None

def print_transaction_details(log_data):
    logger.info(f"Signature: {log_data.get('signature')}")
    
    for log in log_data.get('logs', []):
        if log.startswith("Program data:"):
            try:
                data = base58.b58decode(log.split(": ")[1]).decode('utf-8')
                logger.info(f"Data: {data}")
            except:
                pass

async def listen_for_new_tokens():
    while True:
        try:
            async with websockets.connect(WSS_ENDPOINT) as websocket:
                subscription_message = json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "logsSubscribe",
                    "params": [
                        {"mentions": [str(PUMP_PROGRAM)]},
                        {"commitment": "processed"}
                    ]
                })
                await websocket.send(subscription_message)
                logger.info(f"Listening for new token creations from program: {PUMP_PROGRAM}")

                # Wait for subscription confirmation
                response = await websocket.recv()
                logger.info(f"Subscription response: {response}")

                while True:
                    try:
                        response = await websocket.recv()
                        data = json.loads(response)

                        if 'method' in data and data['method'] == 'logsNotification':
                            log_data = data['params']['result']['value']
                            logs = log_data.get('logs', [])
                            
                            if any("Program log: Instruction: Create" in log for log in logs):
                                for log in logs:
                                    if "Program data:" in log:
                                        try:
                                            encoded_data = log.split(": ")[1]
                                            decoded_data = base64.b64decode(encoded_data)
                                            parsed_data = await parse_create_instruction(decoded_data)
                                            if parsed_data and 'name' in parsed_data:
                                                logger.info("Signature:", log_data.get('signature'))
                                                for key, value in parsed_data.items():
                                                    logger.info(f"{key}: {value}")
                                                
                                                # Calculate associated bonding curve
                                                mint = Pubkey.from_string(parsed_data['mint'])
                                                bonding_curve = Pubkey.from_string(parsed_data['bondingCurve'])
                                                associated_curve = find_associated_bonding_curve(mint, bonding_curve)
                                                logger.info(f"Associated Bonding Curve: {associated_curve}")
                                                logger.info("##########################################################################################")
                                        except Exception as e:
                                            logger.info(f"Failed to decode: {log}")
                                            logger.info(f"Error: {str(e)}")

                    except Exception as e:
                        logger.info(f"An error occurred while processing message: {e}")
                        break

        except Exception as e:
            logger.info(f"Connection error: {e}")
            logger.info("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(listen_for_new_tokens())