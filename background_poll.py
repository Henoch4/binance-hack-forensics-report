#!/usr/bin/env python3
"""
Background poller - writes to log file, no stdin needed
"""
import asyncio
import aiohttp
import json
from datetime import datetime, timezone

RPC = "https://eth.drpc.org"
USDT_CONTRACT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
USDC_CONTRACT = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

ADDRESSES = {
    "Exploiter 3": "0x8532fa14acaf483729c449b8458aeddb900543d4",
    "Exploiter 2": "0x5227f603c1ee34ce3c06efe6477003bdfccb2f8c",
    "Attacker EOA": "0x7c8601d4645b93cea45f71e118a729332e6b5ca0",
    "Binance 14": "0x28C6c06298d514Db089934071355E5743bf21d60",
    "Binance 16": "0xDFd5293D8e347dFe59E90eFd55b2956a1343963d",
    "Hot Wallet 34": "0xEe7aE85f2Fe2239E27D9c1E23fFFe168D63b4055",
}

LOG_FILE = "watchlist.log"

async def rpc_call(session, method, params):
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    async with session.post(RPC, json=payload) as resp:
        return await resp.json()

async def get_token_balance(session, contract, address):
    data = "0x70a08231" + address[2:].lower().zfill(64)
    result = await rpc_call(session, "eth_call", [{
        "to": contract,
        "data": data
    }, "latest"])
    return int(result.get("result", "0x0"), 16)

async def poll_once(session):
    timestamp = datetime.now(timezone.utc).isoformat()
    lines = [f"\n=== {timestamp} ==="]
    
    for label, addr in ADDRESSES.items():
        # ETH balance + tx count
        bal_res = await rpc_call(session, "eth_getBalance", [addr, "latest"])
        cnt_res = await rpc_call(session, "eth_getTransactionCount", [addr, "latest"])
        
        eth_bal = int(bal_res.get("result", "0x0"), 16) / 1e18
        tx_cnt = int(cnt_res.get("result", "0x0"), 16)
        
        # USDT/USDC for Exploiter 2
        if label == "Exploiter 2":
            usdt = await get_token_balance(session, USDT_CONTRACT, addr) / 1e6
            usdc = await get_token_balance(session, USDC_CONTRACT, addr) / 1e6
            lines.append(f"{label}: {eth_bal:.4f} ETH | {tx_cnt} txs | {usdt:,.0f} USDT | {usdc:,.0f} USDC")
        else:
            lines.append(f"{label}: {eth_bal:.4f} ETH | {tx_cnt} txs")
    
    log_entry = "\n".join(lines) + "\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    # Also print to console
    print(log_entry.strip())

async def main():
    print(f"Starting background poller - logging to {LOG_FILE}")
    print("Press Ctrl+C to stop")
    
    connector = aiohttp.TCPConnector(limit=10)
    timeout = aiohttp.ClientTimeout(total=15)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        while True:
            try:
                await poll_once(session)
            except Exception as e:
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"ERROR: {e}\n")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())