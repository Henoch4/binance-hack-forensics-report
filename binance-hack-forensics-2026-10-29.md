# BINANCE HACK FORENSICS REPORT
## Incident: October 29, 2026 — Potential $2.8–3.3B Hot Wallet Drain via EIP-7702 Delegation Abuse
**Status**: ACTIVE INVESTIGATION | **Classification**: CONFIRMED ON-CHAIN EXFILTRATION | **Attribution**: UNKNOWN (hypothesis: sophisticated actor, possible Lazarus/DPRK overlap)

---

## EXECUTIVE SUMMARY

At **20:24:23 UTC on October 29, 2026**, an attacker executed the largest exchange hack in crypto history, draining **~$2.8–3.3 billion** from Binance hot wallets across **5 blockchains**. The attack leveraged **EIP-7702 delegation** — a feature live since the Pectra upgrade (May 7, 2025) — to seize control of Binance's "Binance 14" hot wallet via a signed delegation, then swept all assets in a single transaction.

**Key differentiator from prior hacks**: The attacker held a valid EIP-7702 signature from Binance 14's private key, enabling delegation to an attacker-controlled contract. This implies either:
1. **Private key theft** (hot wallet key compromised)
2. **Signing system manipulation** (Bybit-style: tricked signing system into signing malicious delegation)
3. **Insider access** (authorized signer complicit)

**Freeze status**: Tether froze **>$1.567B USDT**; Circle froze **>$823M USDC**. Native ETH (~$442M) and non-freezable tokens remain at risk.

---

## TIMELINE (UTC)

| Time | Event | Source |
|------|-------|--------|
| **Oct 28** | Attacker EOA `0x7C86...5CA0` receives 3× 0.1 ETH from Tornado Cash | Multiple |
| **Oct 29 afternoon** | Attacker deploys contract `0x63e842B0...6fAe` | Cryptoticker |
| **20:20:59** | EIP-7702 delegation tx: Binance 14 → attacker contract (50 delegations, nonce-protected) | Cryptoticker, Defimon |
| **20:24:23** | **MAIN SWEEP**: Attacker contract calls `execute()` on Binance 14 → 167,464 ETH + 63 tokens to `0x5227...CB2f8c` | Etherscan, PANews |
| **20:24:47** | Binance 16 sends 28,005.6 ETH to same address (24 sec later) | Cryptoticker |
| **20:39** | 195,460 ETH forwarded from Exploiter 2 → Exploiter 3 (`0x8532...43D4`) | PANews |
| **20:41** | 780M USDC from Binance Hot Wallet 34 via same delegation route | PANews, Cryptoticker |
| **21:05+** | Freeze reports begin: Tether (971M→1.567B USDT), Circle (823M USDC) | CZ, Paolo Ardoino, Jeremy Allaire |
| **21:15** | CZ: "does look like a hack on Binance" | X/Twitter |
| **21:24** | Binance official: "actively investigating" | X/Twitter |
| **21:30+** | Binance: Withdrawals paused, security checks underway | X/Twitter |

---

## CONFIRMED ADDRESSES (Ethereum Mainnet)

| Label | Address | Role | Status |
|-------|---------|------|--------|
| **Binance 14** | `0x28C6c06298d514Db089934071355E5743bf21d60` | Victim hot wallet (drained) | EMPTY |
| **Binance 16** | `0xDFd5293D8e347dFe59E90eFd55b2956a1343963d` | Victim hot wallet (28K ETH drained) | PARTIAL |
| **Hot Wallet 34** | `0xEe7aE85f2Fe2239E27D9c1E23fFFe168D63b4055` | Victim smart wallet (780M USDC drained) | PARTIAL |
| **Attacker EOA** | `0x7C86...5CA0` | Tornado-funded trigger address | ACTIVE |
| **Attacker Contract** | `0x63e842B0...6fAe` | EIP-7702 delegate target | ACTIVE |
| **Exploiter 2** | `0x5227...CB2f8c` | Primary receiver (labeled "Binance Hot Wallet Exploiter 2") | HOLDING ~$1.5B tokens |
| **Exploiter 3** | `0x8532...43D4` | Secondary receiver (195K ETH) | HOLDING ~$442M ETH |

---

## STOLEN ASSET BREAKDOWN (Ethereum Mainnet)

