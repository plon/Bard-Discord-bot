import os
import bardapi
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Set up the Discord bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, heartbeat_timeout=60)
os.environ['_BARD_API_KEY'] = "xxxxx"
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

allow_dm = True
active_channels = set()

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(activity=discord.Game(name="/help"))
    print(f"{bot.user.name} has connected to Discord!")
    invite_link = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(administrator=True),
        scopes=("bot", "applications.commands")
    )
    print(f"Invite link: {invite_link}")

message_id = ""
async def generate_response(prompt):
    response = bardapi.core.Bard().get_answer(prompt)
    if not response:
        response = "I couldn't generate a response. Please try again."
    return (f"{response['content']}")

def split_response(response, max_length=1900):
    words = response.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(" ".join(current_chunk)) + len(word) + 1 > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
        else:
            current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
    
message_history = {}
MAX_HISTORY = 8

@bot.event
async def on_message(message):
    if message.author.bot:
      return
    if message.reference and message.reference.resolved.author != bot.user:
      return  # Ignore replies to messages not from the bot
    author_id = str(message.author.id)
    if author_id not in message_history:
        message_history[author_id] = []

    message_history[author_id].append(message.content)
    message_history[author_id] = message_history[author_id][-MAX_HISTORY:]
    
    is_dm_channel = isinstance(message.channel, discord.DMChannel)
    if message.channel.id in active_channels or (allow_dm and is_dm_channel):
        user_prompt = "\n".join(message_history[author_id])
        prompt = f"{user_prompt}\n{message.author.name}: {message.content}\n{bot.user.name}:"
        async with message.channel.typing():
            response = await generate_response(prompt)     
        chunks = split_response(response)  
        for chunk in chunks:
            await message.reply(chunk)

@bot.hybrid_command(name="toggledm", description="Toggle DM for chatting.")
async def toggledm(ctx):
    global allow_dm
    allow_dm = not allow_dm
    await ctx.send(f"DMs are now {'allowed' if allow_dm else 'disallowed'} for active channels.")
    
@bot.hybrid_command(name="toggleactive", description="Toggle active channels.")
async def toggleactive(ctx):
    channel_id = ctx.channel.id
    if channel_id in active_channels:
        active_channels.remove(channel_id)
        with open("channels.txt", "w") as f:
            for id in active_channels:
                f.write(str(id) + "\n")
        await ctx.send(
            f"{ctx.channel.mention} has been removed from the list of active channels."
        )
    else:
        active_channels.add(channel_id)
        with open("channels.txt", "a") as f:
            f.write(str(channel_id) + "\n")
        await ctx.send(
            f"{ctx.channel.mention} has been added to the list of active channels!")

# Read the active channels from channels.txt on startup
if os.path.exists("channels.txt"):
    with open("channels.txt", "r") as f:
        for line in f:
            channel_id = int(line.strip())
            active_channels.add(channel_id)

bot.remove_command("help")   
@bot.hybrid_command(name="help", description="Get all other commands!")
async def help(ctx):
    embed = discord.Embed(title="Bot Commands", color=0x00ff00)
    embed.add_field(name="/clear", value="Clear bot's context.", inline=False)
    embed.add_field(name="/toggleactive", value="Add the channel you are currently in to the Active Channel List.", inline=False)   
    embed.add_field(name="/toggledm", value="Toggle if DM chatting should be active or not.", inline=False)
    
    await ctx.send(embed=embed)

bot.run(TOKEN)