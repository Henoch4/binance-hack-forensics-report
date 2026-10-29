import asyncio
import aiohttp

async def test_poll():
    rpc = 'https://eth.drpc.org'
    addresses = {
        'Exploiter 3': '0x8532fa14acaf483729c449b8458aeddb900543d4',
        'Exploiter 2': '0x5227f603c1ee34ce3c06efe6477003bdfccb2f8c',
        'Attacker EOA': '0x7c8601d4645b93cea45f71e118a729332e6b5ca0',
        'Binance 14': '0x28C6c06298d514Db089934071355E5743bf21d60',
    }
    
    async with aiohttp.ClientSession() as session:
        for label, addr in addresses.items():
            # ETH balance
            bal_res = await session.post(rpc, json={'jsonrpc':'2.0','method':'eth_getBalance','params':[addr,'latest'],'id':1})
            bal_data = await bal_res.json()
            eth_bal = int(bal_data.get('result','0x0'),16) / 1e18
            
            # Tx count
            cnt_res = await session.post(rpc, json={'jsonrpc':'2.0','method':'eth_getTransactionCount','params':[addr,'latest'],'id':1})
            cnt_data = await cnt_res.json()
            tx_cnt = int(cnt_data.get('result','0x0'),16)
            
            print(f'{label}: {eth_bal:.4f} ETH | {tx_cnt} txs | {addr[:10]}...')

asyncio.run(test_poll())