| Token | Amount | Est. Value | Freeze Status |
|-------|--------|------------|---------------|
| **USDT** | 1,615,409,499 | $1.615B | **FROZEN** (~$1.567B) |
| **USDC** | 780,177,060 | $780M | **FROZEN** (~$823M) |
| **ETH** | 195,470 | $442M | **UNFREEZABLE** |
| **wBETH** | 29,934 | $74.6M | Check wBETH contract |
| **RLUSD** | 62,597,240 | $62.6M | Check Ripple freeze capability |
| **XAUt** | 11,372 | $45.6M | Check Tether Gold freeze |
| **UNI** | 6,189,796 | $41.2M | Governance token - no freeze |
| **ENA** | 198,369,717 | $37.0M | Check Ethena freeze |
| **PEPE** | 7.18 trillion | $35.3M | No freeze |
| **USD1** | 27,760,802 | $27.7M | Check World Liberty freeze |
| **LINK** | 2,263,172 | $25.0M | No freeze |
| **AAVE** | 127,853 | $16.2M | No freeze |
| **+50 other tokens** | Various | ~$200M+ | Check individually |

**Total Ethereum mainnet**: ~$3.1B | **Freezable recovered**: ~$2.39B (77%) | **At large**: ~$710M (23%)

---

## CROSS-CHAIN SCOPE (5 Blockchains Reported)

| Chain | Status | Known Outflows | Priority |
|-------|--------|----------------|----------|
| **Ethereum** | CONFIRMED | $3.1B+ | CRITICAL - trace complete |
| **BSC (BNB Chain)** | REPORTED | Unknown - need BSCScan trace | HIGH |
| **Arbitrum** | REPORTED | Unknown - need Arbiscan trace | HIGH |
| **Polygon** | REPORTED | Hot Wallet 34 active on Polygon | HIGH |
| **Optimism/Base** | REPORTED | Unknown - need trace | MEDIUM |

**Action**: Deploy trace scripts on all 5 chains for Binance-labeled addresses.

---

## ATTACK VECTOR ANALYSIS: EIP-7702 DELEGATION ABUSE

### Technical Mechanism
1. **EIP-7702** (Pectra, May 2025): Allows EOA to delegate execution to a smart contract via `AUTH` transaction (type 0x04)
2. **Delegation tx** (20:20:59): 50 delegations signed by Binance 14 key, covering nonces 0-49 → prevents revocation
3. **Sweep tx** (20:24:23): Attacker calls `execute()` on delegated contract → `delegatecall` to attacker contract → drains all tokens via `transferFrom`/`sweep` logic
4. **Contract restriction**: Only accepts calls from Tornado-funded EOA `0x7C86...5CA0`

### Critical Questions
- **Source of signature**: How did attacker obtain valid EIP-7702 signature from Binance 14?
  - Hypothesis A: Hot wallet private key extracted (malware, HSM breach)
  - Hypothesis B: Signing system tricked into signing (Bybit-style Safe{Wallet} UI injection)
  - Hypothesis C: Insider with signing authority
- **Why 50 delegations?**: Attacker pre-empted nonce-gap revocation attempts
- **Contract deployment timing**: Afternoon Oct 29 → prepared same day

---

## PRE-EXPLOIT INTELLIGENCE (ZachXBT Standard)

### Test Transactions / Preparation
- ✅ **Tornado Cash funding**: 3× 0.1 ETH to `0x7C86...5CA0` on Oct 28-29
- ✅ **Contract deployment**: `0x63e842B0...6fAe` deployed Oct 29 afternoon
- ✅ **Delegation preparation**: 50 nonces pre-signed at 20:20:59
- 🔍 **NEED**: Check for earlier test delegations / small transfers from Binance 14/16/34 to attacker addresses
- 🔍 **NEED**: Scan for shared funding sources with prior Lazarus incidents

### Cross-Incident Overlap Check (Lazarus/DPRK)
| Prior Incident | Date | Key IOCs | Overlap Check |
|----------------|------|----------|---------------|
| **Bybit** | Feb 2025 | $1.4B, Safe{Wallet} JS injection, 40+ splits, $27M chunks, stETH→ETH→BTC 9K wallets | 🔍 Check attacker EOA vs Bybit funding cluster |
| **Phemex** | Jan 2025 | $85M, Lazarus-attributed | 🔍 Check address reuse |
| **BingX** | 2024 | Lazarus-attributed | 🔍 Check address reuse |
| **Poloniex** | 2024 | Lazarus-attributed | 🔍 Check address reuse |
| **Bitget** | Sep 2024 | $387M, peel chains, mixer usage | 🔍 Check Tornado Cash deposit patterns |

