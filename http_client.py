import asyncio
import random
from config import SERVER_LIST, BUFFER, PORT, PROXY_PORT
from print_bw import upload_queue, download_queue


async def handle_http(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    socket = writer.transport.get_extra_info("peername")
    header = await reader.readline()
    host = header.decode()[:-11]
    proxy = random.choice(SERVER_LIST)
    print(f"HTTP {socket[0]}:{socket[1]} --{proxy}--> {host}")
    pr, pw = await asyncio.open_connection(proxy, PROXY_PORT)
    pw.write(header)
    pw.write(b"X-T5-Auth: ZjQxNDIh\r\n")
    pw.write(b'Proxy-Connection: Keep-Alive\r\n\r\n')


    async def __upload():
        while not pw.is_closing():
            data = await reader.read(BUFFER)
            if len(data) == 0:
                return
            await upload_queue.put(len(data))
            pw.write(data)

    async def __download():
        while not writer.is_closing():
            data = await pr.read(BUFFER)
            if len(data) == 0:
                return
            await download_queue.put(len(data))
            writer.write(data)

    asyncio.create_task(__download())
    asyncio.create_task(__upload())
