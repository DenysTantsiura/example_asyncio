# import asyncio

from aiofile import async_open
from aiopath import AsyncPath


async_log_file = 'asynclog.txt'


async def async_logging_to_file(message: str) -> None:
    """Asunc write log to file."""
    apath = AsyncPath(async_log_file)
    if await apath.exists() and await apath.is_file():  # rewrite to try
        mode_file_open: str = 'a+'

    elif not await apath.exists():
        mode_file_open: str = 'w+'

    else:
        print(f'Sorry, no log-file and can\'t create "{async_log_file}"')
        return None
    
    async with async_open(async_log_file, mode_file_open) as afp:
        await afp.write(f'{message}\n')