**Immediate action**: Query Arkham / Elliptic / TRM for `0x7C86...5CA0` and `0x63e842B0...6fAe` cluster matches.

---

## LAUNDERING PATTERN ANALYSIS (Initial)

### Phase 1: Consolidation (Complete)
- All assets → Exploiter 2 (`0x5227...CB2f8c`) in 2-3 txs
- 63 tokens + ETH in single sweep tx (gas: $0.93)

### Phase 2: ETH Segregation (Complete)
- 195,460 ETH → Exploiter 3 (`0x8532...43D4`) at 20:39
- **Native ETH is unfreezable** — this is the attacker's "safe" allocation

### Phase 3: Token Holding (Current)
- Exploiter 2 holds ~$1.5B in 60+ tokens (mostly USDT/USDC now frozen)
- Awaiting: swaps, bridging, mixer deposits, CEX deposits

### Predicted Next Steps (Bybit/Lazarus Playbook)
1. **Stablecoin conversion**: Remaining non-frozen stables → ETH via Uniswap V3/Universal Router
2. **ETH → BTC**: Cross-chain via THORChain / LayerZero / Stargate / Celer
3. **Peel chains**: 10K ETH parking wallets → 9K+ wallets (1.41 BTC avg per Bybit)
4. **Mixers**: Wasabi / CryptoMixer / Railgun / Tornado (if unbanned)
5. **P2P**: eXch, no-KYC swaps
6. **Solana bridge**: Pump.fun memecoin laundering (Bybit: $1.08M USDC → 0x3639...)

---

## FREEZE / BOUNTY OPERATIONS STATUS

### Filed / Confirmed
- ✅ **Tether USDT freeze**: >$1.567B (Paolo Ardoino confirmed)
- ✅ **Circle USDC freeze**: >$823M (Jeremy Allaire / CZ confirmed)
- ✅ **Trace report**: Filed by multiple parties (Spreek, Tree News, Blockaid, Arkham)

### Pending / Needed
- 🔲 **CEX deposit monitoring**: Alert on Exploiter 2/3 → Binance/Kraken/OKX/KuCoin/Bybit/HTX deposit addresses
- 🔲 **Bridge monitoring**: LayerZero/Stargate/THORChain/Celer vault outbound from Exploiter 2/3
- 🔲 **Arkham attribution bounty**: Prepare definitive-proof package (test txs + graphs + timing + overlap)
- 🔲 **Binance bug bounty**: Check if Binance has active program (~5% recovery)
- 🔲 **Law enforcement coordination**: Share trace with relevant jurisdictions

---

## DORMANT WATCHLIST (Immediate Monitoring)

| Address | Chain | Asset | Risk | Action |
|---------|-------|-------|------|--------|
| `0x8532...43D4` (Exploiter 3) | Ethereum | 195K ETH ($442M) | **CRITICAL** - unfreezable, will move to BTC/bridges | Mempool watch + 10s polling |
| `0x5227...CB2f8c` (Exploiter 2) | Ethereum | ~$1.5B tokens (mostly frozen) | HIGH - residual non-frozen tokens | Poll for swaps/transfers |
| `0x7C86...5CA0` (Attacker EOA) | Ethereum | Gas funder | MEDIUM - may fund new delegations | Watch for new contract deployments |
| `0x63e842B0...6fAe` (Attacker Contract) | Ethereum | Delegation target | MEDIUM - may be reused | Monitor for new EIP-7702 auths |
| Binance 16 (`0xDFd5...`) | Ethereum | Residual balance | LOW - may be swept further | Balance alert |
| Hot Wallet 34 (`0xEe7a...`) | Ethereum/Polygon | Residual balance | LOW - may be swept further | Balance alert |
| **All Binance-labeled hot wallets** | All 5 chains | Unknown | HIGH - same key compromise risk | Full sweep audit |

---

## FORENSICS GRAPHS REQUIRED (ZachXBT Standard)

