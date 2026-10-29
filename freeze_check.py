#!/usr/bin/env python3
"""
Freeze Verification Script
Checks exact freeze status of stolen USDT/USDC with Tether and Circle
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone
from typing import Dict, List

# ============================================================
# FREEZE STATUS CHECKING
# ============================================================

# USDT on Ethereum: Blacklist is maintained in USDT contract
# Function: isBlacklisted(address) -> bool
# Function: getBlacklistStatus(address) -> uint8 (0=not, 1=frozen, 2=thawed)
USDT_CONTRACT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

# USDC on Ethereum: Blacklist via Circle's FiatTokenV2 (FiatTokenProxy)
# Function: blacklisted(address) -> bool (not isBlacklisted)
USDC_CONTRACT = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # USDC mainnet (FiatTokenProxy)

# Known frozen addresses from reports
REPORTED_FROZEN = {
    "USDT": [
        "0x5227...CB2f8c",  # Exploiter 2 - primary receiver
        # Tether froze >$1.567B USDT linked to incident
    ],
    "USDC": [
        "0x5227...CB2f8c",  # Exploiter 2
        # Circle froze >$823M USDC
    ]
}

# Addresses to check (full addresses from on-chain data)
ADDRESSES_TO_CHECK = [
    "0x5227f603c1ee34ce3c06efe6477003bdfccb2f8c",  # Exploiter 2 - primary receiver
    "0x8532...43D4",    # Exploiter 3 - NEED FULL ADDRESS (received 195K ETH)
    "0x7c8601d4645b93cea45f71e118a729332e6b5ca0",  # Attacker EOA - Tornado funded
    "0x63e842B0...6fAe", # Attacker Contract - NEED FULL ADDRESS (EIP-7702 delegate)
    "0x28C6c06298d514Db089934071355E5743bf21d60",  # Binance 14 (victim)
    "0xDFd5293D8e347dFe59E90eFd55b2956a1343963d",  # Binance 16 (victim)
    "0xEe7aE85f2Fe2239E27D9c1E23fFFe168D63b4055",  # Hot Wallet 34 (victim)
]

async def rpc_call(session, rpc, method, params):
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    async with session.post(rpc, json=payload) as resp:
        content_type = resp.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            text = await resp.text()
            raise Exception(f"Non-JSON response ({resp.status}): {text[:200]}")
        return await resp.json()

async def check_usdt_blacklist(session, rpc, address: str) -> Dict:
    """Check if address is blacklisted on USDT contract"""
    # isBlacklisted(address) selector: 0x4f52d31a
    data = "0x4f52d31a" + address[2:].lower().zfill(64)
    result = await rpc_call(session, rpc, "eth_call", [{
        "to": USDT_CONTRACT,
        "data": data
    }, "latest"])
    
    is_blacklisted = int(result.get("result", "0x0"), 16) == 1
    
    # Also check balance
    # balanceOf(address) selector: 0x70a08231
    bal_data = "0x70a08231" + address[2:].lower().zfill(64)
    bal_result = await rpc_call(session, rpc, "eth_call", [{
        "to": USDT_CONTRACT,
        "data": bal_data
    }, "latest"])
    balance = int(bal_result.get("result", "0x0"), 16) / 1e6  # USDT 6 decimals
    
    return {
        "address": address,
        "token": "USDT",
        "blacklisted": is_blacklisted,
        "balance": balance,
        "balance_raw": int(bal_result.get("result", "0x0"), 16)
    }

async def check_usdc_blacklist(session, rpc, address: str) -> Dict:
    """Check if address is blacklisted on USDC contract"""
    # USDC (FiatTokenProxy) uses `blacklisted(address)` not `isBlacklisted`
    # selector: keccak256("blacklisted(address)") = 0x0c9c9c9c... (first 4 bytes)
    # We'll try multiple selectors since the exact one varies by version
    
    is_blacklisted = False
    blacklist_selectors = [
        "0x0c9c9c9c",  # blacklisted(address) - common
        "0x4f52d31a",  # isBlacklisted(address) - USDT style
        "0x5c975abb",  # frozen(address)
    ]
    
    for selector in blacklist_selectors:
        try:
            data = selector + address[2:].lower().zfill(64)
            result = await rpc_call(session, rpc, "eth_call", [{
                "to": USDC_CONTRACT,
                "data": data
            }, "latest"])
            if result.get("result") and result["result"] != "0x":
                is_blacklisted = int(result["result"], 16) == 1
                break
        except:
            continue
    
    # Balance
    bal_data = "0x70a08231" + address[2:].lower().zfill(64)
    bal_result = await rpc_call(session, rpc, "eth_call", [{
        "to": USDC_CONTRACT,
        "data": bal_data
    }, "latest"])
    balance = int(bal_result.get("result", "0x0"), 16) / 1e6  # USDC 6 decimals
    
    return {
        "address": address,
        "token": "USDC",
        "blacklisted": is_blacklisted,
        "balance": balance,
        "balance_raw": int(bal_result.get("result", "0x0"), 16)
    }

async def check_token_balance(session, rpc, token_contract: str, address: str, decimals: int = 18) -> float:
    """Generic ERC-20 balance check"""
    data = "0x70a08231" + address[2:].lower().zfill(64)
    result = await rpc_call(session, rpc, "eth_call", [{
        "to": token_contract,
        "data": data
    }, "latest"])
    return int(result.get("result", "0x0"), 16) / (10 ** decimals)

# Token contracts for other stolen assets
OTHER_TOKENS = {
    "wBETH": ("0x...", 18),
    "RLUSD": ("0x...", 6),
    "XAUt": ("0x...", 18),
    "UNI": ("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", 18),
    "ENA": ("0x...", 18),
    "PEPE": ("0x...", 18),
    "USD1": ("0x...", 18),
    "LINK": ("0x514910771AF9Ca656af840dff83E8264EcF986CA", 18),
    "AAVE": ("0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9", 18),
}

async def main():
    print("=" * 60)
    print("FREEZE VERIFICATION - BINANCE HACK STOLEN FUNDS")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    rpc = "https://eth.drpc.org"
    
    async with aiohttp.ClientSession() as session:
        results = {"USDT": [], "USDC": [], "OTHER": []}
        
        # Check USDT blacklist
        print("\n[1/3] Checking USDT (Tether) blacklist...")
        for addr in ADDRESSES_TO_CHECK:
            try:
                result = await check_usdt_blacklist(session, rpc, addr)
                results["USDT"].append(result)
                status = "[FROZEN]" if result["blacklisted"] else "[ACTIVE]"
                print(f"  {addr[:12]}... | {status} | Balance: {result['balance']:,.2f} USDT")
            except Exception as e:
                print(f"  {addr[:12]}... | ERROR: {e}")
        
        # Check USDC blacklist
        print("\n[2/3] Checking USDC (Circle) blacklist...")
        for addr in ADDRESSES_TO_CHECK:
            try:
                result = await check_usdc_blacklist(session, rpc, addr)
                results["USDC"].append(result)
                status = "[FROZEN]" if result["blacklisted"] else "[ACTIVE]"
                print(f"  {addr[:12]}... | {status} | Balance: {result['balance']:,.2f} USDC")
            except Exception as e:
                print(f"  {addr[:12]}... | ERROR: {e}")
        
        # Check other token balances
        print("\n[3/3] Checking other token balances on Exploiter 2...")
        exploiter2 = "0x5227...CB2f8c"
        for token_name, (contract, decimals) in OTHER_TOKENS.items():
            if contract == "0x...":
                continue
            try:
                bal = await check_token_balance(session, rpc, contract, exploiter2, decimals)
                if bal > 0:
                    results["OTHER"].append({
                        "token": token_name,
                        "address": exploiter2,
                        "balance": bal
                    })
                    print(f"  {token_name}: {bal:,.2f}")
            except:
                pass
    
    # Summary
    print("\n" + "=" * 60)
    print("FREEZE SUMMARY")
    print("=" * 60)
    
    usdt_frozen = sum(1 for r in results["USDT"] if r["blacklisted"])
    usdt_total = sum(r["balance"] for r in results["USDT"])
    usdc_frozen = sum(1 for r in results["USDC"] if r["blacklisted"])
    usdc_total = sum(r["balance"] for r in results["USDC"])
    
    print(f"USDT: {usdt_frozen}/{len(results['USDT'])} addresses frozen | Total balance: {usdt_total:,.2f} USDT")
    print(f"USDC: {usdc_frozen}/{len(results['USDC'])} addresses frozen | Total balance: {usdc_total:,.2f} USDC")
    
    # Save
    with open("freeze_verification.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to freeze_verification.json")

if __name__ == "__main__":
    asyncio.run(main())