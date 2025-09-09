#pip install discord
import discord
from discord.ext import commands

import os
from dotenv import load_dotenv
load_dotenv()

# 请将此处替换为你的 Discord Bot Token
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
THREAD_ID = int(os.getenv("DISCORD_THREAD_ID", "0"))

intents = discord.Intents.default()
intents.message_content = True

# 如果你需要使用代理，请在这里设置，如果不需要，则设置为 None
proxy_url = "http://127.0.0.1:7890"  # 例如 "http://localhost:7890"

bot = commands.Bot(command_prefix='!', intents=intents, proxy=proxy_url)

@bot.event
async def on_ready():
    print(f'Bot已登录为 {bot.user}')
    # 创建一个可以被 await 的假的 ctx.send
    async def dummy_send(*args, **kwargs):
        print(f"无法发送消息，因为找不到频道/线程。检查你的 THREAD_ID。")
        print(f"参数: {args}, {kwargs}")

    ctx = type('Ctx', (), {'send': dummy_send})()
    await send_text(ctx, text="Hello, this is a sample text from Python.", thread_id=THREAD_ID)
    await send_embed(ctx, title="SampleTitle", description="This is a sample embed description from Python.", thread_id=THREAD_ID)
    await send_image(ctx, thread_id=THREAD_ID)

# 发送文字消息
@bot.command()
async def send_text(ctx, *, text: str, thread_id: int = None):
    if thread_id:
        thread = bot.get_channel(thread_id)
        if thread:
            await thread.send(text)
        else:
            await ctx.send("找不到指定的线程。")
    else:
        await ctx.send(text)

# 发送富文本（嵌入消息）
@bot.command()
async def send_embed(ctx, title: str, description: str, thread_id: int = None):
    embed = discord.Embed(title=title, description=description, color=0x00ff00)
    if thread_id:
        thread = bot.get_channel(thread_id)
        if thread:
            await thread.send(embed=embed)
        else:
            await ctx.send("找不到指定的线程。")
    else:
        await ctx.send(embed=embed)

# 发送图片（本地图片）
path_img = 'SampleImage.jpg'

@bot.command()
async def send_image(ctx, thread_id: int = None):
    with open(path_img, 'rb') as f:
        picture = discord.File(f)
        if thread_id:
            thread = bot.get_channel(thread_id)
            if thread:
                await thread.send(file=picture)
            else:
                await ctx.send("找不到指定的线程。")
        else:
            await ctx.send(file=picture)

if __name__ == '__main__':
    bot.run(TOKEN)
