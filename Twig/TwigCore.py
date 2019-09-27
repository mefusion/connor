import discord
from discord.ext import commands
from dotenv import load_dotenv, dotenv_values
from discord.ext.commands import BucketType
from contextlib import redirect_stdout
from Twig.Utils.AppLogging import *
import json
import time
import datetime
from Twig.Utils.Configurator import *
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

env_path = pathlib.Path('./Config/token.env')
load_dotenv(dotenv_path=env_path)
BOT_TOKEN = os.getenv("TOKEN")

ERROR_COLOR = 0xDD2E44
SUCCESS_COLOR = 0x77B255
SECONDARY_COLOR = 0x3B88C3
DEFAULT_COLOR = discord.Colour.default()
WARNING_COLOR = discord.Colour.gold()
BLURPLE_COLOR = discord.Colour.blurple()
BOT_STARTED_AT = int(time.time())
DEFAULT_PREFIX = "?"

print('[CORE] Core initialized!')