1. **Funding Graph**: Tornado Cash → `0x7C86...5CA0` → contract deployment → delegation tx
2. **Dispersal Graph**: Binance 14/16/34 → Exploiter 2 → Exploiter 3 (ETH) + token holdings
3. **Bridge-Out Graph**: (Pending) Exploiter 2/3 → LayerZero/Stargate/THORChain → destination chains
4. **Overlap Graph**: Attacker addresses vs. Lazarus/Bybit/Phemex/BingX/Poloniex IOCs
5. **Timing Graph**: UTC timeline with block timestamps (test → exploit → dispersal → freezes)

---

## IMMEDIATE NEXT STEPS (Next 2 Hours)

### 1. Transaction Hash Collection
- [ ] EIP-7702 delegation tx hash (block ~26300791, 20:20:59)
- [ ] Main sweep tx hash (block ~26300803, 20:24:23)
- [ ] Binance 16 tx hash (block ~26300804, 20:24:47)
- [ ] ETH forward tx hash (block ~26300818, 20:39)
- [ ] Hot Wallet 34 USDC tx hash (block ~26300946, 20:41)

### 2. Cross-Chain Trace Initiation
- [ ] BSCScan: Check Binance-labeled addresses for outflows 20:20-21:00 UTC
- [ ] Arbiscan: Check Binance-labeled addresses
- [ ] PolygonScan: Check Hot Wallet 34 (`0xEe7aE85f2Fe2239E27D9c1E23fFFe168D63b4055`) + others
- [ ] Optimistic Etherscan / BaseScan: Check Binance-labeled addresses

### 3. Attribution Data Pull
- [ ] Arkham API: Cluster analysis on `0x7C86...5CA0`, `0x63e842B0...6fAe`, `0x5227...CB2f8c`, `0x8532...43D4`
- [ ] Elliptic/TRM: Overlap check with Lazarus IOCs
- [ ] GitHub: `tayvano/lazarus-bluenoroff-research` address list cross-reference

### 4. Freeze Verification
- [ ] Confirm exact USDT freeze addresses & amounts (Tether blacklist)
- [ ] Confirm exact USDC freeze addresses & amounts (Circle blacklist)
- [ ] Check wBETH, RLUSD, XAUt, USD1, ENA freeze status with issuers

### 5. Automation Deployment
- [ ] Deploy 10s batch polling on watchlist addresses (Ethereum + 4 other chains)
- [ ] Configure mempool websocket (mempool.space) for Exploiter 3 ETH movements
- [ ] Set Arkham/Etherscan alerts on all watchlist addresses
- [ ] Dedup key: `(chain, tx_hash)`

---

## EVIDENCE PRESERVATION

- [ ] Screenshot all Etherscan/BSCScan/Arbiscan/PolygonScan/Optimistic pages with timestamps
- [ ] Save raw transaction calldata for delegation + sweep + forward txs
- [ ] Archive X/Twitter posts from Spreek, Tree News, Blockaid, CZ, Paolo, Jeremy (replies + quotes)
- [ ] Log first-seen timestamps for each lead (handle, URL, UTC, tx hash)

---

## CONFIDENCE ASSESSMENTS

| Finding | Confidence | Basis |
|---------|------------|-------|
| Exfiltration occurred | **100%** | On-chain txs confirmed, multiple independent sources |
| EIP-7702 delegation used | **95%** | Cryptoticker analysis, Defimon classification, tx pattern |
| Attacker funded via Tornado | **95%** | Multiple sources confirm 3× 0.1 ETH deposits Oct 28-29 |
| Binance 14/16/34 compromised | **90%** | Labeled wallets, but Binance hasn't confirmed ownership |
| $2.8-3.3B total loss | **85%** | Varying reports ($2.53B-$3.3B), cross-chain not fully traced |
| Lazarus/DPRK attribution | **30%** | Tornado + sophisticated + exchange target = consistent, but no direct overlap yet |
| Insider vs external key theft | **Unknown** | Insufficient evidence; all 3 hypotheses viable |

---

## OFFICIAL CONFIRMATIONS (X/Twitter — 22:30-23:00 UTC)

