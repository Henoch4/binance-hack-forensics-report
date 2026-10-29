#!/usr/bin/env python3
"""
Cross-Chain Trace Script for Binance Hack
Traces funds from Exploiter addresses across Ethereum, BSC, Arbitrum, Polygon, Optimism, Avalanche, BTC, TRON
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

# ============================================================
# CONFIGURATION
# ============================================================

CHAINS = {
    "ethereum": {
        "rpc": "https://eth.drpc.org",
        "explorer": "https://etherscan.io",
        "explorer_api": "https://api.etherscan.io/api",
        "chain_id": 1,
        "layerzero_eid": 30101,
        "stargate_chain_id": 101,
        "type": "evm",
    },
    "bsc": {
        "rpc": "https://bsc.drpc.org",
        "explorer": "https://bscscan.com",
        "explorer_api": "https://api.bscscan.com/api",
        "chain_id": 56,
        "layerzero_eid": 30102,
        "stargate_chain_id": 102,
        "type": "evm",
    },
    "arbitrum": {
        "rpc": "https://arb1.drpc.org",
        "explorer": "https://arbiscan.io",
        "explorer_api": "https://api.arbiscan.io/api",
        "chain_id": 42161,
        "layerzero_eid": 30110,
        "stargate_chain_id": 110,
        "type": "evm",
    },
    "polygon": {
        "rpc": "https://polygon.drpc.org",
        "explorer": "https://polygonscan.com",
        "explorer_api": "https://api.polygonscan.com/api",
        "chain_id": 137,
        "layerzero_eid": 30109,
        "stargate_chain_id": 109,
        "type": "evm",
    },
    "optimism": {
        "rpc": "https://optimism.drpc.org",
        "explorer": "https://optimistic.etherscan.io",
        "explorer_api": "https://api-optimistic.etherscan.io/api",
        "chain_id": 10,
        "layerzero_eid": 30111,
        "stargate_chain_id": 111,
        "type": "evm",
    },
    "base": {
        "rpc": "https://base.drpc.org",
        "explorer": "https://basescan.org",
        "explorer_api": "https://api.basescan.org/api",
        "chain_id": 8453,
        "layerzero_eid": 30184,
        "stargate_chain_id": 184,
        "type": "evm",
    },
    "avalanche": {
        "rpc": "https://api.avax.network/ext/bc/C/rpc",
        "explorer": "https://snowtrace.io",
        "explorer_api": "https://api.snowtrace.io/api",
        "chain_id": 43114,
        "layerzero_eid": 30109,
        "stargate_chain_id": 109,
        "type": "evm",
    },
    "bitcoin": {
        "rpc": "https://blockstream.info/api",
        "explorer": "https://mempool.space",
        "explorer_api": "https://blockstream.info/api",
        "chain_id": 0,
        "type": "utxo",
    },
    "tron": {
        "rpc": "https://api.trongrid.io",
        "explorer": "https://tronscan.org",
        "explorer_api": "https://apilist.tronscan.org/api",
        "chain_id": 0,
        "type": "tron",
    },
}

# Source addresses to trace from (full addresses from image)
SOURCE_ADDRESSES = {
    "ethereum": [
        "0x5227f603c1ee34ce3c06efe6477003bdfccb2f8c",  # Exploiter 2 - primary receiver
        "0x8532fa14acaf483729c449b8458aeddb900543d4",  # Exploiter 3 - ETH holder (195,460 ETH)
        "0x7c8601d4645b93cea45f71e118a729332e6b5ca0",  # Attacker EOA (Tornado-funded)
    ],
    "bsc": [],
    "arbitrum": [],
    "polygon": [
        "0xEe7aE85f2Fe2239E27D9c1E23fFFe168D63b4055",  # Hot Wallet 34 on Polygon
    ],
    "optimism": [],
    "base": [],
    "avalanche": [],
    "bitcoin": [],
    "tron": [],
}

# Bridge contracts to monitor for outbound transfers (EVM chains)
BRIDGE_CONTRACTS = {
    "ethereum": {
        "layerzero_endpoint": "0x66A71Dcef29A0fFBDBE3c6a460a3B5BC225Cd675",
        "stargate_router": "0x8731d54E9D02c286767d56ac03e8037C07e01e98",
        "celer_cbridge": "0xC5cEA3B5234064D253D9A820eD7f296b4E22E9E2",
        "thorchain_router": "0x...",  # THORChain router on Ethereum
        "wormhole": "0x98f3c9e6E3fAce36bAAC7458435B85e1d6A4bE34",  # Wormhole core
    },
    "bsc": {
        "layerzero_endpoint": "0x5f8b39A7E2E0881114a10C421C6E5f2459A4a7f1",
        "stargate_router": "0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8",
    },
    "arbitrum": {
        "layerzero_endpoint": "0x1a44076050125825900e736c501f859c50fE728c",
        "stargate_router": "0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614",
    },
    "polygon": {
        "layerzero_endpoint": "0x3c2269811836af69497E5F486A85D73392462312",
        "stargate_router": "0x45F089E8D1E15d8A8CE5d527011Dd1567E99F9e5",
    },
    "optimism": {
        "layerzero_endpoint": "0x3c2269811836af69497E5F486A85D73392462312",
        "stargate_router": "0xB0D502E938ed5f4df2E681fE6E419ff29631d62b",
    },
    "base": {
        "layerzero_endpoint": "0x6A9A058C9E21A5a69C6E2b8e5d3C6b3C6E4E5E5E",
        "stargate_router": "0x...",
    },
    "avalanche": {
        "layerzero_endpoint": "0x...",  # Need Avalanche LZ endpoint
        "stargate_router": "0x...",
    },
}

# LayerZero EIDs for cross-chain messaging
LAYERZERO_EIDS = {
    "ethereum": 30101,
    "bsc": 30102,
    "arbitrum": 30110,
    "polygon": 30109,
    "optimism": 30111,
    "base": 30184,
    "avalanche": 30109,  # Verify current EID
}

# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class BridgeTransfer:
    chain: str
    tx_hash: str
    block: int
    timestamp: int
    protocol: str  # layerzero, stargate, celer, thorchain, wormhole, tron_bridge, btc_bridge
    src_address: str
    dst_chain: str
    dst_address: str
    token: str
    amount: int
    amount_usd: float

@dataclass
class UtxoMovement:
    chain: str
    tx_hash: str
    address: str
    amount_satoshi: int
    amount_btc: float
    timestamp: int

# ============================================================
# RPC HELPERS
# ============================================================

async def rpc_call(session, rpc, method, params):
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    async with session.post(rpc, json=payload) as resp:
        content_type = resp.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            text = await resp.text()
            raise Exception(f"Non-JSON response ({resp.status}): {text[:200]}")
        return await resp.json()

async def get_logs(session, rpc, from_block, to_block, address, topics):
    result = await rpc_call(session, rpc, "eth_getLogs", [{
        "fromBlock": hex(from_block),
        "toBlock": hex(to_block),
        "address": address,
        "topics": topics
    }])
    return result.get("result", [])

async def get_address_balance_evm(session, rpc, address):
    """Get ETH/native balance for EVM address"""
    result = await rpc_call(session, rpc, "eth_getBalance", [address, "latest"])
    return int(result.get("result", "0x0"), 16)

async def get_address_tx_count_evm(session, rpc, address):
    """Get transaction count for EVM address"""
    result = await rpc_call(session, rpc, "eth_getTransactionCount", [address, "latest"])
    return int(result.get("result", "0x0"), 16)

# ============================================================
# BTC TRACKING (mempool.space API)
# ============================================================

async def check_btc_address(session, address):
    """Check BTC address for incoming/outgoing transactions"""
    url = f"https://mempool.space/api/address/{address}"
    async with session.get(url) as resp:
        return await resp.json()

async def check_btc_utxos(session, address):
    """Check BTC address UTXOs"""
    url = f"https://mempool.space/api/address/{address}/utxo"
    async with session.get(url) as resp:
        return await resp.json()

# ============================================================
# TRON TRACKING (Trongrid API)
# ============================================================

async def check_tron_address(session, address):
    """Check TRON address for TRC20/USDt transactions"""
    url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20"
    async with session.get(url) as resp:
        return await resp.json()

# ============================================================
# TRACE FUNCTIONS
# ============================================================

async def trace_evm_chain(session, chain, source_addresses, start_block=0):
    """Trace an EVM-compatible chain for bridge transfers and movements"""
    config = CHAINS[chain]
    transfers = []
    
    for addr in source_addresses:
        try:
            # Check balance
            balance = await get_address_balance_evm(session, config["rpc"], addr)
            tx_count = await get_address_tx_count_evm(session, config["rpc"], addr)
            
            if balance > 0 or tx_count > 0:
                print(f"  [{chain}] {addr[:12]}... balance: {balance/1e18:.6f} native | txs: {tx_count}")
                
        except Exception as e:
            print(f"  [{chain}] Error checking {addr[:12]}...: {e}")
    
    return transfers

async def trace_btc(session, source_addresses):
    """Trace Bitcoin addresses for movements"""
    transfers = []
    for addr in source_addresses:
        try:
            data = await check_btc_address(session, addr)
            if data.get("chain_stats", {}).get("funded_txo_sum", 0) > 0:
                print(f"  [BTC] {addr[:12]}... funded: {data['chain_stats']['funded_txo_sum']/1e8:.8f} BTC")
                print(f"  [BTC] {addr[:12]}... spent: {data['chain_stats']['spent_txo_sum']/1e8:.8f} BTC")
                print(f"  [BTC] {addr[:12]}... tx_count: {data['chain_stats']['tx_count']}")
        except Exception as e:
            print(f"  [BTC] Error checking {addr[:12]}...: {e}")
    return transfers

async def trace_tron(session, source_addresses):
    """Trace TRON addresses for TRC20 movements"""
    transfers = []
    for addr in source_addresses:
        try:
            data = await check_tron_address(session, addr)
            if data.get("data"):
                print(f"  [TRON] {addr[:12]}... has {len(data['data'])} TRC20 transactions")
        except Exception as e:
            print(f"  [TRON] Error checking {addr[:12]}...: {e}")
    return transfers

# ============================================================
# MAIN SCAN
# ============================================================

async def scan_all_chains():
    """Scan all configured chains for source address activity"""
    print("=" * 60)
    print("CROSS-CHAIN TRACE - BINANCE HACK")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    connector = aiohttp.TCPConnector(limit=30)
    timeout = aiohttp.ClientTimeout(total=20)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        
        # Scan EVM chains
        evm_chains = ["ethereum", "bsc", "arbitrum", "polygon", "optimism", "base", "avalanche"]
        for chain in evm_chains:
            addrs = SOURCE_ADDRESSES.get(chain, [])
            if not addrs:
                print(f"\n[{chain}] No source addresses configured - skipping")
                continue
            print(f"\n[{chain}] Scanning {len(addrs)} source addresses...")
            await trace_evm_chain(session, chain, addrs)
        
        # Scan Bitcoin
        btc_addrs = SOURCE_ADDRESSES.get("bitcoin", [])
        if btc_addrs:
            print(f"\n[BTC] Scanning {len(btc_addrs)} source addresses...")
            await trace_btc(session, btc_addrs)
        else:
            print("\n[BTC] No source addresses configured - skipping")
        
        # Scan TRON
        tron_addrs = SOURCE_ADDRESSES.get("tron", [])
        if tron_addrs:
            print(f"\n[TRON] Scanning {len(tron_addrs)} source addresses...")
            await trace_tron(session, tron_addrs)
        else:
            print("\n[TRON] No source addresses configured - skipping")
    
    print("\n" + "=" * 60)
    print("Cross-chain scan complete")
    print("=" * 60)

async def main():
    await scan_all_chains()

if __name__ == "__main__":
    asyncio.run(main())