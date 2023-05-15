# Setup 

## Prerequisites to install

* run pip3 install -r requirements.txt

* Rename the file `example.env` to `.env`

## Step 1: Create a Discord bot

1. Go to https://discord.com/developers/applications create an application
2. Build a Discord bot under the application
3. Get the token from bot setting

   ![image](https://user-images.githubusercontent.com/89479282/205949161-4b508c6d-19a7-49b6-b8ed-7525ddbef430.png)
4. Store the token to `.env` under the `DISCORD_BOT_TOKEN`

   <img height="190" width="390" alt="image" src="https://user-images.githubusercontent.com/89479282/222661803-a7537ca7-88ae-4e66-9bec-384f3e83e6bd.png">

5. Turn MESSAGE CONTENT INTENT `ON`

   ![image](https://user-images.githubusercontent.com/89479282/205949323-4354bd7d-9bb9-4f4b-a87e-deb9933a89b5.png)

6. Invite your bot to your server via OAuth2 URL Generator

   ![image](https://user-images.githubusercontent.com/89479282/205949600-0c7ddb40-7e82-47a0-b59a-b089f929d177.png)

## Authentication
1. Visit https://bard.google.com/
2. F12 for console
3. Session: Application → Cookies → Copy the value of  `__Secure-1PSID` cookie.

## Step 3: Run the bot on the desktop

1. Open a terminal or command prompt

2. Navigate to the directory where you installed the ChatGPT Discord bot

3. Run `python3 main.py` or `python main.py` to start the bot

## Step 4. Invite the bot
![image](https://user-images.githubusercontent.com/91066601/236673317-64a1789c-f6b1-48d7-ba1b-dbb18e7d802a.png)

## Modes

* **Direct message mode:** The bot can be used to chat with users in direct messages. To enable this mode, use the `/toggledm` command
* **Channel mode:** The bot can be used to chat with users in channels. To enable this mode for a channel, use the `/toggleactive` command

## Commands

* `/help`: Displays a list of all available commands
* `/toggledm`: Toggles direct message mode
* `/toggleactive`: Toggles channel mode for a channel

## License

This program is based on the work of [mishalhossin](https://github.com/mishalhossin), [Zero6992](https://github.com/zero6992), and [acheong08](https://github.com/acheong08)

For more information, please visit the following repositories:

* https://github.com/mishalhossin/Discord-Chatbot-Gpt4Free
* https://github.com/Zero6992/chatGPT-discord-bot
* https://github.com/acheong08/Bard