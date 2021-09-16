import asyncio
from config import BUFFER
import logging

async def copy(writer: asyncio.StreamWriter, reader: asyncio.StreamReader, queue: asyncio.Queue):
    try:
        while not writer.is_closing():
            data = await reader.read(BUFFER)
            if len(data) == 0:
                writer.close()
                return
            await queue.put(len(data))
            writer.write(data)
    except Exception as e:
        logging.error(e)
        writer.close()
        reader.feed_eof()