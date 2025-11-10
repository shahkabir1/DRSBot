# 🏎️ DRSBot

**DRSBot** is a Formula 1 Discord bot that delivers real-time race updates, schedules, standings, and event info — all at your fingertips.  
Built using **Python** and **Discord.py**, DRSBot integrates with the **Jolpica F1 API** to keep you and your community up to speed every race weekend.

---

## 🚀 Features

- **Live F1 Updates** — instant race results, standings, and schedule info  
- **Weekend Schedule Command** — view all sessions (FP1–FP3, Quali, Sprint, Race)  
- **Driver & Constructor Standings** — for current or past seasons  
- **Previous Season Lookup** — retrieve stats from any F1 season  
- **Podium Indicators** — 🥇 🥈 🥉 for top 3 finishers  
- **Winner Highlights** — 🏆 beside race winners  
- **Custom Role-Based Access** — optional admin/mod-only commands  

---

## 🧩 Commands

| Command | Description |
|----------|-------------|
| `!standings` | Displays current driver standings |
| `!constructors` | Displays constructor standings |
| `!schedule` | Shows the upcoming race weekend schedule |
| `!schedule <year>` | Shows the schedule for a specific year |
| `!race <round>` | Shows detailed info for a specific race |
| `!help` | Lists all available commands |

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+  
- **Framework:** [discord.py](https://discordpy.readthedocs.io/en/stable/)  
- **API:** [Jolpica F1 API](https://api.jolpi.ca/)  
- **Hosting:** Railway / Replit / Local  
- **Libraries:** aiohttp, dotenv  

---

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/drsbot.git
   cd drsbot
2. **Install dependencies**
  ```bash
  pip install -r requirements.txt
  ```
3. **Configure environment variables**
  ```bash
  DISCORD_TOKEN=your_discord_bot_token
  JOLPICA_API=https://api.jolpi.ca/f1/
  ```
4. **Run the bot**
  ```bash
  python bot.py
```
