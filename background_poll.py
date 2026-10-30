#!/usr/bin/env python3
"""
Background poller - writes to log file, no stdin needed
Includes Aave V3 pool watcher to detect if Exploiter 2 deposits stolen USDT/USDC as collateral
"""
import asyncio
import aiohttp
import json
from datetime import datetime, timezone

RPC = "https://eth.drpc.org"
USDT_CONTRACT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
USDC_CONTRACT = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

# Aave V3 Ethereum Mainnet
AAVE_LENDING_POOL = "0x87869991452208843334988248bDd9e514747e33"
AAVE_USDT_ATOKEN = "0x8dc4C39555C7f19c77c9e07229d994C7e135B964"  # aUSDT
AAVE_USDC_ATOKEN = "0x9bA8DC8c31F8222b93587f4978e00504d7327F78"  # aUSDC
# allowance selector: allowance(owner, spender)
ALLOWANCE_SELECTOR = "0xdda051c1"
# getReserveData selector on LendingPool
GET_RESERVE_DATA_SELECTOR = "0x6d475d8c"

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
        content_type = resp.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            text = await resp.text()
            raise Exception(f"Non-JSON response ({resp.status}): {text[:200]}")
        return await resp.json()

async def get_token_balance(session, contract, address):
    data = "0x70a08231" + address[2:].lower().zfill(64)
    result = await rpc_call(session, "eth_call", [{
        "to": contract,
        "data": data
    }, "latest"])
    return int(result.get("result", "0x0"), 16)

async def get_allowance(session, token_contract, owner, spender):
    """Check allowance(token owner -> spender)"""
    data = ALLOWANCE_SELECTOR + owner[2:].lower().zfill(64) + spender[2:].lower().zfill(64)
    result = await rpc_call(session, "eth_call", [{
        "to": token_contract,
        "data": data
    }, "latest"])
    return int(result.get("result", "0x0"), 16)

async def get_aave_reserve_data(session, token_contract):
    """Check if Aave reserve is paused via getReserveData"""
    data = GET_RESERVE_DATA_SELECTOR + token_contract[2:].lower().zfill(64)
    result = await rpc_call(session, "eth_call", [{
        "to": AAVE_LENDING_POOL,
        "data": data
    }, "latest"])
    hex_result = result.get("result", "0x")
    if hex_result == "0x" or len(hex_result) < 130:
        return None
    # getReserveData returns: configuration (uint256), liquidityIndex, variableBorrowIndex, ...
    # configuration bit 0 = paused
    configuration = int(hex_result[2:66], 16)
    paused = bool(configuration & 1)
    return paused

async def poll_once(session):
    timestamp = datetime.now(timezone.utc).isoformat()
    lines = [f"\n=== {timestamp} ==="]
    
    # Check Aave market status first
    aave_usdt_paused = await get_aave_reserve_data(session, USDT_CONTRACT)
    aave_usdc_paused = await get_aave_reserve_data(session, USDC_CONTRACT)
    aave_status = []
    if aave_usdt_paused is not None:
        aave_status.append(f"USDT market {'PAUSED' if aave_usdt_paused else 'ACTIVE'}")
    if aave_usdc_paused is not None:
        aave_status.append(f"USDC market {'PAUSED' if aave_usdc_paused else 'ACTIVE'}")
    if aave_status:
        lines.append(f"[AAVE] {' | '.join(aave_status)}")
    
    for label, addr in ADDRESSES.items():
        # ETH balance + tx count
        bal_res = await rpc_call(session, "eth_getBalance", [addr, "latest"])
        cnt_res = await rpc_call(session, "eth_getTransactionCount", [addr, "latest"])
        
        eth_bal = int(bal_res.get("result", "0x0"), 16) / 1e18
        tx_cnt = int(cnt_res.get("result", "0x0"), 16)
        
        # USDT/USDC for Exploiter 2 + Aave checks
        if label == "Exploiter 2":
            usdt = await get_token_balance(session, USDT_CONTRACT, addr) / 1e6
            usdc = await get_token_balance(session, USDC_CONTRACT, addr) / 1e6
            
            # Check aToken balances (proof of Aave deposit)
            ausdt = await get_token_balance(session, AAVE_USDT_ATOKEN, addr) / 1e6
            ausdc = await get_token_balance(session, AAVE_USDC_ATOKEN, addr) / 1e6
            
            # Check allowance to LendingPool (pre-deposit signal)
            usdt_allow = await get_allowance(session, USDT_CONTRACT, addr, AAVE_LENDING_POOL)
            usdc_allow = await get_allowance(session, USDC_CONTRACT, addr, AAVE_LENDING_POOL)
            
            aave_alert = ""
            if ausdt > 0 or ausdc > 0:
                aave_alert = " ⚠️ AAVE DEPOSIT DETECTED!"
            elif usdt_allow > 0 or usdc_allow > 0:
                aave_alert = " ⚠️ AAVE ALLOWANCE SET!"
            
            lines.append(f"{label}: {eth_bal:.4f} ETH | {tx_cnt} txs | {usdt:,.0f} USDT | {usdc:,.0f} USDC | aUSDT:{ausdt:,.0f} aUSDC:{ausdc:,.0f}{aave_alert}")
        else:
            lines.append(f"{label}: {eth_bal:.4f} ETH | {tx_cnt} txs")
    
    log_entry = "\n".join(lines) + "\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    # Also print to console
    print(log_entry.strip())

async def main():
    print(f"Starting background poller with Aave watcher - logging to {LOG_FILE}")
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