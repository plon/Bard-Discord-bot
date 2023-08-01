from bardapi import BardAsync
import configparser 
import discord 
from discord.ext import commands

config = configparser.ConfigParser()
config.read('config.ini')
BARD_TOKEN = config["TOKENS"]['bard_token']
bard = BardAsync(token=BARD_TOKEN)
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, heartbeat_timeout=60)

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/help"))
    print(f"{bot.user.name} has connected to Discord!")
    invite_link = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(administrator=True),
        scopes=("bot", "applications.commands")
    )
    print(f"Invite link: {invite_link}")

@bot.tree.command(name="reset", description="Reset chat context")
async def reset(interaction: discord.Interaction):
    await interaction.response.defer()
    global bard
    bard = BardAsync(token=BARD_TOKEN)
    await interaction.followup.send("Chat context successfully reset.")
    return
    
@bot.tree.command(name="chat", description="Chat with Bard")
async def chat(interaction: discord.Interaction, prompt: str, image: discord.Attachment = None):
    await interaction.response.defer()
    if image is not None:
        if not image.content_type.startswith('image/'):
            await interaction.response.send_message("File must be an image")
            return
        response = await bard.ask_about_image(prompt, await image.read())
        if len(response['content']) > 2000:
            embed = discord.Embed(title="Response", description=response['content'], color=0xf1c40f)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(response['content'])
            return
    response = await generate_response(prompt) 
    if len(response['content']) > 2000:
        embed = discord.Embed(title="Response", description=response['content'], color=0xf1c40f)
        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send(response['content'])
    return

async def generate_response(prompt):
    max_length = 1950
    response = await bard.get_answer(prompt)
    # if "unable to get response" not in response["content"]
    if not "Unable to get response." in response["content"]:
        config = read_config()
        if config.getboolean("SETTINGS", "use_images"):
            images = response["images"]
            if images:
                for image in images:
                    response["content"] += f"\n{image}"
        # check image perms
        # check tts terms
        return response
    
@bot.tree.command(name="public", description = "Bot will respond to all messages")
async def public(interaction: discord.Interaction):
    config = read_config()
    if config.getboolean("SETTINGS", "reply_all"):
        await interaction.response.send_message("Bot is already in public mode")
    else:
        config["SETTINGS"]["reply_all"] = "True"
        await interaction.response.send_message("Bot will now respond to all messages")
    write_config(config)
    return

@bot.tree.command(name="private", description = "Bot will only respond to /chat")
async def private(interaction: discord.Interaction):
    config = read_config()
    if not config.getboolean("SETTINGS", "reply_all"):
        config["SETTINGS"]["reply_all"] = "false"
        await interaction.response.send_message("Bot will now only respond to /chat")
    else:
        await interaction.response.send_message("Bot is already in private mode")
    write_config(config)
    return

@bot.event
async def on_message(message):
    config = read_config()
    if config.getboolean("SETTINGS", "reply_all"):
        if message.author == bot.user:
            return
        async with message.channel.typing():
            response = await generate_response(message.content)
            if len(response['content']) > 2000:
                embed = discord.Embed(title="Response", description=response['content'], color=0xf1c40f)
                await message.channel.send(embed=embed)
            else:
                await message.channel.send(response['content'])

@bot.tree.command(name="images", description="Toggle if bot should respond with images")
async def images(interaction: discord.Interaction):
    config = read_config()
    if config.getboolean("SETTINGS", "use_images"):
        config["SETTINGS"]["use_images"] = "false"
        await interaction.response.send_message("Bot will no longer respond with images")
    else:
        config["SETTINGS"]["use_images"] = "true"
        await interaction.response.send_message("Bot will now respond with images")
    write_config(config)
    return

@bot.tree.command(name="help", description="Get all commands")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Commands", description="All commands for the bot", color=0xf1c40f)
    embed.add_field(name="/chat", value="Chat with Bard", inline=False)
    embed.add_field(name="/reset", value="Reset chat context", inline=False)
    embed.add_field(name="/public", value="Set bot to respond to all messages", inline=False)
    embed.add_field(name="/private", value="Set bot to only respond to /chat", inline=False)
    embed.add_field(name="/images", value="Toggle if bot should respond with images", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)
    
def read_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config

def write_config(config):
    with open("config.ini", "w") as configfile:
        config.write(configfile)

bot.run(config["TOKENS"]['discord_bot_token'])