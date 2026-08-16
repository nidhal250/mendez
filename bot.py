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
        print('Please check your token and try again')
    except Exception as e:
        print(f'❌ ERROR: {e}')
