import asyncio
import ipaddress
import random
import struct
import socket

from config import SERVER_LIST, PROXY_PORT, BUFFER
from print_bw import upload_queue, download_queue
from utils import copy


async def handle_socks(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # 获取握手包
    connection = writer.transport.get_extra_info("peername")
    '''
    +----+----------+----------+
    |VER | NMETHODS | METHODS  |
    +----+----------+----------+
    | 1  |    1     | 1 to 255 |
    +----+----------+----------+
    '''
    p = struct.unpack("!bb", await reader.readexactly(2))
    _methods = struct.unpack("!p", await reader.readexactly(p[1]))
    if p[0] != 5:
        reader.feed_eof()
        writer.close()
        return
    '''
    +----+--------+
    |VER | METHOD |
    +----+--------+
    | 1  |   1    |
    +----+--------+
    '''
    writer.write(b'\x05\x00')
    '''
    +----+-----+-------+------+----------+----------+
    |VER | CMD |  RSV  | ATYP | DST.ADDR | DST.PORT |
    +----+-----+-------+------+----------+----------+
    | 1  |  1  | X'00' |  1   | Variable |    2     |
    +----+-----+-------+------+----------+----------+
    '''
    p = struct.unpack("!bbxb", await reader.readexactly(4))
    atype = p[2]
    if p[1] == 3 or p[2] == 0x04:
        writer.write(b"\x05\x01\x00")
        writer.close()
        reader.feed_eof()
        return
    # 域名处理
    if atype == 3:
        size = await reader.readexactly(1)
        address = await reader.readexactly(int.from_bytes(size, 'little'))
        port = int.from_bytes(await reader.readexactly(2), 'big', signed=False)
        address = await asyncio.get_running_loop().getaddrinfo(address.decode(), port,family=socket.AF_INET)
        address = address[0][4][0]
    if atype == 1:
        address = ipaddress.IPv4Address(await reader.readexactly(4))
        port = int.from_bytes(await reader.readexactly(2), 'big', signed=False)
    proxy = random.choice(SERVER_LIST)
    pr, pw = await asyncio.open_connection(proxy, PROXY_PORT)
    print(f"SOCKS {connection[0]}:{connection[1]} --{proxy}--> {address}:{port}")
    pw.write(f'CONNECT {address}:{port} HTTP/1.1\r\n'.encode())
    pw.write(b"X-T5-Auth: ZjQxNDIh\r\n")
    pw.write(b'Proxy-Connection: Keep-Alive\r\n\r\n')
    '''+----+-----+-------+------+----------+----------+
|VER | REP |  RSV  | ATYP | BND.ADDR | BND.PORT |
+----+-----+-------+------+----------+----------+
| 1  |  1  | X'00' |  1   | Variable |    2     |
+----+-----+-------+------+----------+----------+
    '''
    pack = struct.pack("!bbxb", 5, 0, atype)
    writer.write(pack)

    if atype == 3:
        writer.write(int.to_bytes(len(address), 1, 'little'))
        writer.write(address.encode())
    else:
        writer.write(int.to_bytes(int(address), 4, 'little'))
    writer.write(int.to_bytes(port, 2, 'big', signed=False))
    await pr.readline()
    await pr.readline()
    asyncio.create_task(copy(writer, pr, download_queue))
    asyncio.create_task(copy(pw, reader, upload_queue))
