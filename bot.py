import os
import discord
import aiohttp
import difflib
import json
import pytz
from datetime import datetime, timedelta
from dateutil import tz
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from dotenv import load_dotenv
from stayin_alive import keep_alive

TZ_ABBREVIATIONS = {
    # UTC / GMT
    "UTC": "UTC",
    "GMT": "Europe/London",

    # North America
    "EST": "America/New_York",
    "EDT": "America/New_York",
    "CST": "America/Chicago",
    "CDT": "America/Chicago",
    "MST": "America/Denver",
    "MDT": "America/Denver",
    "PST": "America/Los_Angeles",
    "PDT": "America/Los_Angeles",
    "MST-AZ": "America/Phoenix",
    "VST": "America/Vancouver",
    "MT": "America/Edmonton",
    "MEX": "America/Mexico_City",

    # South America
    "ART": "America/Buenos_Aires",
    "BRT": "America/Sao_Paulo",
    "PET": "America/Lima",
    "COT": "America/Bogota",

    # Europe
    "BST": "Europe/London",
    "CET": "Europe/Paris",
    "CEST": "Europe/Paris",
    "MEZ": "Europe/Berlin",
    "MESZ": "Europe/Berlin",
    "WEST": "Europe/Madrid",
    "EET": "Europe/Athens",
    "EEST": "Europe/Athens",
    "AMT": "Europe/Amsterdam",
    "CHT": "Europe/Zurich",
    "CET-OSLO": "Europe/Oslo",
    "CET-STO": "Europe/Stockholm",
    "EET-FIN": "Europe/Helsinki",
    "TRT": "Europe/Istanbul",

    # Asia
    "JST": "Asia/Tokyo",
    "KST": "Asia/Seoul",
    "CST-CHINA": "Asia/Shanghai",
    "SGT": "Asia/Singapore",
    "PHT": "Asia/Manila",
    "GST": "Asia/Dubai",
    "ICT": "Asia/Bangkok",
    "WIB": "Asia/Jakarta",
    "MYT": "Asia/Kuala_Lumpur",
    "CST-TW": "Asia/Taipei",

    # Oceania
    "AEST": "Australia/Sydney",
    "AEDT": "Australia/Sydney",
    "AEST-MEL": "Australia/Melbourne",
    "AEST-BRI": "Australia/Brisbane",
    "NZST": "Pacific/Auckland",
    "NZDT": "Pacific/Auckland",
    "FJT": "Pacific/Fiji",
    "CHST": "Pacific/Guam",

    # Africa
    "EET-EGY": "Africa/Cairo",
    "SAST": "Africa/Johannesburg",
    "EAT": "Africa/Nairobi",
    "WAT": "Africa/Lagos",

    # Middle East
    "AST": "Asia/Riyadh",
    "IRST": "Asia/Tehran",
    "AST-IRQ": "Asia/Baghdad",

    # Special zones (Etc)
    "GMT+0": "Etc/GMT+0",
    "GMT+1": "Etc/GMT+1",
    "GMT-1": "Etc/GMT-1",
    "GMT-8": "Etc/GMT-8"
}

TIMEZONES = [
    # North America
    "America/Toronto", "America/New_York", "America/Chicago", "America/Denver",
    "America/Los_Angeles", "America/Phoenix", "America/Vancouver", "America/Edmonton",
    "America/Mexico_City",

    # South America
    "America/Buenos_Aires", "America/Sao_Paulo", "America/Lima", "America/Bogota",

    # Europe
    "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Madrid",
    "Europe/Rome", "Europe/Athens", "Europe/Amsterdam", "Europe/Zurich",
    "Europe/Oslo", "Europe/Stockholm", "Europe/Helsinki", "Europe/Istanbul",

    # Asia
    "Asia/Tokyo", "Asia/Seoul", "Asia/Shanghai", "Asia/Singapore",
    "Asia/Manila", "Asia/Dubai", "Asia/Bangkok", "Asia/Jakarta",
    "Asia/Kuala_Lumpur", "Asia/Taipei",

    # Australia / Oceania
    "Australia/Sydney", "Australia/Melbourne", "Australia/Brisbane",
    "Pacific/Auckland", "Pacific/Fiji", "Pacific/Guam",

    # Africa
    "Africa/Cairo", "Africa/Johannesburg", "Africa/Nairobi", "Africa/Lagos",

    # Middle East
    "Asia/Riyadh", "Asia/Tehran", "Asia/Baghdad",

    # Special
    "UTC", "Etc/GMT+0", "Etc/GMT+1", "Etc/GMT-1", "Etc/GMT-8"
]

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.AutoShardedBot(command_prefix='!', intents=intents)

