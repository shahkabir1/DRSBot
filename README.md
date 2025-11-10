🏎️ DRSBot

DRSBot is a Formula 1 Discord bot that delivers real-time race updates, schedules, standings, and event info — all at your fingertips. Built using Python and Discord.py, DRSBot integrates with the Jolpica F1 API to keep you and your community up to speed on every race weekend.

🚀 Features

Live F1 Updates – Get instant race results, standings, and schedule info.

Weekend Schedule Command – View all sessions (FP1–FP3, Quali, Sprint, Race) for any Grand Prix.

Driver & Constructor Standings – Access current or past season rankings.

Previous Season Lookup – Retrieve stats and standings from any F1 season.

Podium Indicators – Medal emojis for the top 3 finishers.

Winner Highlights – Trophy emoji beside race winners.

Custom Role-Based Access – Optional admin/mod commands for configuration.

🧩 Commands
Command	Description
!standings	Displays current driver standings.
!constructors	Displays constructor standings.
!schedule	Shows the upcoming race weekend schedule.
!schedule <year>	Shows schedule for a specific year.
!race <round>	Shows detailed info for a specific race.
!help	Lists all available commands.
🛠️ Tech Stack

Language: Python 3.10+

Framework: discord.py

API: Jolpica F1 API

Hosting: Railway / Replit / Local

Other Tools: aiohttp, dotenv

⚙️ Setup & Installation

Clone the repository

git clone https://github.com/yourusername/drsbot.git
cd drsbot


Create a virtual environment

python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows


Install dependencies

pip install -r requirements.txt


Set up your environment variables
Create a .env file in the root directory:

DISCORD_TOKEN=your_discord_bot_token
JOLPICA_API=https://api.jolpi.ca/f1/


Run the bot

python bot.py
