import asyncio
import ipaddress
import random

from config import SERVER_LIST, PROXY_PORT, BUFFER
from print_bw import upload_queue, download_queue
from utils import copy


async def handle_socks(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # 获取握手包
    socket = writer.transport.get_extra_info("peername")
    pack = await reader.readexactly(2)
    if pack[:1] == b'\x05':
        size = pack[1]
        # 丢掉头部信息
        await reader.readexactly(size)
        # 发送无需密码验证信息
        writer.write(b'\x05\x00')
    else:
        writer.close()
        reader.feed_eof()
        return

    pack = await reader.readexactly(4)
    # 除了connect之外的都不支持
    if pack[1:2] != b'\x01':
        writer.write(b'\x05\x01')
        writer.close()
        reader.feed_eof()
    atyp = pack[3:]
    # 不支持ipv6
    address = None
    if atyp == b'\x04':
        writer.write(b'\x05\x01')
        writer.close()
        reader.feed_eof()
    if atyp == b'\x01':
        address = ipaddress.IPv4Address(await reader.readexactly(4))
        if str(address) == "0.0.0.0":
            writer.close()
            reader.feed_eof()
            return
    if atyp == b'\x03':
        size = await reader.readexactly(1)
        address = await reader.readexactly(int.from_bytes(size, 'little'))
        address = address.decode()

    port = int.from_bytes(await reader.readexactly(2), 'big', signed=False)
    proxy = random.choice(SERVER_LIST)
    pr, pw = await asyncio.open_connection(proxy, PROXY_PORT)
    print(f"SOCKS {socket[0]}:{socket[1]} --{proxy}--> {address}:{port}")
    pw.write(f'CONNECT {address}:{port} HTTP/1.1\r\n'.encode())
    pw.write(b"X-T5-Auth: ZjQxNDIh\r\n")
    pw.write(b'Proxy-Connection: Keep-Alive\r\n\r\n')

    writer.write(b'\x05\x00\x00')
    writer.write(atyp)
    if atyp == b'\x03':
        encoded = address.encode()
        writer.write(int.to_bytes(len(encoded), 1, 'little'))
        writer.write(encoded)
    else:
        writer.write(int.to_bytes(int(address), 4, 'little'))
    writer.write(int.to_bytes(port, 2, 'big', signed=False))
    await pr.readline()
    await pr.readline()
    asyncio.create_task(copy(writer, pr, download_queue))
    asyncio.create_task(copy(pw, reader, upload_queue))
