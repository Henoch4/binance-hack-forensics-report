# BINANCE HACK FORENSICS REPORT
## Incident: October 29–30, 2026 — Largest Exchange Hack in History via EIP-7702 Delegation Abuse
**Status**: ACTIVE INVESTIGATION | **Classification**: CONFIRMED ON-CHAIN EXFILTRATION | **Attribution**: UNKNOWN (hypothesis: sophisticated actor, possible Lazarus/DPRK overlap)
**Last Updated**: October 30, 2026 ~00:00 UTC

---

## EXECUTIVE SUMMARY

At **20:24:23 UTC on October 29, 2026**, an attacker executed the largest exchange hack in crypto history, draining **~$2.5–5.8 billion** from Binance hot wallets across **7+ blockchains**. The attack leveraged **EIP-7702 delegation** — a feature live since the Pectra upgrade (May 7, 2025) — to seize control of Binance's "Binance 14" hot wallet via a signed delegation, then swept all assets in a single transaction.

**Key differentiator from prior hacks**: The attacker held a valid EIP-7702 signature from Binance 14's private key, enabling delegation to an attacker-controlled contract. This implies either:
1. **Private key theft** (hot wallet key compromised)
2. **Signing system manipulation** (Bybit-style: tricked signing system into signing malicious delegation)
3. **Insider access** (authorized signer complicit)

**Freeze status**: Tether froze **>$1.567B USDT**; Circle froze **>$823M USDC**; Ripple RLUSD partially frozen. Native ETH (~$442M), BTC (~$45M), TRX, and non-freezable tokens remain at risk.

**🚨 CRITICAL**: Binance 14 EIP-7702 delegation is **STILL ACTIVE** — second sweep confirmed at ~01:44 UTC. Binance 16 being drained in real-time (849 ETH → 0.21 ETH between 22:54–23:01 UTC).

---

## TIMELINE (UTC)

| Time | Event | Source |
|------|-------|--------|
| **Oct 28** | Attacker EOA `0x7c8601d4645b93cea45f71e118a729332e6b5ca0` receives 3× 0.1 ETH from Tornado Cash | Multiple |
| **Oct 29 afternoon** | Attacker deploys sweeper contract `0x63e842B0...c6fAe` | Cryptoticker, Image |
| **20:20:59** | EIP-7702 delegation tx: Binance 14 → attacker contract (50 delegations, nonce-protected) | Cryptoticker, Defimon |
| **20:24:23** | **MAIN SWEEP #1**: Attacker contract calls `execute()` on Binance 14 → 167,464 ETH + 1.615B USDT + 60+ tokens to `0x5227f603c1ee34ce3c06efe6477003bdfccb2f8c` | Etherscan, PANews |
| **20:24:47** | Binance 16 sends 28,005 ETH to same address (24 sec later) | Cryptoticker |
| **20:39** | 195,460 ETH forwarded from Exploiter 2 → Exploiter 3 (`0x8532fa14acaf483729c449b8458aeddb900543d4`) | PANews, Image |
| **20:41** | 780M USDC from Binance Hot Wallet 34 via same delegation route | PANews, Cryptoticker |
| **20:45** | 43M additional USDC pulled from Binance smart account | Image |
| **21:05+** | Freeze reports begin: Tether (971M→1.567B USDT), Circle (823M USDC) | CZ, Paolo Ardoino, Jeremy Allaire |
| **21:15** | CZ: "does look like a hack on Binance" | X/Twitter |
| **21:24** | Binance official: "actively investigating" | X/Twitter |
| **21:30+** | Binance: Withdrawals paused, security checks underway | X/Twitter |
| **01:44 UTC** | **SECOND SWEEP**: ~200M more USDT from Binance 14 (still delegated) | Unchained |
| **22:00+** | Aave freezes lending markets; Tether blacklists 7 downstream wallets | The Block, Unchained |
| **22:30+** | Arkham labels "binance-hacker-1029" cluster (~$5.84B) | Arkham |
| **23:00+** | Cross-chain confirmed: Arbitrum ~$19.5M, Avalanche ~$24M | Blockaid |
| **23:00+ (LIVE)** | **Binance 16 draining**: 849 ETH → 0.21 ETH in progress (delegation active) | Live poller |
| **23:00+ (LIVE)** | Exploiter 2 at 20 txs, downstream movement ongoing | Live poller |

