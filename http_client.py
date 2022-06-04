import asyncio
import random
from config import SERVER_LIST, BUFFER, PORT, PROXY_PORT
from print_bw import upload_queue, download_queue
from utils import copy


async def handle_http(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    socket = writer.transport.get_extra_info("peername")
    header = await reader.readline()
    host = header.decode()[:-11]
    proxy = random.choice(SERVER_LIST)
    print(f"HTTP {socket[0]}:{socket[1]} --{proxy}--> {host}")
    pr, pw = await asyncio.open_connection(proxy, PROXY_PORT)
    pw.write(header)
    pw.write(b"X-T5-Auth: ZjQxNDIh\r\n")
    pw.write(b"User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 SP-engine/2.44.0 baiduboxapp/13.6.0.10 (Baidu; P2 15.0)\r\n")
    pw.write(b'Proxy-Connection: Keep-Alive\r\n\r\n')

    asyncio.create_task(copy(writer, pr, download_queue))
    asyncio.create_task(copy(pw, reader, upload_queue))
