#!/usr/bin/env python3
"""
Binance Hack Transaction Decoder
Fetches and decodes key transactions from the hack.
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

# ============================================================
# KEY TRANSACTION HASHES (to be filled from on-chain data)
# ============================================================

# These need to be populated from Etherscan/BSCScan/Arbiscan
KEY_TXS = {
    "ethereum": {
        "eip7702_delegation": None,      # ~block 26300791, 20:20:59 UTC
        "main_sweep": None,              # ~block 26300803, 20:24:23 UTC  
        "binance16_transfer": None,      # ~block 26300804, 20:24:47 UTC
        "eth_forward": None,             # ~block 26300818, 20:39 UTC
        "hotwallet34_usdc": None,        # ~block 26300946, 20:41 UTC
    },
    "bsc": {},
    "arbitrum": {},
    "polygon": {},
    "optimism": {}
}

# ============================================================
# ADDRESS MAPPING (full addresses from research)
# ============================================================

ADDRESSES = {
    "binance_14": "0x28C6c06298d514Db089934071355E5743bf21d60",
    "binance_16": "0xDFd5293D8e347dFe59E90eFd55b2956a1343963d",
    "hot_wallet_34": "0xEe7aE85f2Fe2239E27D9c1E23fFFe168D63b4055",
    "attacker_eoa": "0x7C86...5CA0",  # Need full
    "attacker_contract": "0x63e842B0...6fAe",  # Need full
    "exploiter_2": "0x5227...CB2f8c",  # Need full
    "exploiter_3": "0x8532...43D4",   # Need full
}

# ============================================================
# RPC ENDPOINTS
# ============================================================

RPCS = {
    "ethereum": "https://eth.drpc.org",
    "bsc": "https://bsc.drpc.org",
    "arbitrum": "https://arb1.drpc.org",
    "polygon": "https://polygon.drpc.org",
    "optimism": "https://optimism.drpc.org",
}

# ============================================================
# EIP-7702 DELEGATION DECODING
# ============================================================

# EIP-7702 AUTH transaction (type 0x04) structure:
# - chain_id
# - nonce
# - max_priority_fee_per_gas
# - max_fee_per_gas
# - gas_limit
# - to (contract address to delegate to)
# - value
# - data (empty for delegation)
# - authorization_list: [{chain_id, address, nonce, y_parity, r, s}]

# The delegation is identified by tx type 0x04 and non-empty authorization_list

async def fetch_tx(session: aiohttp.ClientSession, rpc: str, tx_hash: str) -> dict:
    result = await rpc_call(session, rpc, "eth_getTransactionByHash", [tx_hash])
    return result.get("result")

async def fetch_tx_receipt(session: aiohttp.ClientSession, rpc: str, tx_hash: str) -> dict:
    result = await rpc_call(session, rpc, "eth_getTransactionReceipt", [tx_hash])
    return result.get("result")

async def rpc_call(session: aiohttp.ClientSession, rpc: str, method: str, params: list) -> dict:
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    async with session.post(rpc, json=payload) as resp:
        return await resp.json()

def decode_eip7702_authorization(auth: dict) -> dict:
    """Decode EIP-7702 authorization tuple"""
    return {
        "chain_id": int(auth.get("chainId", "0x0"), 16),
        "delegate_address": auth.get("address"),
        "nonce": int(auth.get("nonce", "0x0"), 16),
        "y_parity": auth.get("yParity"),
        "r": auth.get("r"),
        "s": auth.get("s"),
    }

def decode_sweep_calldata(data: str) -> dict:
    """Decode the sweep contract calldata"""
    if not data or data == "0x":
        return {"type": "empty"}
    
    selector = data[:10]
    params_hex = data[10:]
    
    # Common sweep patterns:
    # - sweepToken(address token, address to, uint256 amount)
    # - sweepETH(address to)
    # - execute(bytes calldata)
    
    return {
        "selector": selector,
        "params_hex": params_hex,
        "param_count": len(params_hex) // 64 if params_hex else 0
    }

async def analyze_tx(session: aiohttp.ClientSession, chain: str, tx_hash: str, label: str):
    rpc = RPCS[chain]
    print(f"\n{'='*60}")
    print(f"ANALYZING: {label}")
    print(f"Chain: {chain} | Hash: {tx_hash}")
    print(f"{'='*60}")
    
    tx = await fetch_tx(session, rpc, tx_hash)
    if not tx:
        print("TX NOT FOUND")
        return
    
    receipt = await fetch_tx_receipt(session, rpc, tx_hash)
    
    print(f"Block: {int(tx.get('blockNumber', '0x0'), 16)}")
    print(f"From: {tx.get('from')}")
    print(f"To: {tx.get('to')}")
    print(f"Value: {int(tx.get('value', '0x0'), 16) / 1e18:.6f} ETH")
    print(f"Gas: {int(tx.get('gas', '0x0'), 16)}")
    print(f"Gas Price: {int(tx.get('gasPrice', '0x0'), 16) / 1e9:.2f} gwei")
    print(f"Type: {tx.get('type', '0x0')} ({'EIP-7702' if tx.get('type') == '0x4' else 'Legacy/EIP-1559'})")
    
    # Check for EIP-7702 authorization list
    if tx.get("authorizationList"):
        print("\n*** EIP-7702 DELEGATION DETECTED ***")
        for i, auth in enumerate(tx["authorizationList"]):
            decoded = decode_eip7702_authorization(auth)
            print(f"  Authorization #{i+1}:")
            print(f"    Delegate to: {decoded['delegate_address']}")
            print(f"    Nonce: {decoded['nonce']}")
            print(f"    Chain ID: {decoded['chain_id']}")
    
    # Decode calldata
    calldata = tx.get("input", "0x")
    if calldata != "0x":
        decoded = decode_sweep_calldata(calldata)
        print(f"\nCalldata: {calldata[:100]}...")
        print(f"Selector: {decoded['selector']}")
        print(f"Params: {decoded['param_count']} words")
    
    # Receipt logs
    if receipt and receipt.get("logs"):
        print(f"\nLogs ({len(receipt['logs'])}):")
        for log in receipt["logs"][:10]:
            topics = log.get("topics", [])
            if topics:
                print(f"  Topic0: {topics[0]}")
                print(f"  Address: {log.get('address')}")
                print(f"  Data: {log.get('data', '0x')[:100]}...")
    
    return {"tx": tx, "receipt": receipt}

async def search_tx_by_address(session: aiohttp.ClientSession, chain: str, address: str, start_block: int, end_block: int):
    """Search for transactions from/to address in block range (requires archive node or indexer)"""
    # This requires an indexer like Alchemy, QuickNode, or Etherscan API
    # For now, placeholder
    pass

async def main():
    # This script needs actual transaction hashes to work
    # Run after collecting hashes from Etherscan
    print("Transaction Decoder - Ready to analyze")
    print("Populate KEY_TXS with actual hashes first")
    
    # Example usage once hashes are known:
    # async with aiohttp.ClientSession() as session:
    #     await analyze_tx(session, "ethereum", KEY_TXS["ethereum"]["main_sweep"], "Main Sweep")

if __name__ == "__main__":
    asyncio.run(main())