---

## CONFIRMED ADDRESSES (Ethereum Mainnet)

| Label | Address | Role | Status |
|-------|---------|------|--------|
| **Binance 14** | `0x28C6c06298d514Db089934071355E5743bf21d60` | Victim hot wallet (drained, **STILL DELEGATED**) | 0.96 ETH residual |
| **Binance 16** | `0xDFd5293D8e347dFe59E90eFd55b2956a1343963d` | Victim hot wallet (28K ETH drained, **being swept live**) | 0.21 ETH residual |
| **Hot Wallet 34** | `0xEe7aE85f2Fe2239E27D9c1E23fFFe168D63b4055` | Victim smart wallet (780M+ USDC drained) | 0.34 ETH residual |
| **Attacker EOA** | `0x7c8601d4645b93cea45f71e118a729332e6b5ca0` | Tornado-funded trigger / delegation signer | 1.18 ETH, 17 txs |
| **Attacker Contract** | `0x63e842B0...c6fAe` | EIP-7702 delegate target (sweep logic) | ACTIVE |
| **Exploiter 2** | `0x5227f603c1ee34ce3c06efe6477003bdfccb2f8c` | Primary receiver ("Binance Hot Wallet Exploiter 2") | **1,175M USDT, 823M USDC, 2,075 ETH, 20 txs** |
| **Exploiter 3** | `0x8532fa14acaf483729c449b8458aeddb900543d4` | ETH parking (195K ETH) | **195,460 ETH, 0 txs out — CRITICAL** |
| **Downstream 1** | (TBD) | Tether-blacklisted (~205M USDT) | FROZEN |
| **Downstream 2** | (TBD) | Tether-blacklisted (~205M USDT) | FROZEN |

---

## STOLEN ASSET BREAKDOWN (Ethereum Mainnet)

| Token | Amount | Est. Value | Freeze Status |
|-------|--------|------------|---------------|
| **USDT** | 1,615,409,499 | $1.615B | **FROZEN** (~1.567B primary + 205M downstream) |
| **USDC** | 823,000,000 + 43M additional | $866M | **FROZEN** (~823M) |
| **ETH** | 195,470 | $442M | **UNFREEZABLE** (Exploiter 3) |
| **wBETH** | 29,934 | $74.6M | Check wBETH contract |
| **RLUSD** | 62,597,240 | $62.6M | Attacker hopped twice in 3 min to beat freeze — check Ripple |
| **XAUt** | 11,372 | $45.6M | Check Tether Gold freeze |
| **UNI** | 6,189,796 | $41.2M | Split to new wallet (Whale Alert) |
| **ENA** | 198,369,717 | $37.0M | Check Ethena freeze |
| **PEPE** | 7.18 trillion | $35.3M | Split to new wallet (Whale Alert) |
| **USD1** | 27,760,802 | $27.7M | Check World Liberty freeze |
| **LINK** | 2,263,172 | $25.0M | No freeze |
| **AAVE** | 127,853 | $16.2M | No freeze (Aave markets frozen) |
| **+50 other tokens** | Various | ~$200M+ | Check individually |

**Total Ethereum mainnet**: ~$3.52B (Unchained) | **Freezable recovered**: ~$2.6B+ (74%) | **At large**: ~$900M+ (26%)

**Multi-chain total (Arkham/Blockaid)**: **$3.3B–$5.8B** across Ethereum, Arbitrum, Avalanche, BSC, Polygon

---