PREF_FILE = 'data/preferences.json'
CHANNEL_PREF_FILE = 'data/channel_preferences.json'

scheduler = AsyncIOScheduler()

current_year = datetime.now(pytz.UTC).year

def load_prefs():
    if not os.path.isfile(PREF_FILE):
        return {}
    with open(PREF_FILE, 'r') as f:
        return json.load(f)
    
def save_prefs(prefs):
    with open(PREF_FILE, 'w') as f:
        json.dump(prefs, f, indent=2)

def load_channel_prefs():
    if not os.path.isfile(CHANNEL_PREF_FILE):
        return {}
    with open(CHANNEL_PREF_FILE, 'r') as f:
        return json.load(f)
    
def save_channel_prefs(prefs):
    with open(CHANNEL_PREF_FILE, 'w') as f:
        json.dump(prefs, f, indent=2)

user_prefs = load_prefs()
channel_prefs = load_channel_prefs()

@bot.event
async def on_ready():
    global scheduler
    await bot.change_presence(activity=discord.Game(name="!menu | In the DRS Detection Zone 🏁"))
    print(f'{bot.user.name} is live and in the paddock!')

    if scheduler is None:
        scheduler.start()

    await schedule_next_race_reminders()

@bot.command()
async def menu(ctx):
    msg = (
        "**🏁 DRSBot Command Menu**\n"
        "`!menu` – Show this menu\n"
        "`!hello` – Say hello to me!\n"
        "`!favdriver <name>` – Set your favourite driver\n"
        "`!favteam <name>` – Set your favourite team\n"
        "`!whoami` – See your favourite driver\n"
        "`!standings` – Show Driver standings\n"
        "`!constructors` – Show Constructor standings\n"
        "`!prevquali` – Show previous Qualifying results\n"
        "`!prevgp` – Show previous Grand Prix results\n"
        "`!quali` – Show the Qualifying results for this weekend\n"
        "`!gp` – Show the Grand Prix results for this weekend\n"
        "`!weekend` – Show the schedule for the next weekend\n"
        "`!season` – Show the schedule for the current season\n"
        "`!settimezone` – Set your timezone\n"
        "`!mytimezone` – Show your timezone\n"
        "`!setreminderchannel` – (Admin) Set reminder channel\n"
        "\nMore commands coming soon!"
    )
    await ctx.send(msg)

@bot.command()
async def settimezone(ctx, *, user_input: str):
    user_input = user_input.strip().upper()

    if user_input in TZ_ABBREVIATIONS:
        matched = TZ_ABBREVIATIONS[user_input]
    else:
        matches = difflib.get_close_matches(user_input.lower(), [tz.lower() for tz in TIMEZONES], n=1, cutoff=0.5)
        if not matches:
            await ctx.send("❌ Unknown timezone. Try `PST`, `Toronto`, `London`, or `America/New_York`.")
            return
        matched = next(tz for tz in TIMEZONES if tz.lower() == matches[0])

    user_id = str(ctx.author.id)
    if not isinstance(user_prefs.get(user_id), dict):
        user_prefs[user_id] = {}

    user_prefs[user_id]['timezone'] = matched
    save_prefs(user_prefs)

    await ctx.send(f"✅ Your timezone has been set to `{matched}`.")

@bot.command()
async def mytimezone(ctx):
    user_id = str(ctx.author.id)
    tz_name = user_prefs.get(user_id, {}).get('timezone')

    if tz_name:
        await ctx.send(f"🕒 Your current timezone is set to: `{tz_name}`")
    else:
        await ctx.send("❗ You haven't set a timezone yet. Use `!settimezone <zone>` to set one. For example: `!settimezone toronto` or `!settimezone PST`.")

async def schedule_next_race_reminders():
    url = 'https://api.jolpi.ca/ergast/f1/current.json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print("Failed to fetch next race for reminders.")
                return

            data = await resp.json()
            races = data['MRData']['RaceTable']['Races']

            now = datetime.now(pytz.UTC)
            upcoming = None

            for race in races:
                race_time = datetime.fromisoformat(race['date'] + 'T' + race['time'].replace('Z', '+00:00'))
                if race_time > now:
                    upcoming = race
                    break

            if upcoming:
                race_time = datetime.fromisoformat(upcoming['date'] + 'T' + upcoming['time'].replace('Z', '+00:00'))
                reminder_time = race_time - timedelta(minutes=30)
                message = f"\U0001F3C1 Reminder: The {upcoming['raceName']} starts in 30 minutes! Get ready!"

                for guild_id, channel_id in channel_prefs.items():
                    scheduler.add_job(send_race_reminder, DateTrigger(reminder_time), args=[channel_id, message])

