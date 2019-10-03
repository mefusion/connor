import discord
from discord.ext import commands
from dotenv import load_dotenv, dotenv_values
from discord.ext.commands import BucketType
from contextlib import redirect_stdout
from Saber.Utils.AppLogging import *
import json
import time
import datetime
from Saber.Utils.Configurator import *
import pathlib
import datetime
import aiohttp
import asyncio
import discord
import logging
import time
import json
import io
import os
import git
import sys
import re
import textwrap
import traceback
import random
import subprocess
import psutil
import yaml
import requests
import urllib
import unicodedata
import lyricsgenius

repo = git.Repo(".git")
ARTISTS_BLACKLIST = ('face', 'фэйс', 'lida', 'rasa')

IS_TOKEN_REVEALED = False


def authorize(client):
    global IS_TOKEN_REVEALED

    if IS_TOKEN_REVEALED is False:
        IS_TOKEN_REVEALED = True
        load_dotenv(dotenv_path='./Config/token.env')
        client.run(os.getenv("TOKEN"), bot=True, reconnect=True)


ERROR_COLOR = 0xDD2E44
SUCCESS_COLOR = 0x77B255
SECONDARY_COLOR = 0x3B88C3
DEFAULT_COLOR = discord.Colour.default()
WARNING_COLOR = discord.Colour.gold()
BLURPLE_COLOR = discord.Colour.blurple()
BOT_STARTED_AT = int(time.time())
DEFAULT_PREFIX = "?"

print('[CORE] Core initialized!')
