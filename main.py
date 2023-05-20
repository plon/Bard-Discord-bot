import os
from Bard import Chatbot
import discord
from discord.ext import commands
import dotenv

# Set up the Discord bot
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, heartbeat_timeout=60)
BARD_TOKEN = os.getenv('BARD_TOKEN')
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
bard = Chatbot(BARD_TOKEN)
reply_all = os.environ["REPLY_ALL"]

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
    max_length = 1900
    response = bard.ask(prompt)
    if not response or "Google Bard encountered an error" in response["content"]:
        response = "I couldn't generate a response. Please try again."
        return response
    words = response["content"].split()
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

@bot.event
async def on_message(message):
    reply_all = os.environ.get('REPLY_ALL', '').lower() == 'true'
    if reply_all:
        if message.author.bot:
            return
        if message.reference and message.reference.resolved.author != bot.user:
            return  # Ignore replies to messages not from the bot
        is_dm_channel = isinstance(message.channel, discord.DMChannel)
    
        if message.channel.id in active_channels or (allow_dm and is_dm_channel):
            user_prompt = message.content
            async with message.channel.typing():
                response = await generate_response(user_prompt)
            for chunk in response:
                await message.reply(chunk)

@bot.hybrid_command(name="toggledm", description="Toggle DM for chatting.")
async def toggledm(ctx):
    global allow_dm
    allow_dm = not allow_dm
    await ctx.send(f"DMs are now {'allowed' if allow_dm else 'disallowed'} for active channels.")
    
@bot.hybrid_command(name="togglechannel", description="Toggle active channels.")
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
        
@bot.hybrid_command(name="reset", description="Reset the bot's context.")
async def reset(ctx):
    bard.conversation_id = ""
    bard.response_id = ""
    bard.choice_id = ""
    await ctx.send("Bot context has been reset.")

# Read the active channels from channels.txt on startup
if os.path.exists("channels.txt"):
    with open("channels.txt", "r") as f:
        for line in f:
            channel_id = int(line.strip())
            active_channels.add(channel_id)

@bot.hybrid_command(name="public", description="Toggle if bot should only respond to /chat or all messages in chat.")
async def public(ctx):
    global reply_all
    if os.environ.get('REPLY_ALL', '').lower() == 'false':
        reply_all = True 
        dotenv.set_key(dotenv_file, "REPLY_ALL", str(reply_all))
        os.environ['REPLY_ALL'] = str(reply_all)
        print(os.environ['REPLY_ALL'])
        await ctx.send(f"Bot will now respond to all messages in chat.")
    else:
        await ctx.send(f"Bot is already in public mode.")

@bot.hybrid_command(name="private", description="Toggle if bot should only respond to /chat or all messages in chat.")
async def private(ctx):
    global reply_all
    if os.environ.get('REPLY_ALL', '').lower() == 'true':
        reply_all = False 
        dotenv.set_key(dotenv_file, "REPLY_ALL", str(reply_all))
        os.environ['REPLY_ALL'] = str(reply_all)
        print(os.environ['REPLY_ALL'])
        await ctx.send(f"Bot will now only respond to /chat.")
    else:
        await ctx.send(f"Bot is already in private mode.")

@bot.tree.command(name="chat", description="Have a chat with Bard")
async def chat(interaction: discord.Interaction, message: str):
    await interaction.response.defer()
    is_dm_channel = isinstance(interaction.channel, discord.DMChannel)
    if interaction.user == bot.user:
        return
    if interaction.channel.id in active_channels or (allow_dm & is_dm_channel):
        allowed_mentions = discord.AllowedMentions(users=False)
        interaction_response = (f'> **{message}** - {interaction.user.mention} \n\n')      
        response = await generate_response(message)
        await interaction.followup.send(interaction_response, allowed_mentions=allowed_mentions)
        for chunk in response:
            try:
                await interaction.channel.send(chunk)
            except discord.errors.HTTPException:
                await interaction.channel.send("I couldn't generate a response. Please try again.")

bot.remove_command("help")   
@bot.hybrid_command(name="help", description="Get all other commands!")
async def help(ctx):
    embed = discord.Embed(title="Bot Commands", color=0x00ff00)
    embed.add_field(name="/chat", value="Have a chat with Bard.", inline=False)
    embed.add_field(name="/reset", value="Reset bot's context.", inline=False)
    embed.add_field(name="/togglechannel", value="Add the channel you are currently in to the Active Channel List.", inline=False)   
    embed.add_field(name="/toggledm", value="Toggle if DM chatting should be active", inline=False)
    embed.add_field(name="/public", value ="Toggle if bot should respond to all messages in chat", inline=False)
    embed.add_field(name="/private", value ="Toggle if bot should only respond to /chat", inline=False)
    
    await ctx.send(embed=embed)

bot.run(TOKEN)