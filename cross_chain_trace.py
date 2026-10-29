#!/usr/bin/env python3
"""
Cross-Chain Trace Script for Binance Hack
Traces funds from Exploiter addresses across Ethereum, BSC, Arbitrum, Polygon, Optimism
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
        "rpc": "https://eth.llamarpc.com",
        "explorer": "https://etherscan.io",
        "explorer_api": "https://api.etherscan.io/api",  # Needs API key
        "chain_id": 1,
        "layerzero_eid": 30101,
        "stargate_chain_id": 101,
    },
    "bsc": {
        "rpc": "https://bsc-dataseed1.binance.org",
        "explorer": "https://bscscan.com",
        "explorer_api": "https://api.bscscan.com/api",
        "chain_id": 56,
        "layerzero_eid": 30102,
        "stargate_chain_id": 102,
    },
    "arbitrum": {
        "rpc": "https://arb1.arbitrum.io/rpc",
        "explorer": "https://arbiscan.io",
        "explorer_api": "https://api.arbiscan.io/api",
        "chain_id": 42161,
        "layerzero_eid": 30110,
        "stargate_chain_id": 110,
    },
    "polygon": {
        "rpc": "https://polygon-rpc.com",
        "explorer": "https://polygonscan.com",
        "explorer_api": "https://api.polygonscan.com/api",
        "chain_id": 137,
        "layerzero_eid": 30109,
        "stargate_chain_id": 109,
    },
    "optimism": {
        "rpc": "https://mainnet.optimism.io",
        "explorer": "https://optimistic.etherscan.io",
        "explorer_api": "https://api-optimistic.etherscan.io/api",
        "chain_id": 10,
        "layerzero_eid": 30111,
        "stargate_chain_id": 111,
    },
    "base": {
        "rpc": "https://mainnet.base.org",
        "explorer": "https://basescan.org",
        "explorer_api": "https://api.basescan.org/api",
        "chain_id": 8453,
        "layerzero_eid": 30184,
        "stargate_chain_id": 184,
    }
}

# Source addresses to trace from
SOURCE_ADDRESSES = {
    "ethereum": [
        "0x5227...CB2f8c",  # Exploiter 2 - primary receiver
        "0x8532...43D4",    # Exploiter 3 - ETH holder
        "0x7C86...5CA0",    # Attacker EOA
    ],
    "bsc": [],
    "arbitrum": [],
    "polygon": [
        "0xEe7aE85f2Fe2239E27D9c1E23fFFe168D63b4055",  # Hot Wallet 34 on Polygon
    ],
    "optimism": [],
    "base": [],
}

# Bridge contracts to monitor for outbound transfers
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
    }
}

# LayerZero OFT message structure
# DepositLocal(event): (uint16 dstEid, bytes to, uint256 amount, bytes extraOptions, bytes composeMsg, bytes oftCmd)
# Event signature: DepositLocal(uint16,bytes,uint256,bytes,bytes,bytes)

# Stargate: tokens deposited to pool, then message sent via LayerZero

@dataclass
class BridgeTransfer:
    chain: str
    tx_hash: str
    block: int
    timestamp: int
    protocol: str  # layerzero, stargate, celer, thorchain, wormhole
    src_address: str
    dst_chain: str
    dst_address: str
    token: str
    amount: int
    amount_usd: float

async def rpc_call(session, rpc, method, params):
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    async with session.post(rpc, json=payload) as resp:
        return await resp.json()

async def get_logs(session, rpc, from_block, to_block, address, topics):
    result = await rpc_call(session, rpc, "eth_getLogs", [{
        "fromBlock": hex(from_block),
        "toBlock": hex(to_block),
        "address": address,
        "topics": topics
    }])
    return result.get("result", [])

async def trace_layerzero_deposits(session, chain, from_block, to_block, source_addresses):
    """Trace LayerZero DepositLocal events from source addresses"""
    config = CHAINS[chain]
    endpoint = BRIDGE_CONTRACTS[chain].get("layerzero_endpoint")
    if not endpoint:
        return []
    
    # DepositLocal topic: keccak256("DepositLocal(uint16,bytes,uint256,bytes,bytes,bytes)")
    topic = "0x..."  # Need to calculate
    
    logs = await get_logs(session, config["rpc"], from_block, to_block, endpoint, [topic])
    
    transfers = []
    for log in logs:
        # Parse log - need to decode topics and data
        # topics[1] = dstEid (uint16)
        # topics[2] = sender (address, padded)
        # data contains: to (bytes), amount (uint256), extraOptions, composeMsg, oftCmd
        pass
    
    return transfers

async def trace_stargate_transfers(session, chain, from_block, to_block, source_addresses):
    """Trace Stargate transfers via LayerZero"""
    # Stargate uses LayerZero underneath
    # Look for transfers to Stargate router, then LayerZero message
    pass

async def trace_celer_transfers(session, chain, from_block, to_block, source_addresses):
    """Trace Celer cBridge transfers"""
    pass

async def trace_thorchain_transfers(session, chain, from_block, to_block, source_addresses):
    """Trace THORChain router interactions"""
    pass

async def trace_wormhole_transfers(session, chain, from_block, to_block, source_addresses):
    """Trace Wormhole token bridge transfers"""
    pass

async def scan_chain_for_bridges(chain: str, start_block: int, end_block: int):
    """Scan a chain for bridge interactions from source addresses"""
    config = CHAINS[chain]
    sources = SOURCE_ADDRESSES.get(chain, [])
    
    if not sources:
        print(f"[{chain}] No source addresses configured")
        return []
    
    print(f"[{chain}] Scanning blocks {start_block} to {end_block} for {len(sources)} source addresses")
    
    async with aiohttp.ClientSession() as session:
        all_transfers = []
        
        # LayerZero
        lz_transfers = await trace_layerzero_deposits(session, chain, start_block, end_block, sources)
        all_transfers.extend(lz_transfers)
        
        # Stargate
        sg_transfers = await trace_stargate_transfers(session, chain, start_block, end_block, sources)
        all_transfers.extend(sg_transfers)
        
        # Celer
        cl_transfers = await trace_celer_transfers(session, chain, start_block, end_block, sources)
        all_transfers.extend(cl_transfers)
        
        # THORChain
        tc_transfers = await trace_thorchain_transfers(session, chain, start_block, end_block, sources)
        all_transfers.extend(tc_transfers)
        
        # Wormhole
        wh_transfers = await trace_wormhole_transfers(session, chain, start_block, end_block, sources)
        all_transfers.extend(wh_transfers)
        
        return all_transfers

def format_transfer(t: BridgeTransfer) -> str:
    return (f"  [{t.chain}] {t.protocol} → {t.dst_chain} | "
            f"{t.token} {t.amount/1e18:.4f} (${t.amount_usd:,.0f}) | "
            f"src:{t.src_address[:10]}... dst:{t.dst_address[:10]}... | "
            f"tx:{t.tx_hash[:10]}...")

async def main():
    # Block range: Oct 29 20:20 UTC onwards
    # Ethereum block ~26300791 at 20:20:59
    START_BLOCKS = {
        "ethereum": 26300791,
        "bsc": 0,  # Need to find
        "arbitrum": 0,
        "polygon": 0,
        "optimism": 0,
        "base": 0,
    }
    
    END_BLOCK = "latest"
    
    all_results = {}
    
    for chain in CHAINS:
        start = START_BLOCKS.get(chain, 0)
        if start == 0:
            print(f"[{chain}] Skipping - need start block")
            continue
            
        transfers = await scan_chain_for_bridges(chain, start, 99999999)
        all_results[chain] = transfers
        
        if transfers:
            print(f"\n[{chain}] Found {len(transfers)} bridge transfers:")
            for t in transfers:
                print(format_transfer(t))
        else:
            print(f"[{chain}] No bridge transfers found")
    
    # Save results
    with open("bridge_traces.json", "w") as f:
        json.dump({k: [vars(t) for t in v] for k, v in all_results.items()}, f, indent=2)
    
    print("\nResults saved to bridge_traces.json")

if __name__ == "__main__":
    asyncio.run(main())