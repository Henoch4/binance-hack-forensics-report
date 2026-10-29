#!/usr/bin/env python3
"""
Binance Hack Watchlist Poller
Monitors key addresses across 5 chains for movement.
Run every 10 seconds via cron or loop.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, List, Optional
import hashlib

# ============================================================
# WATCHLIST CONFIGURATION
# ============================================================

WATCHLIST = {
    "ethereum": {
        "rpc": "https://eth.llamarpc.com",  # Use your own RPC
        "addresses": {
            "0x8532...43D4": {"label": "Exploiter 3 (ETH)", "priority": "CRITICAL", "asset": "ETH"},
            "0x5227...CB2f8c": {"label": "Exploiter 2 (Tokens)", "priority": "HIGH", "asset": "MULTI"},
            "0x7C86...5CA0": {"label": "Attacker EOA", "priority": "MEDIUM", "asset": "ETH"},
            "0x63e842B0...6fAe": {"label": "Attacker Contract", "priority": "MEDIUM", "asset": "CONTRACT"},
            "0xDFd5293D8e347dFe59E90eFd55b2956a1343963d": {"label": "Binance 16", "priority": "LOW", "asset": "ETH"},
            "0xEe7aE85f2Fe2239E27D9c1E23fFFe168D63b4055": {"label": "Hot Wallet 34", "priority": "LOW", "asset": "MULTI"},
        }
    },
    "bsc": {
        "rpc": "https://bsc-dataseed1.binance.org",
        "addresses": {
            # Add Binance-labeled BSC addresses here
        }
    },
    "arbitrum": {
        "rpc": "https://arb1.arbitrum.io/rpc",
        "addresses": {
            # Add Binance-labeled Arbitrum addresses here
        }
    },
    "polygon": {
        "rpc": "https://polygon-rpc.com",
        "addresses": {
            "0xEe7aE85f2Fe2239E27D9c1E23fFFe168D63b4055": {"label": "Hot Wallet 34 (Polygon)", "priority": "HIGH", "asset": "MULTI"},
        }
    },
    "optimism": {
        "rpc": "https://mainnet.optimism.io",
        "addresses": {
            # Add Binance-labeled Optimism addresses here
        }
    }
}

# ERC-20 ABI for balanceOf
ERC20_ABI = [{
    "constant": True,
    "inputs": [{"name": "_owner", "type": "address"}],
    "name": "balanceOf",
    "outputs": [{"name": "balance", "type": "uint256"}],
    "type": "function"
}]

# Known token contracts on Ethereum mainnet
TOKENS = {
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "USDC": "0xA0b86a33E6441b8c4C8C8C8C8C8C8C8C8C8C8C8C",  # placeholder
    "wBETH": "0x...",  # Add actual
    "RLUSD": "0x...",  # Add actual
    "XAUt": "0x...",   # Add actual
    "UNI": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "ENA": "0x...",    # Add actual
    "PEPE": "0x...",   # Add actual
    "USD1": "0x...",   # Add actual
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
}

# ============================================================
# STATE TRACKING
# ============================================================

@dataclass
class AddressState:
    address: str
    chain: str
    label: str
    last_eth_balance: int = 0
    last_token_balances: Dict[str, int] = None
    last_tx_count: int = 0
    first_seen: str = None
    
    def __post_init__(self):
        if self.last_token_balances is None:
            self.last_token_balances = {}
        if self.first_seen is None:
            self.first_seen = datetime.now(timezone.utc).isoformat()

# Global state
STATES: Dict[str, AddressState] = {}
SEEN_TXS: set = set()  # (chain, tx_hash) for dedup

# ============================================================
# RPC HELPERS
# ============================================================

async def rpc_call(session: aiohttp.ClientSession, rpc_url: str, method: str, params: list) -> dict:
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    async with session.post(rpc_url, json=payload) as resp:
        return await resp.json()

async def get_eth_balance(session: aiohttp.ClientSession, rpc_url: str, address: str) -> int:
    result = await rpc_call(session, rpc_url, "eth_getBalance", [address, "latest"])
    return int(result.get("result", "0x0"), 16)

async def get_tx_count(session: aiohttp.ClientSession, rpc_url: str, address: str) -> int:
    result = await rpc_call(session, rpc_url, "eth_getTransactionCount", [address, "latest"])
    return int(result.get("result", "0x0"), 16)

async def get_token_balance(session: aiohttp.ClientSession, rpc_url: str, token_address: str, wallet_address: str) -> int:
    # eth_call to balanceOf
    data = "0x70a08231" + wallet_address[2:].lower().zfill(64)  # balanceOf(address)
    result = await rpc_call(session, rpc_url, "eth_call", [{
        "to": token_address,
        "data": data
    }, "latest"])
    return int(result.get("result", "0x0"), 16)

async def get_block_number(session: aiohttp.ClientSession, rpc_url: str) -> int:
    result = await rpc_call(session, rpc_url, "eth_blockNumber", [])
    return int(result.get("result", "0x0"), 16)

# ============================================================
# ALERTING
# ============================================================

def alert(chain: str, address: str, label: str, msg: str, severity: str = "INFO"):
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"[{timestamp}] [{severity}] {chain} | {label} ({address}) | {msg}")
    # TODO: Add webhook/Telegram/Slack integration here

def alert_new_tx(chain: str, address: str, label: str, tx_hash: str, severity: str = "HIGH"):
    key = (chain, tx_hash.lower())
    if key in SEEN_TXS:
        return
    SEEN_TXS.add(key)
    alert(chain, address, label, f"NEW TX: {tx_hash}", severity)

# ============================================================
# POLLING LOGIC
# ============================================================

async def poll_address(session: aiohttp.ClientSession, chain: str, address: str, info: dict):
    state_key = f"{chain}:{address.lower()}"
    state = STATES.get(state_key)
    
    if state is None:
        state = AddressState(address=address, chain=chain, label=info["label"])
        STATES[state_key] = state
    
    rpc_url = WATCHLIST[chain]["rpc"]
    
    try:
        # Check ETH balance
        eth_balance = await get_eth_balance(session, rpc_url, address)
        if eth_balance != state.last_eth_balance:
            diff = eth_balance - state.last_eth_balance
            direction = "IN" if diff > 0 else "OUT"
            alert(chain, address, info["label"], 
                  f"ETH balance change: {direction} {abs(diff)/1e18:.6f} ETH (now {eth_balance/1e18:.6f})",
                  "HIGH" if abs(diff) > 1e18 else "INFO")
            state.last_eth_balance = eth_balance
        
        # Check tx count (detect new outgoing txs)
        tx_count = await get_tx_count(session, rpc_url, address)
        if tx_count > state.last_tx_count:
            alert_new_tx(chain, address, info["label"], f"tx_count:{tx_count}", "HIGH")
            state.last_tx_count = tx_count
        
        # Check token balances (if multi-asset wallet)
        if info["asset"] == "MULTI":
            for token_name, token_addr in TOKENS.items():
                try:
                    bal = await get_token_balance(session, rpc_url, token_addr, address)
                    if bal != state.last_token_balances.get(token_name, 0):
                        diff = bal - state.last_token_balances.get(token_name, 0)
                        direction = "IN" if diff > 0 else "OUT"
                        alert(chain, address, info["label"],
                              f"{token_name} balance change: {direction} {abs(diff)} (now {bal})",
                              "HIGH" if abs(diff) > 0 else "INFO")
                        state.last_token_balances[token_name] = bal
                except Exception as e:
                    pass  # Token not on this chain or error
                    
    except Exception as e:
        alert(chain, address, info["label"], f"Poll error: {e}", "ERROR")

async def poll_chain(session: aiohttp.ClientSession, chain: str):
    tasks = []
    for addr, info in WATCHLIST[chain]["addresses"].items():
        tasks.append(poll_address(session, chain, addr, info))
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

async def main_loop(interval: int = 10):
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Binance hack watchlist poller (interval={interval}s)")
    print(f"Watching {sum(len(v['addresses']) for v in WATCHLIST.values())} addresses across {len(WATCHLIST)} chains")
    
    connector = aiohttp.TCPConnector(limit=50)
    timeout = aiohttp.ClientTimeout(total=10)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        while True:
            start = time.time()
            
            # Poll all chains in parallel
            chain_tasks = [poll_chain(session, chain) for chain in WATCHLIST]
            await asyncio.gather(*chain_tasks, return_exceptions=True)
            
            elapsed = time.time() - start
            sleep_time = max(0, interval - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    asyncio.run(main_loop(10))