## CROSS-CHAIN SCOPE (7+ Blockchains Confirmed)

| Chain | Status | Known Outflows | Priority |
|-------|--------|----------------|----------|
| **Ethereum** | CONFIRMED | **$3.52B** (Unchained) | CRITICAL - trace active |
| **Arbitrum** | CONFIRMED | **~$19.5M** (Blockaid) | HIGH - trace needed |
| **Avalanche** | CONFIRMED | **~$24M** (Blockaid) | HIGH - trace needed |
| **Optimism** | CONFIRMED | Reported (Arkham) | HIGH - trace needed |
| **BSC (BNB Chain)** | REPORTED | Unknown - need BSCScan trace | HIGH |
| **Polygon** | REPORTED | Hot Wallet 34 active on Polygon | HIGH |
| **Bitcoin** | REPORTED | ~18K BTC outflow (Image estimates) | HIGH - unfreezable |
| **TRON** | REPORTED | Reported outflow (Image) | HIGH - unfreezable |

**Action**: Deploy trace scripts on all chains for Binance-labeled addresses.

**New: Aave froze lending markets** to prevent borrowing against stolen collateral.
**New: Tether blacklisted 7 downstream wallets** (2 holding ~205M USDT combined).
**New: Ripple RLUSD** — attacker hopped twice in 3 minutes to beat freeze; check Ripple freeze status.

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

## LAUNDERING PATTERN ANALYSIS (Updated)

### Phase 1: Consolidation (Complete)
- All assets → Exploiter 2 (`0x5227f603c1ee34ce3c06efe6477003bdfccb2f8c`) in 2-3 txs
- 63 tokens + ETH in single sweep tx (gas: $0.93)

### Phase 2: ETH Segregation (Complete)
- 195,460 ETH → Exploiter 3 (`0x8532fa14acaf483729c449b8458aeddb900543d4`) at 20:39
- **Native ETH is unfreezable** — this is the attacker's "safe" allocation
- **0 txs out from Exploiter 3** — has not moved yet (CRITICAL watch)

### Phase 3: Token Holding + Downstream Movement (Active)
- Exploiter 2 holds ~$1.5B in 60+ tokens (mostly USDT/USDC now frozen)
- **~$900M+ already moved downstream** to 7+ wallets (Unchained)
- **Tether blacklisted 7 downstream wallets** (2 holding ~205M USDT each)
- **Second sweep at 01:44 UTC**: ~200M more USDT from Binance 14 (still delegated!)
- Aave froze lending markets to prevent borrowing

### Predicted Next Steps (Bybit/Lazarus Playbook)
1. **Exploiter 3 ETH → BTC**: Cross-chain via THORChain / LayerZero / Stargate / Celer (PRIMARY RISK)
2. **Stablecoin conversion**: Remaining non-frozen stables → ETH via Uniswap V3/Universal Router
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
| `0x8532fa14acaf483729c449b8458aeddb900543d4` (Exploiter 3) | Ethereum | 195K ETH ($442M) | **CRITICAL** - unfreezable, 0 txs out, will bridge to BTC | Mempool watch + 10s polling + bridge alerts |
| `0x5227f603c1ee34ce3c06efe6477003bdfccb2f8c` (Exploiter 2) | Ethereum | ~$1.5B tokens (mostly frozen) | HIGH - residual non-frozen, downstream movement | Poll for swaps/transfers + downstream tracking |
| `0x7c8601d4645b93cea45f71e118a729332e6b5ca0` (Attacker EOA) | Ethereum | Gas funder | MEDIUM - may fund new delegations | Watch for new contract deployments |
| `0x63e842B0...6fAe` (Attacker Contract) | Ethereum | Delegation target | MEDIUM - Binance 14 STILL DELEGATED | Monitor for new EIP-7702 auths + revocation |
| Binance 14 (`0x28C6c062...`) | Ethereum | 129 ETH residual | **HIGH - STILL DELEGATED** | **URGENT: Revoke delegation** |
| Binance 16 (`0xDFd5293D...`) | Ethereum | 849 ETH residual | MEDIUM - may be swept further | Balance alert |
| Hot Wallet 34 (`0xEe7aE85f...`) | Ethereum/Polygon | 0.34 ETH residual | MEDIUM - may be swept further | Balance alert |
| **Downstream USDT wallets** | Ethereum | ~205M USDT each | **FROZEN** - Tether blacklisted | Monitor for thaw attempts |
| **All Binance-labeled hot wallets** | All chains | Unknown | HIGH - same key compromise risk | Full sweep audit + delegation check |

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
- [ ] Main sweep tx hash (0x53bd38b816c23e74134786c29a8c18d792777998a3b9326047b583100e88e2f3)
- [ ] Binance 16 tx hash (block ~26300804, 20:24:47)
- [ ] ETH forward tx hash (Exploiter 2 → Exploiter 3, ~20:39)
- [ ] Hot Wallet 34 USDC tx hash (block ~26300946, 20:41)
- [ ] **Second sweep tx hash** (~01:44 UTC, ~200M USDT)

