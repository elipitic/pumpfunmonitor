from solders.pubkey import Pubkey
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