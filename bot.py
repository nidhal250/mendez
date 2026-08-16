import asyncio
import re
import os
os.system("pip install pynacl")
import sys
import discord
from datetime import timedelta
from discord.ext import commands
from flask import Flask
from threading import Thread
import json
from typing import Optional

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is alive and running!'

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
# ==========================
# WRITE COMMAND
# ==========================
abot.command()
@commands.is_owner()
async def write(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(message)