### 2. Cross-Chain Trace Initiation
- [ ] **Arbitrum**: Trace ~$19.5M outflows (Blockaid confirmed)
- [ ] **Avalanche**: Trace ~$24M outflows (Blockaid confirmed)
- [ ] **BSCScan**: Check Binance-labeled addresses for outflows 20:20-21:00 UTC
- [ ] **PolygonScan**: Check Hot Wallet 34 (`0xEe7aE85f2Fe2239E27D9c1E23fFFe168D63b4055`) + others
- [ ] **Optimistic Etherscan / BaseScan**: Check Binance-labeled addresses

### 3. Attribution Data Pull
- [ ] Arkham API: Cluster analysis on all 9 addresses + "binance-hacker-1029" label
- [ ] Elliptic/TRM: Overlap check with Lazarus IOCs
- [ ] GitHub: `tayvano/lazarus-bluenoroff-research` address list cross-reference
- [ ] **Check Binance Oct 27 NK social-engineering attempt IOCs** for overlap

### 4. Freeze Verification & Downstream Tracking
- [ ] Confirm exact USDT freeze addresses & amounts (Tether blacklist - primary + 7 downstream)
- [ ] Confirm exact USDC freeze addresses & amounts (Circle blacklist)
- [ ] Check wBETH, RLUSD, XAUt, USD1, ENA freeze status with issuers
- [ ] **Track 7 downstream USDT wallets** for movement/thaw attempts

### 5. Urgent Binance Security Actions
- [ ] **REVOKE EIP-7702 DELEGATION** on Binance 14 (still active, second sweep occurred)
- [ ] Audit all hot wallet delegations across chains
- [ ] Rotate signing keys for all hot wallets
- [ ] Verify no other wallets have active malicious delegations

### 6. Automation Deployment
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
| EIP-7702 delegation used | **100%** | Confirmed by Blockaid, Cryptoticker, Defimon, tx analysis |
| Attacker funded via Tornado | **100%** | 3× 0.1 ETH deposits Oct 28-29 confirmed on-chain |
| Binance 14/16/34 compromised | **95%** | Labeled wallets, multiple sweep txs, official Binance acknowledgment |
| **$3.52B Ethereum / $3.3-5.8B multi-chain** | **90%** | Unchained $3.52B, Arkham $5.84B, Blockaid $3.3B cross-chain |
| **Lazarus/DPRK attribution** | **40%** | Tornado + exchange target + NK social-engineering (Oct 27) + sophistication, but no direct IOC overlap yet |
| **Insider vs external key theft** | **Unknown** | All 3 hypotheses viable; 50 delegations = sophisticated prep |
| **Delegation still active** | **100%** | Second sweep at 01:44 UTC confirms Binance 14 still delegated |

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