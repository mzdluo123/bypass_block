import asyncio
from config import PORT,SOCKS_PORT
from print_bw import print_bw
from http_client import handle_http
from socks_client import handle_socks


async def main():
    http_server = await asyncio.start_server(handle_http, "0.0.0.0", PORT)
    socks_server = await asyncio.start_server(handle_socks, "0.0.0.0", SOCKS_PORT)
    print(f"starting http server on port {PORT}.....")
    print(f"starting socks server on port {SOCKS_PORT}.....")
    asyncio.create_task(print_bw())
    await asyncio.gather(http_server.serve_forever(),socks_server.serve_forever())


if __name__ == '__main__':
    asyncio.run(main())