async def send_race_reminder(channel_id, message):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(message)        

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to the DRSBot Server!'
    )

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}, ready for lights out?')

@bot.command()
async def favdriver(ctx, *, driver):
    user_id = str(ctx.author.id)

    if not isinstance(user_prefs.get(user_id), dict):
        user_prefs[user_id] = {}

    user_prefs[user_id]['favdriver'] = driver.lower()
    save_prefs(user_prefs)

    await ctx.send(f"✅ Your favourite driver is now set to **{driver.title()}**!")

@bot.command()
async def favteam(ctx, *, team):
    user_id = str(ctx.author.id)

    if not isinstance(user_prefs.get(user_id), dict):
        user_prefs[user_id] = {}

    user_prefs[user_id]['favteam'] = team.lower()
    save_prefs(user_prefs)

    await ctx.send(f"✅ Your favourite constructor is set to **{team.title() if len(team) > 2 else team.upper()}**!")

@bot.command()
async def whoami(ctx):
    user_id = str(ctx.author.id)
    driver = user_prefs.get(user_id, {}).get('favdriver')

    if driver:
        driver_display = driver.title()
        await ctx.send(f"Hey {ctx.author.display_name}, your favourite driver is **{driver_display}**!")
    else:
        await ctx.send(f"You are {ctx.author.display_name}, but I don’t know your favourite driver yet. Use `!favdriver <name>` to tell me.")



@bot.command()
@commands.has_permissions(administrator=True)
async def setreminderchannel(ctx):
    channel_prefs[str(ctx.channel.guild.id)] = ctx.channel.id
    save_channel_prefs(channel_prefs)
    await ctx.send('Reminder set for this channel! \U0001F3C1')

@bot.command()
async def standings(ctx, year: str = None):
    if year is None:
        year = str(datetime.now(pytz.UTC).year)

    url = f'https://api.jolpi.ca/ergast/f1/{year}/driverStandings.json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await ctx.send('Failed to fetch standings. Please try again later.')
                return
            data = await resp.json()
            standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
            fav = user_prefs.get(str(ctx.author.id), {}).get('favdriver')

            msg = "**🏆 Driver Championship Standings:**\n"

            for driver in standings:
                d = driver['Driver']
                name = f"{d['givenName']} {d['familyName']}"
                team = driver['Constructors'][-1]['name']
                points = driver['points']
                position = driver['position']   
                highlight = " \U0001F525" if fav and fav in name.lower() else ""
                trophy = " 🏆" if position == "1" and year != str(datetime.now(pytz.UTC).year) else ""

                msg += f"{position}. **{name}** ({team}) – {points} pts{trophy}{highlight}\n"
            await ctx.send(msg)

@bot.command()
async def constructors(ctx, year: str = None):
    if year is None:
        year = str(datetime.utcnow().year)
    url = f'https://api.jolpi.ca/ergast/f1/{year}/constructorStandings.json'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await ctx.send("❌ Failed to fetch constructor standings.")
                return
            data = await resp.json()
            standings_data = data['MRData']['StandingsTable']['StandingsLists']
            if not standings_data:
                await ctx.send("No constructor standings found yet for this season.")
                return

    constructors = standings_data[0]['ConstructorStandings']
    msg = "**🛠️ Constructor Championship Standings:**\n"

    fav_team = user_prefs.get(str(ctx.author.id), {}).get('favteam')

    for team in constructors:
        name = team['Constructor']['name']
        points = team['points']
        position = team['position']
        highlight = " 🔥" if fav_team and fav_team in name.lower() else ""
        trophy = " 🏆" if position == "1" and year != str(datetime.now(pytz.UTC).year) else ""
        msg += f"{position}. **{name}** – {points} pts{trophy}{highlight}\n"

    await ctx.send(msg)
