import discord
from flask import Flask
import os
from threading import Thread

# ====== Flask App ======
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Bot is alive and running!'

@app.route('/health')
def health():
    return 'OK', 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# ====== Discord Bot ======
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

# ====== أحداث البوت ======

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')
    print(f'✅ Bot ID: {bot.user.id}')
    print(f'✅ Connected to {len(bot.guilds)} servers')
    await bot.change_presence(
        activity=discord.Game(name="Online 24/7"),
        status=discord.Status.online
    )

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # رد تلقائي على كلمة "سلام"
    if "سلام" in message.content.lower():
        await message.channel.send(f"وعليكم السلام {message.author.mention}")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"👋 Welcome {member.mention} to the server!")

@bot.event
async def on_error(event, *args, **kwargs):
    print(f'❌ Error: {event}')

# ====== تشغيل البوت ======
if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    print('✅ Flask server started')
    
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if not TOKEN:
        print('❌ ERROR: DISCORD_TOKEN not set')
        exit(1)
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f'❌ ERROR: {e}')
# 8️⃣ أمر !dmall
@bot.command()
@commands.is_owner()
async def dmall(ctx, *, message: str):
    """يبعث رسالة خاصة لجميع الأعضاء (باستثناء البوتات)"""
    members = [m for m in ctx.guild.members if not m.bot]
    
    confirm_msg = await ctx.send(f"⚠️ **You are about to send a DM to {len(members)} member **\nmessage: \"{message}\"\n\nReply with **yes** To confirm or **no** Cancel (30 S)")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['yes', 'no']
    
    try:
        response = await bot.wait_for('message', timeout=30.0, check=check)
        
        if response.content.lower() == 'no':
            return await ctx.send("❌ Cancelled.")
        
        await ctx.send(f"⏳ Messages are being sent to {len(members)} member ...")
        
        success_count = 0
        fail_count = 0
        
        embed = discord.Embed(
            title="📢  Message from 𝙳𝚎𝚊𝚝𝚑 𝚆𝚑𝚒𝚜𝚙𝚎𝚛 𝙲𝚘𝚖𝚖𝚞𝚗𝚒𝚝𝚢",
            description=message,
            color=discord.Color.green()
        )
        embed.set_footer(text=f"from: {ctx.author.display_name} • {ctx.guild.name}")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        for member in members:
            try:
                await member.send(embed=embed)
                success_count += 1
                await asyncio.sleep(0.3)
            except:
                fail_count += 1
        
        await ctx.send(f"✅ **Sent successfully!**\n✅  succeeded: {success_count}\n❌fail: {fail_count}")
        
    except asyncio.TimeoutError:
        await ctx.send("⏰ime's up! Cancelled.")
# 6️⃣ أمر !dm
@bot.command()
@commands.is_owner()
async def dm(ctx, member: discord.Member, *, message: str):
    """يبعث رسالة خاصة لعضو واحد"""
    try:
        embed = discord.Embed(
            title="📩 Message from 𝙳𝚎𝚊𝚝𝚑 𝚆𝚑𝚒𝚜𝚙𝚎𝚛 𝙲𝚘𝚖𝚖𝚞𝚗𝚒𝚝𝚢",
            description=message,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"from: {ctx.author.display_name} • {ctx.guild.name}")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await member.send(embed=embed)
        await ctx.send(f"✅ The message was sent successfully! **{member.display_name}** ")
    except discord.Forbidden:
        await ctx.send(f"❌ I can't send a message to**{member.display_name}** (DM locked )")
    except Exception as e:
        await ctx.send(f"❌error : {str(e)}")
# ==========================
# HELLO COMMAND
# ==========================
@bot.command()
@commands.is_owner()
async def hello(ctx):
    await ctx.send(f'👋 Hello {ctx.author.mention}!')

# ==========================
# WRITE COMMAND
# ==========================
@bot.command()
@commands.is_owner()
async def write(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(message)

