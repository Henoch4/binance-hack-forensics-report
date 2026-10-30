# Binance Hack Forensics Report & Toolkit

**Incident:** October 29–30, 2026  
**Attack Vector:** EIP-7702 Delegation Abuse (Hot Wallet Key Compromise)  
**Estimated Loss:** $2.5B–$5.8B across 7+ blockchains  
**Repo:** https://github.com/Henoch4/binance-hack-forensics-report

---

## Overview

This repository contains the full forensics toolkit and report for the Binance hot-wallet compromise of October 29, 2026 — the largest exchange hack in crypto history.

The attacker exploited **EIP-7702 delegation** to seize control of Binance's "Binance 14" hot wallet via a signed EOA delegation, then swept 167,464 ETH + 63 tokens (~$3.5B on Ethereum alone) in a single transaction. Binance 16 and Hot Wallet 34 were drained minutes later.

**Critical finding:** The EIP-7702 delegation on Binance 14 remains **active**. The attacker can sweep again at any time.

---

## What's in this repo

| File | Purpose |
|------|---------|
| `binance-hack-forensics-2026-10-29.md` | Full ZachXBT-standard forensics report (timeline, addresses, asset breakdown, confidence scoring, laundering playbook, urgency checklist) |
| `master.py` | CLI controller for the full investigation pipeline |
| `watchlist_poller.py` | 10-second live monitoring of 7 critical addresses across Ethereum |
| `background_poll.py` | Background poller with **Aave V3 borrow window watcher** — detects if hacker deposits stolen USDT/USDC to Aave to borrow unfreezable ETH |
| `freeze_check.py` | On-chain USDT/USDC blacklist verification + Aave market pause status |
| `cross_chain_trace.py` | Cross-chain bridge tracer (LayerZero, Stargate, THORChain, Celer, Wormhole) across Ethereum, BSC, Arbitrum, Polygon, Optimism, Avalanche |
| `tx_decoder.py` | EIP-7702 delegation + sweep transaction decoder |
| `attribution_check.py` | Lazarus/DPRK IOC overlap check (cross-references tayvano/lazarus-bluenoroff-research) |
| `TASKS.md` | Action task list ranked by severity |
| `watchlist.log` | Live poll output (appended every 10s when background_poll.py runs) |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# View the full forensics report
python master.py report

# Run complete investigation pipeline
python master.py full

# Verify USDT/USDC freeze status + Aave borrow window
python master.py freeze

# Start live 10-second polling (background)
python background_poll.py

# One-shot status check with Aave detection
python quick_poll.py

# Trace cross-chain bridge movements
python master.py trace

# Check Lazarus/DPRK attribution overlap
python master.py attribution
```

---

## Key Findings

| Finding | Confidence |
|---------|------------|
| EIP-7702 delegation attack | **100%** |
| Attacker funded via Tornado Cash | **100%** |
| Binance 14 delegation still active | **100%** |
| $3.52B Ethereum / $3.3–5.8B multi-chain | **90%** |
| Lazarus/DPRK attribution | **40%** (no direct IOC overlap yet) |

---

## Urgent Actions (From TASKS.md)

1. **REVOKE EIP-7702 DELEGATION** on Binance 14 (`0x28C6c06298d514Db089934071355E5743bf21d60`) — still active, second sweep confirmed
2. Watch **Exploiter 3** (`0x8532fa14acaf483729c449b8458aeddb900543d4`) — 197,460 ETH parked, 0 outgoing txs
3. Watch **Exploiter 2** (`0x5227f603c1ee34ce3c06efe6477003bdfccb2f8c`) — 1.175B USDT + 823M USDC, could deposit to Aave to borrow unfreezable ETH
4. Trace cross-chain outflows on Arbitrum, Avalanche, Optimism, BTC, TRON
5. Check RLUSD freeze status with Ripple

---

## Disclaimer

This is defensive/investigative research only. Do not use this toolkit to move, launder, mix, or obscure funds. All on-chain data is sourced from public explorers and RPC nodes. Attribution claims are hypotheses pending independent corroboration.

**Classification:** TLP:AMBER — Share with investigative partners only

---

## License

MIT