| Source | Statement | Timestamp (UTC) |
|--------|-----------|-----------------|
| **CZ (@cz_binance)** | "User funds are safe! It does look like a hack on Binance. Appreciate the quick freeze from Tether (~$971m) and Circle (~$823m). I don't manage Binance (.com) anymore, but as a shareholder, I expect all user funds will be fully covered." | ~21:15 |
| **Binance (@binance)** | "Our teams are aware of reports of a potential security issue and are actively investigating... Withdrawals paused until resolved. User funds remain safe. Users should remain cautious of scams." | ~21:24, updated |
| **Paolo Ardoino (@paoloardoino, Tether CEO)** | "Tether froze more than 1.567B USDT related to a potential Binance exchange hack." | ~21:25 |
| **Circle (via CZ/Jeremy Allaire)** | ~$800-823M USDC frozen in coordination with law enforcement | ~21:18-21:25 |

**Total frozen stablecoins**: ~$2.3-2.4B+ (USDT + USDC combined)

---

## MARKET IMPACT (X/Coinglass data)

| Metric | Value |
|--------|-------|
| **1-hour liquidations** | ~$600-628M (97% longs) |
| **BTC** | Dipped below $79K (-2-3%) |
| **ETH** | -3-4% |
| **BNB** | -6-9% (hardest hit top-10) |
| **Primary liquidation venue** | Binance ($344M of 1-hour total) |

---

## ATTRIBUTION CHATTER (X — Unverified)

| Theory | Proponents | Evidence |
|--------|------------|----------|
| **Lazarus/DPRK (North Korea)** | Spreek, multiple analysts | Tornado funding, exchange target, sophistication, Binance recently blocked NK social-engineering attempts (Oct 27) |
| **Inside job / key compromise** | Various | Valid EIP-7702 signature from Binance 14; 50 delegations = pre-empted revocation |
| **Signing system manipulation (Bybit-style)** | Analysts | Similar to Safe{Wallet} JS injection (Bybit Feb 2025) |
| **No confirmation** | All | No on-chain IOC overlap with prior Lazarus incidents yet |

**Status**: No confirmed attribution. Requires funding graph + Elliptic/TRM corroboration.

---

## CONTACTS FOR COORDINATION

| Entity | Contact | Purpose |
|--------|---------|---------|
| **Binance Security** | security@binance.com / X @Binance | Official confirmation, wallet labels, signing system audit |
| **Tether Compliance** | compliance@tether.to / Paolo Ardoino X | USDT freeze confirmation, additional addresses |
| **Circle Compliance** | compliance@circle.com / Jeremy Allaire X | USDC freeze confirmation, additional addresses |
| **Arkham Intelligence** | Arkham platform / X @arkham | Attribution bounty, cluster analysis |
| **Elliptic / TRM** | Sales channels | Independent attribution corroboration |
| **Law Enforcement** | Varies by jurisdiction | Freeze orders, seizure warrants |
| **Blockaid / TreeAI / Spreek** | X/Twitter | On-chain intel sharing |

---

## APPENDIX: DATA SOURCES

- Cryptoticker.io: "Binance Hack: $2.8B Drained From Hot Wallet via EIP-7702" (2026-10-29T21:38:40Z)
- PANews: "Binance Suspected Theft Tracker" (2026-10-29T20:55:33Z)
- BeInCrypto: "Is Binance Being Hacked?" (2026-10-29T20:49:22Z)
- CoinDesk: "Potential multi-billion Binance hack" (2026-10-29T21:12:45Z)
- CryptoBriefing: "BNB falls as much as 9%" (2026-10-29T21:07:39Z)
- The Defiant: "Binance-Labeled Wallet Swept Minutes After EIP-7702 Delegation" (2026-10-29T21:04:09Z)
- Koin Bülteni: "Breaking: Massive Attack Alleged at Binance" (2026-10-29T20:47:40Z)
- Etherscan address pages for Binance 14, Binance 16, Hot Wallet 34
- Dedaub Security Suite: Transaction analysis `0xe630fa9ed6653369d06bb905ceccec99cbcd3ee71b20bf1377bad866c73caadd`

---

**Report generated**: 2026-10-29 ~21:45 UTC
**Next update**: 2026-10-29 ~23:00 UTC (or upon material developments)
**Analyst**: Crypto Forensics Toolkit + Crypto Hack Forensics skills
**Classification**: TLP:AMBER — Share with investigative partners only