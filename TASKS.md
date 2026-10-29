# BINANCE HACK — ACTION TASK LIST (Updated from image analysis)
**Generated**: 2026-10-29 ~23:00 UTC
**Status**: ACTIVE — All tasks pending execution

---

## 🚨 TASK 1: URGENT — Binance 14 Delegation Still Active

**Status**: PENDING
**Severity**: CRITICAL

### Evidence
- EIP-7702 delegation from Binance 14 (`0x28C6c06298d514Db089934071355E5743bf21d60`) to attacker contract (`0x63e842B0...c6fAe`) is **still active**
- Image confirms: "The wallet now runs the attacker's sweeper code"
- Second sweep executed at ~01:44 UTC (~200M USDT) — proves delegation still works

### Required Actions
1. **REVOKE EIP-7702 DELEGATION** on Binance 14 immediately
   - Send `eth_call` / transaction with empty `authorizationList` (type 0x04 tx with no auths)
   - This revokes the delegated authority
2. Audit ALL Binance hot wallets for active malicious delegations
3. Rotate signing keys for Binance 14, 16, Hot Wallet 34

### Technical Details
- Revocation: EIP-7702 AUTH tx type 0x04 with empty authorization list
- Target: Binance 14 address
- Gas: Minimal (~$0.50)
- Urgency: Every minute = risk of another sweep

---

## 🔍 TASK 2: Exploiter 3 Watch (Highest Priority)

**Status**: ACTIVE POLLING
**Address**: `0x8532fa14acaf483729c449b8458aeddb900543d4`
**Assets**: 195,460 ETH (~$442M)
**Tx Count**: 0 (has NOT moved)

### Monitoring Required
- [ ] Mempool websocket for any outgoing tx from this address
- [ ] Balance change alerts (ETH drops below 195K)
- [ ] Bridge interaction detection (THORChain, LayerZero, Stargate, Celer)
- [ ] Swap detection (Uniswap V3, Universal Router, 1inch)
- [ ] Cross-chain movement (BTC, TRON, Arbitrum, Avalanche, Optimism)

### Prediction (Bybit/Lazarus Playbook)
- ETH → BTC via cross-chain bridges
- Peel chains into 9K+ wallets
- Mixers (Wasabi, CryptoMixer, Railgun, Tornado)
- Solana/Pump.fun laundering

---

## 🔄 TASK 3: Downstream Movement Tracking

**Status**: ACTIVE
**Addresses**: 
- Exploiter 2: `0x5227f603c1ee34ce3c06efe6477003bdfccb2f8c` (18 txs)

### Confirmed Movements
| Token | Action | Time | Source |
|-------|--------|------|--------|
| ETH | 195,460 → Exploiter 3 | ~20:39 UTC | PANews |
| USDC | 780M + 43M pull | ~20:41 UTC | PANews, Image |
| RLUSD | Hopped twice in 3 min | ~20:45 UTC | Image |
| UNI | Split to new wallet | ~3:11 AM IST | Whale Alert |
| PEPE | Split to new wallet | ~3:18 AM IST | Whale Alert |

### Tracking Required
- [ ] Monitor Exploiter 2 tx count (currently 18, increasing)
- [ ] Track UNI/PEPE recipient addresses
- [ ] Track RLUSD movement (attempting to beat freeze)
- [ ] Check if downstream wallets are Tether-blacklisted

---

## 🌐 TASK 4: Cross-Chain Trace Expansion

**Status**: SCRIPTS NEED UPDATE
**New Chains to Add**: Arbitrum, Avalanche, Optimism, BTC, TRON

### Current Script Coverage
| Chain | Script Status | RPC Endpoint |
|-------|--------------|--------------|
| Ethereum | ✅ Working | eth.drpc.org |
| BSC | ⚠️ Needs addresses | bsc.drpc.org |
| Arbitrum | ⚠️ Needs addresses | arb1.drpc.org |
| Polygon | ⚠️ Needs addresses | polygon.drpc.org |
| Optimism | ⚠️ Needs addresses | optimism.drpc.org |
| Avalanche | ❌ NOT IN SCRIPT | Need RPC |
| BTC | ❌ NOT IN SCRIPT | mempool.space |
| TRON | ❌ NOT IN SCRIPT | Trongrid |

### Required Updates
1. Update `cross_chain_trace.py` — add Avalanche, Optimism, BTC, TRON
2. Update `watchlist_poller.py` — add new chain addresses
3. Get Binance-labeled addresses for each new chain from Arkham/Etherscan

---

## ❄️ TASK 5: RLUSD Freeze Check

**Status**: PENDING
**Token**: RLUSD (Ripple USD)
**Contract**: Need Ripple XRPL address
**Issue**: Attacker RLUSD hopped twice in 3 minutes to beat freeze

### Required Actions
1. Find RLUSD token contract on Ethereum (wrapped RLUSD) or XRPL address
2. Check Ripple freeze capability (rippled `frozen` flag / `lsfDisallowXRP` etc.)
3. Verify if RLUSD issuer can freeze blacklisted addresses
4. Monitor RLUSD movement from Exploiter 2

---

## 📊 TASK 6: Update Report & Push to GitHub

**Status**: PENDING
**File**: `binance-hack-forensics-2026-10-29.md`

### Content to Add
- Binance 14 still delegated (URGENT)
- Binance 16: 9 transfers (not just 1)
- 43M additional USDC pull
- Cross-chain: Arbitrum, Avalanche, Optimism, BTC, TRON
- RLUSD evasion attempt
- Exploiter 3: 195,460 ETH, 0 txs out
- Updated unfreezable: ~197K ETH + ~18K BTC
- Total estimate: $2.5B–$5.7B

---

## 🛠️ SCRIPT EXECUTION ORDER

```
1. python quick_poll.py          # Immediate status check
2. python master.py freeze       # USDT/USDC freeze verification
3. python background_poll.py     # Start continuous monitoring (background)
4. Update cross_chain_trace.py   # Add new chains
5. Update freeze_check.py        # Add RLUSD check
6. Update report.md              # Add image-confirmed details
7. git push                      # Publish updates
```

---

## 📋 LIVE POLL RESULTS (Last Check: 22:51:34 UTC)

| Address | Label | ETH | Tx Count | USDT | USDC |
|---------|-------|-----|----------|------|------|
| 0x8532fa14... | Exploiter 3 | 195,460.0008 | **0** | — | — |
| 0x5227f603... | Exploiter 2 | 2,075.47 | 18 | 1,175,464,711 | 823,000,000 |
| 0x7c8601d4... | Attacker EOA | 1.18 | 17 | — | — |
| 0x28C6c062... | Binance 14 | 1.0000 | 18.9M | — | — |
| 0xDFd5293D... | Binance 16 | 849.01 | 15.7M | — | — |
| 0xEe7aE85f... | Hot Wallet 34 | 0.34 | 1 | — | — |

---

**Background poller**: Running every 10s → `watchlist.log`
**Next check**: Run `python master.py freeze` for USDT/USDC status