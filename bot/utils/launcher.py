import os
import glob
import asyncio
import argparse
from itertools import cycle

from pyrogram import Client, compose
from better_proxy import Proxy

from bot.config import settings
from bot.utils import logger
from bot.core.tapper import run_tapper
from data import Data


start_text = """

▀▀█▀▀ █▀▀█ █▀▀█ ░█▀▀▀█ █   █ █▀▀█ █▀▀█ ░█▀▀█ █▀▀█ ▀▀█▀▀ 
 ░█   █▄▄█ █  █  ▀▀▀▄▄ █▄█▄█ █▄▄█ █  █ ░█▀▀▄ █  █   █   
 ░█   ▀  ▀ █▀▀▀ ░█▄▄▄█  ▀ ▀  ▀  ▀ █▀▀▀ ░█▄▄█ ▀▀▀▀   ▀  
"""

global tg_clients

def get_session_names() -> list[str]:
    session_names = glob.glob('sessions/*.session')
    session_names = [os.path.splitext(os.path.basename(file))[0] for file in session_names]

    return session_names

def get_proxies() -> list[Proxy]:
    
    
    proxies = []

    with open(file='bot/config/proxies.txt', encoding='utf-8-sig') as file:
        for line in file:
            proxy = line.strip()  # Remove leading/trailing whitespace
            parts = proxy.split('|')  # Split the line by '|'
            if len(parts) == 2:
                proxies.append(proxy)
    return proxies


async def get_tg_clients() -> list[Data]:

    proxies = get_proxies()
    tg_clients = []
    for proxy in proxies:
        parts = proxy.split('|')
        client = Data(
            name=parts[0],
            proxy=Proxy.from_str(proxy=parts[1]).as_url,
            json_name=parts[0]
        )
        tg_clients.append(client)

    return tg_clients


async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")

    logger.info(f"Detected {len(get_session_names())} sessions | {len(get_proxies())} proxies")

    action = parser.parse_args().action

    if not action:
        print(start_text)
        
        tg_clients = await get_tg_clients()
        for client in tg_clients:
            print(f'Proxy: {client.proxy}, JSON Name: {client.json_name}')
        await run_tasks(tg_clients=tg_clients)


async def run_tasks(tg_clients: list[Data]):
    tasks = [asyncio.create_task(run_tapper(tg_client=tg_client))
        for tg_client in tg_clients]
    await asyncio.gather(*tasks)
