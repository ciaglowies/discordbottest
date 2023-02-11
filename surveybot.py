import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Discord bot setup
client = discord.Client()

# Set up a list to store surveys
surveys = []

# Set up a dictionary to store users' opt-in status
opt_in = {}

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    # Check if the message is a command to create a survey
    if message.content.lower().startswith("!createsurvey"):
        # Check if the user is an administrator
        if not message.author.guild_permissions.administrator:
            await message.channel.send("Only administrators can create surveys.")
            return

        # Extract the survey questions from the command
        survey_questions = message.content[len("!createsurvey "):].strip()

        # Add the survey to the list of surveys
        surveys.append(survey_questions)
        await message.channel.send(f"Survey added: {survey_questions}")

    # Check if the message is a command to start a survey
    if message.content.lower().startswith("!startsurvey"):
        # Check if the user is an administrator
        if not message.author.guild_permissions.administrator:
            await message.channel.send("Only administrators can start surveys.")
            return

        # Check if there are any surveys to start
        if len(surveys) == 0:
            await message.channel.send("There are no surveys to start.")
            return

        # Get a list of users who have opted in to receive surveys
        opted_in_users = [k for k, v in opt_in.items() if v]

        # Send the survey to each opted-in user
        survey = surveys[0]
        for user_id in opted_in_users:
            user = client.get_user(user_id)
            await user.send(survey)

            # Wait for the response
            response_message = await client.wait_for('message', check=lambda m: m.author == user, timeout=60.0)

            # Extract the response
            response = response_message.content

            # Write the response to a Google Sheet
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
            client = gspread.authorize(creds)

            sheet = client.open("Survey Responses").sheet1
            sheet.append_row([response])

    # Check if the message is a command to opt in or out of surveys
    if message.content.lower().startswith("!opt"):
        # Extract the opt-in status from the command
        opt_in_status = message.content[len("!opt "):].strip().lower()

        # Update the user's opt-in status
        if opt_in_status == "in":