@bot.command()
async def weekend(ctx):
    user_id = str(ctx.author.id)
    user_tz_name = user_prefs.get(user_id, {}).get('timezone', 'UTC')
    try:
        user_tz = tz.gettz(user_tz_name)
    except:
        user_tz = tz.UTC

    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.jolpi.ca/ergast/f1/current/next.json') as resp:
            if resp.status != 200:
                await ctx.send("Failed to get the next race.")
                return
            data = await resp.json()
            next_race = data['MRData']['RaceTable']['Races'][0]
            round_number = next_race['round']

        async with session.get(f'https://api.jolpi.ca/ergast/f1/current/{round_number}.json') as resp:
            if resp.status != 200:
                await ctx.send("Couldn’t load weekend schedule.")
                return
            race_data = await resp.json()
            race = race_data['MRData']['RaceTable']['Races'][0]

    def format_time(date_str, time_str):
        return convert_utc_str_to_user_time(date_str, time_str, str(ctx.author.id))

    msg = f"**🚦 {race['raceName']} – {race['Circuit']['Location']['locality']}, {race['Circuit']['Location']['country']}**\n"

    if 'FirstPractice' in race:
        msg += f"• FP1: {format_time(race['FirstPractice']['date'], race['FirstPractice']['time'])}\n"
    if 'SecondPractice' in race:
        msg += f"• FP2: {format_time(race['SecondPractice']['date'], race['SecondPractice']['time'])}\n"
    if 'ThirdPractice' in race:
        msg += f"• FP3: {format_time(race['ThirdPractice']['date'], race['ThirdPractice']['time'])}\n"
    if 'Sprint' in race:
        msg += f"• Sprint: {format_time(race['Sprint']['date'], race['Sprint']['time'])}\n"
    if 'Qualifying' in race:
        msg += f"• Qualifying: {format_time(race['Qualifying']['date'], race['Qualifying']['time'])}\n"

    msg += f"• **Grand Prix**: {format_time(race['date'], race['time'])}"

    await ctx.send(msg)

@bot.command()
async def season(ctx):
    user_id = str(ctx.author.id)
    tz_name = user_prefs.get(user_id, {}).get('timezone', 'UTC')
    user_tz = tz.gettz(tz_name) or tz.UTC

    url = 'https://api.jolpi.ca/ergast/f1/current.json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await ctx.send("❌ Couldn't fetch the season schedule.")
                return
            data = await resp.json()

    races = data['MRData']['RaceTable']['Races']
    now = datetime.now(tz=tz.UTC)
    msg = "**📅 F1 Season Schedule:**\n"

    upcoming_flagged = False

    for race in races:
        name = race['raceName']
        location = race['Circuit']['Location']
        city = location['locality']
        country = location['country']

        utc_time = datetime.fromisoformat(f"{race['date']}T{race['time'].replace('Z', '+00:00')}")
        local_time = utc_time.astimezone(user_tz)
        date_str = local_time.strftime('%b %d – %H:%M %Z')

        is_upcoming = not upcoming_flagged and utc_time > now
        marker = "🟢 " if is_upcoming else "• "

        if is_upcoming:
            upcoming_flagged = True

        msg += f"{marker}**{name}** – {city}, {country} → `{date_str}`\n"

    await ctx.send(msg[:2000])
@bot.command()
async def prevgp(ctx, year: str = None):
    if year is None:
        year = str(datetime.utcnow().year)

    url = f'https://api.jolpi.ca/ergast/f1/{year}/last/results.json'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await ctx.send("❌ Failed to fetch Grand Prix results.")
                return
            data = await resp.json()

    races = data['MRData']['RaceTable']['Races']
    if not races:
        await ctx.send("No recent race results found.")
        return

    race = races[0]
    results = race['Results']
    race_name = race['raceName']
    circuit = race['Circuit']['circuitName']
    locality = race['Circuit']['Location']['locality']
    country = race['Circuit']['Location']['country']
    round_num = race['round']

    medals = {"1": "🥇", "2": "🥈", "3": "🥉"}

    race_time_str = convert_utc_str_to_user_time(race['date'], race['time'], str(ctx.author.id))
    msg = (
        f"**🏁 {race_name} Results ({circuit}, {locality}, {country}) – Race {round_num} of 24**\n"
        f"🕒 Held on: `{race_time_str}`\n"
    )

    for result in results:
        pos = result['position']
        d = result['Driver']
        name = f"{d['givenName']} {d['familyName']}"
        constructor = result['Constructor']['name']
        if 'Time' in result:
            finish_time = result['Time']['time']
        else:
            finish_time = result['status']
        medal = medals.get(pos, "")
        trophy = " 🏆" if pos == "1" and year != str(datetime.utcnow().year) else ""
        msg += f"{pos}. {medal} **{name}** ({constructor}){trophy} – `{finish_time}`\n"

    await ctx.send(msg)

@bot.command()
async def prevquali(ctx):
    url = 'https://api.jolpi.ca/ergast/f1/current/last/qualifying.json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await ctx.send("❌ Could not fetch qualifying results.")
                return
            data = await resp.json()

    race = data['MRData']['RaceTable']['Races'][0]
    quali_results = race['QualifyingResults'][:10]

    msg = f"**⏱️ {race['raceName']} Qualifying Results – Top 10**\n"

    for q in quali_results:
        driver = q['Driver']
        constructor = q['Constructor']['name']
        name = f"{driver['givenName']} {driver['familyName']}"
        position = q['position']
        best = q.get('Q3') or q.get('Q2') or q.get('Q1') or "N/A"
        msg += f"{position}. **{name}** ({constructor}) – `{best}`\n"

    await ctx.send(msg)

