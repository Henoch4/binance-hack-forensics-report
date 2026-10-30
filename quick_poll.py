import asyncio
import aiohttp

async def test_poll():
    rpc = 'https://eth.drpc.org'
    USDT_CONTRACT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    USDC_CONTRACT = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    AAVE_LENDING_POOL = "0x87869991452208843334988248bDd9e514747e33"
    AAVE_USDT_ATOKEN = "0x8dc4C39555C7f19c77c9e07229d994C7e135B964"
    AAVE_USDC_ATOKEN = "0x9bA8DC8c31F8222b93587f4978e00504d7327F78"
    ALLOWANCE_SELECTOR = "0xdda051c1"
    GET_RESERVE_DATA_SELECTOR = "0x6d475d8c"

    addresses = {
        'Exploiter 3': '0x8532fa14acaf483729c449b8458aeddb900543d4',
        'Exploiter 2': '0x5227f603c1ee34ce3c06efe6477003bdfccb2f8c',
        'Attacker EOA': '0x7c8601d4645b93cea45f71e118a729332e6b5ca0',
        'Binance 14': '0x28C6c06298d514Db089934071355E5743bf21d60',
    }

    async def rpc_call(method, params):
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        async with session.post(rpc, json=payload) as resp:
            content_type = resp.headers.get('Content-Type', '')
            if 'application/json' not in content_type:
                text = await resp.text()
                raise Exception(f"Non-JSON response ({resp.status}): {text[:200]}")
            return await resp.json()

    async def get_reserve_paused(token):
        data = GET_RESERVE_DATA_SELECTOR + token[2:].lower().zfill(64)
        result = await rpc_call("eth_call", [{
            "to": AAVE_LENDING_POOL,
            "data": data
        }, "latest"])
        hex_result = result.get("result", "0x")
        if hex_result == "0x" or len(hex_result) < 130:
            return None
        configuration = int(hex_result[2:66], 16)
        return bool(configuration & 1)

    async def get_bal(contract, addr):
        data = "0x70a08231" + addr[2:].lower().zfill(64)
        result = await rpc_call("eth_call", [{
            "to": contract,
            "data": data
        }, "latest"])
        hex_result = result.get("result", "0x0")
        if hex_result == "0x" or not hex_result:
            return 0
        return int(hex_result, 16)

    async def get_allow(token, addr):
        data = ALLOWANCE_SELECTOR + addr[2:].lower().zfill(64) + AAVE_LENDING_POOL[2:].lower().zfill(64)
        result = await rpc_call("eth_call", [{
            "to": token,
            "data": data
        }, "latest"])
        hex_result = result.get("result", "0x0")
        if hex_result == "0x" or not hex_result:
            return 0
        return int(hex_result, 16)

    async with aiohttp.ClientSession() as session:
        # Check Aave market status
        usdt_paused = await get_reserve_paused(USDT_CONTRACT)
        usdc_paused = await get_reserve_paused(USDC_CONTRACT)
        print(f"Aave USDT market: {'PAUSED 🚨' if usdt_paused else 'ACTIVE'}")
        print(f"Aave USDC market: {'PAUSED 🚨' if usdc_paused else 'ACTIVE'}")

        for label, addr in addresses.items():
            bal_res = await rpc_call('eth_getBalance', [addr, 'latest'])
            cnt_res = await rpc_call('eth_getTransactionCount', [addr, 'latest'])
            eth_bal = int(bal_res.get('result','0x0'),16) / 1e18
            tx_cnt = int(cnt_res.get('result','0x0'),16)
            if label == 'Exploiter 2':
                usdt = await get_bal(USDT_CONTRACT, addr) / 1e6
                usdc = await get_bal(USDC_CONTRACT, addr) / 1e6
                ausdt = await get_bal(AAVE_USDT_ATOKEN, addr) / 1e6
                ausdc = await get_bal(AAVE_USDC_ATOKEN, addr) / 1e6

                usdt_allow = await get_allow(USDT_CONTRACT, addr)
                usdc_allow = await get_allow(USDC_CONTRACT, addr)

                alert = ""
                if ausdt > 0 or ausdc > 0:
                    alert = " ⚠️⚠️ AAVE DEPOSIT DETECTED! HACKER BORROWING ETH!"
                elif usdt_allow > 0 or usdc_allow > 0:
                    alert = " ⚠️ AAVE ALLOWANCE SET - DEPOSIT IMMINENT!"

                print(f"{label}: {eth_bal:.4f} ETH | {tx_cnt} txs | {usdt:,.0f} USDT | {usdc:,.0f} USDC | aUSDT:{ausdt:,.0f} aUSDC:{ausdc:,.0f}{alert}")
            else:
                print(f"{label}: {eth_bal:.4f} ETH | {tx_cnt} txs | {addr[:10]}...")

asyncio.run(test_poll())