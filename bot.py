import discord
from flask import Flask
import os
from threading import Thread

# ====== Flask App (للبقاء على قيد الحياة في Render) ======
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
# تفعيل الصلاحيات الأساسية
intents = discord.Intents.default()
intents.message_content = True

# تعريف البوت
bot = discord.Client(intents=intents)

# ====== أحداث البوت ======

@bot.event
async def on_ready():
    """حدث عند تشغيل البوت"""
    print(f'✅ Bot is online as {bot.user}')
    print(f'✅ Bot ID: {bot.user.id}')
    print(f'✅ Connected to {len(bot.guilds)} servers')
    
    # تغيير حالة البوت (نشاط)
    await bot.change_presence(
        activity=discord.Game(name="Online 24/7"),
        status=discord.Status.online
    )

@bot.event
async def on_message(message):
    """حدث عند استقبال رسالة"""
    # منع البوت من الرد على نفسه
    if message.author == bot.user:
        return
    
    # يمكنك إضافة ردود تلقائية هنا إذا أردت
    # مثال: الرد على كلمة "سلام"
    if "سلام" in message.content.lower():
        await message.channel.send(f"وعليكم السلام {message.author.mention}")

@bot.event
async def on_member_join(member):
    """حدث عند دخول عضو جديد"""
    # إرسال ترحيب في قناة عامة
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"👋 Welcome {member.mention} to the server!")

@bot.event
async def on_member_remove(member):
    """حدث عند مغادرة عضو"""
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"👋 {member.name} has left the server.")

@bot.event
async def on_error(event, *args, **kwargs):
    """معالجة الأخطاء"""
    print(f'❌ Error: {event}')
    import traceback
    traceback.print_exc()

# ====== تشغيل البوت ======
if __name__ == "__main__":
    # تشغيل Flask في Thread منفصل
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    print('✅ Flask server started on port 8080')
    
    # تشغيل البوت
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if not TOKEN:
        print('❌ ERROR: DISCORD_TOKEN not set in environment variables')
        print('Please add DISCORD_TOKEN in Render Environment Variables')
        exit(1)
    
    try:
        print('🚀 Starting Discord bot...')
        bot.run(TOKEN)
    except discord.LoginFailure:
        print('❌ ERROR: Invalid Discord token')
        pint('Please check your token and try again')
    except Exception as e:
        print(f'❌ ERROR: {e}')
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
