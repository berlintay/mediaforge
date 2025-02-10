import asyncio
import contextvars
import dataclasses
import os
import random
import shutil
import string
import tempfile
import typing

import aiofiles.os

import config
from core.clogs import logger
from processing.mediatype import MediaType, mediatype


class TempFile(str):
    mt: MediaType = None
    lock_codec: bool = False

    async def mediatype(self):
        if self.mt is None:
            self.mt = await mediatype(self)
        return self.mt


def init():
    global temp_dir
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)


if config.override_temp_dir is not None:
    temp_dir = config.override_temp_dir
else:
    if os.path.isdir("/dev/shm"):  # in-memory fs
        temp_dir = "/dev/shm/mediaforge"
    else:
        temp_dir = os.path.join(tempfile.gettempdir(), "mediaforge")

logger.debug(f"temp dir is {temp_dir}")


def get_random_string(length):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


def is_named_used(name):
    return os.path.exists(name)


def temp_file_name(extension=None):
    while True:
        name = os.path.join(temp_dir, get_random_string(8))
        if extension:
            name += f".{extension}"
        if not is_named_used(name):
            return name


def reserve_tempfile(arg):
    if arg is None:  # default
        arg = temp_file_name()
    elif "." not in arg:  # just extension
        arg = temp_file_name(arg)
    # full filename otherwise

    tfs = session.get()
    tfs.append(arg)
    session.set(tfs)
    logger.debug(f"Reserved new tempfile {arg}")
    return TempFile(arg)


class TempFileSession:
    def __init__(self):
        pass

    async def __aenter__(self):
        try:
            session.get()
            raise Exception("Cannot create new TempFileSession, one already exists in this context.")
        except LookupError:
            pass
        logger.debug("Created new TempFileSession")
        session.set([])

    async def __aexit__(self, *_):
        files = session.get()
        logger.debug(f"TempFileSession exiting with {len(files)} files: {files}")
        fls = await asyncio.gather(*[aiofiles.os.remove(file) for file in files], return_exceptions=True)
        for f in fls:
            if isinstance(f, Exception):
                logger.warn(f)
        logger.debug(f"TempFileSession exited!")


session: contextvars.ContextVar[list[TempFile]] = contextvars.ContextVar("session")


def handle_tfs_parallel(func: typing.Callable, *args, **kwargs):
    try:
        session.set([])
        res = func(*args, **kwargs)
        return True, res, session.get()
    except Exception as e:
        return False, e, session.get()
