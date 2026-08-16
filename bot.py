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
# ==========================
# 🎵 أوامر الصوت المتكاملة
# ==========================

# متغيرات لتتبع حالة البوت الصوتي
last_voice_channel = {}  # {guild_id: channel_id}
manual_leave = set()  # {guild_id} للغادرين يدوياً

@bot.command()
@commands.is_owner()
async def join(ctx):
    """يدخل البوت للروم الصوتي اللي انت فيه"""
    
    if not ctx.author.voice:
        return await ctx.send("❌ You must be in a voice channel first!")
    
    channel = ctx.author.voice.channel
    
    permissions = channel.permissions_for(ctx.guild.me)
    if not permissions.connect:
        return await ctx.send("❌ I don't have permission to join that voice channel!")
    if not permissions.speak:
        return await ctx.send("❌ I don't have permission to speak in that voice channel!")
    
    try:
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
            await ctx.send(f"✅ Moved to **{channel.name}**")
        else:
            await channel.connect()
            await ctx.send(f"✅ Joined **{channel.name}**")
        
        last_voice_channel[ctx.guild.id] = channel.id
        
        if ctx.guild.id in manual_leave:
            manual_leave.remove(ctx.guild.id)
            
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def leave(ctx):
    """يخرج البوت من الروم الصوتي"""
    
    if not ctx.voice_client:
        return await ctx.send("❌ I'm not in a voice channel!")
    
    manual_leave.add(ctx.guild.id)
    
    try:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left voice channel!")
        
        if ctx.guild.id in last_voice_channel:
            del last_voice_channel[ctx.guild.id]
            
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# ==========================
# إعادة الاتصال التلقائي
# ==========================

@bot.event
async def on_voice_state_update(member, before, after):
    """
    يراقب حالة البوت الصوتي:
    - إذا طلع بالغلط (Disconnect) يرجع تلقائياً
    - إذا تحرك لروم آخر يتابعه
    """
    
    # نتجاوز كل الأعضاء ما عدا البوت نفسه
    if member.id != bot.user.id:
        return
    
    guild = member.guild
    
    # ===== إذا دخل البوت لروم =====
    if after.channel:
        last_voice_channel[guild.id] = after.channel.id
        print(f"🔊 Bot moved to: {after.channel.name}")
        return
    
    # ===== إذا طلع البوت =====
    # نتحقق إذا كان طلع يدوياً (أمر !leave)
    if guild.id in manual_leave:
        manual_leave.remove(guild.id)
        print("👋 Bot left manually (via !leave)")
        return
    
    # ===== إذا طلع بالغلط (Disconnect) =====
    if before.channel and guild.id in last_voice_channel:
        await asyncio.sleep(3)  # نستنى 3 ثواني
        
        try:
            # نتحقق إذا البوت لسا خارج
            if guild.voice_client is None:
                # نجيب الروم المخزن
                channel = guild.get_channel(last_voice_channel[guild.id])
                
                if channel:
                    # نرجع البوت للروم
                    await channel.connect()
                    print(f"🔄 Bot reconnected to: {channel.name}")
                    
                    # نرسل رسالة في الـ logs
                    log_channel = discord.utils.get(guild.text_channels, name="logs")
                    if log_channel:
                        await log_channel.send("🔄 **Bot reconnected automatically!**")
                        
        except Exception as e:
            print(f"❌ Reconnect error: {e}")
