import asyncio

upload_queue = asyncio.Queue()
download_queue = asyncio.Queue()


async def print_bw():
    while True:
        upload = 0
        download = 0
        for i in range(download_queue.qsize()):
            download += download_queue.get_nowait()
        for i in range(upload_queue.qsize()):
            upload += upload_queue.get_nowait()
        download_queue.empty()
        upload_queue.empty()
        print(f"\rD: {download / 1024/1}KB U:{upload / 1024/1}KB",end="",flush=True)
        await asyncio.sleep(1)