@bot.command()
async def quali(ctx):
    calendar_url = "https://api.jolpi.ca/ergast/f1/current.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(calendar_url) as cal_resp:
            if cal_resp.status != 200:
                await ctx.send("Couldn't fetch race calendar.")
                return

            calendar_data = await cal_resp.json()
            races = calendar_data['MRData']['RaceTable']['Races']

        for race in reversed(races):
            round_number = race['round']
            quali_url = f"https://api.jolpi.ca/ergast/f1/current/{round_number}/qualifying.json"

            async with aiohttp.ClientSession() as session:
                async with session.get(quali_url) as quali_resp:
                    if quali_resp.status != 200:
                        continue

                    quali_data = await quali_resp.json()
                    quali_races = quali_data['MRData']['RaceTable']['Races']
                    if not quali_races:
                        continue

                    quali = quali_races[0]
                    quali_results = quali['QualifyingResults'][:10]

                    msg = f"**⏱️ {race['raceName']} Qualifying Results – Top 10**\n"
                    for q in quali_results:
                        driver = q['Driver']
                        constructor = q['Constructor']['name']
                        name = f"{driver['givenName']} {driver['familyName']}"
                        position = q['position']
                        best = q.get('Q3') or q.get('Q2') or q.get('Q1') or "N/A"
                        msg += f"{position}. **{name}** ({constructor}) – `{best}`\n"

                    await ctx.send(msg)
                    return

        await ctx.send("No completed qualifying sessions found yet.")

@bot.command()
async def gp(ctx, year: str = None):
    if year is None:
        year = str(datetime.utcnow().year)
    calendar_url = "https://api.jolpi.ca/ergast/f1/current.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(calendar_url) as cal_resp:
            if cal_resp.status != 200:
                await ctx.send("Couldn't fetch race calendar.")
                return

            calendar_data = await cal_resp.json()
            races = calendar_data['MRData']['RaceTable']['Races']

        for race in reversed(races):
            round_number = race['round']
            results_url = f"https://api.jolpi.ca/ergast/f1/current/{round_number}/results.json"

            async with aiohttp.ClientSession() as session:
                async with session.get(results_url) as result_resp:
                    if result_resp.status != 200:
                        continue

                    result_data = await result_resp.json()
                    result_races = result_data['MRData']['RaceTable']['Races']
                    if not result_races:
                        continue

                    race = races[0]
                    results = race['Results']
                    race_name = race['raceName']
                    race_date = race['date']
                    circuit = race['Circuit']['circuitName']
                    locality = race['Circuit']['Location']['locality']
                    country = race['Circuit']['Location']['country']
                    round_num = race['round']

                    medals = {"1": "🥇", "2": "🥈", "3": "🥉"}

                    race_time_str = convert_utc_str_to_user_time(race['date'], race['time'], str(ctx.author.id))
                    msg = (
                        f"**🏁 {race_name} Results ({circuit}, {locality}, {country}) – Race {round_num} of 24**\n"
                        f"🕒 Held on: `{race_time_str}`\n"
    )

                    msg = f"**Grand Prix Results – {race_name} ({race_date})**\n"
                    for result in results[:10]:
                        pos = result['position']
                        d = result['Driver']
                        name = f"{d['givenName']} {d['familyName']}"
                        constructor = result['Constructor']['name']
                        if 'Time' in result:
                            finish_time = result['Time']['time']
                        else:
                            finish_time = result['status']
                        medal = medals.get(pos, "")
                        trophy = " 🏆" if pos == "1" and year != str(datetime.utcnow().year) else ""
                        msg += f"{pos}. {medal} **{name}** ({constructor}){trophy} – `{finish_time}`\n"

                    await ctx.send(msg)
                    return

        await ctx.send("No completed race results available yet.")


def convert_utc_str_to_user_time(date_str: str, time_str: str, user_id: str) -> str:
    user_tz_name = user_prefs.get(str(user_id), {}).get('timezone', 'UTC')
    user_tz = tz.gettz(user_tz_name) or tz.UTC
    utc_time = datetime.fromisoformat(f"{date_str}T{time_str.replace('Z', '+00:00')}")
    local_time = utc_time.astimezone(user_tz)
    return local_time.strftime('%a %b %d – %H:%M %Z')

keep_alive()
bot.run(TOKEN)
