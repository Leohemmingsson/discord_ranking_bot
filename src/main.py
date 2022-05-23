import os
import memory

import discord
import datetime
import commands_func
# Had this for the intent
#from discord.ext import commands
from dotenv import load_dotenv

# This is just config stuff: Token, what server to write to, what channel to use for io
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD')
CHANNEL_RATING = "rating"


# Creating a obj for the memory and stuff
top_list = memory.Stats()

# This is for seeing all members on server, but it does not work
#intents = discord.Intents()
#intents.all()
#bot = commands.Bot(command_prefix='.',intents=intents)

# This is the handle to the discord api
client = discord.Client()

ranking_handle = commands_func.Ranking(channel_rating=CHANNEL_RATING, memory_handle=top_list)


# Prints the points of each person.
async def ranking(m): 
    longest_name = max(map(len, top_list.get_list()))
    response = ("-" * (longest_name + 12)) + "\n"

    for counter, person in enumerate(top_list.get_list()):
        response += f"| \#{str(counter+1)} {top_list.get_stat(person)}"

    response += ("-" * (longest_name + 12))
    await m.channel.send(response)

# This will store different commands and stuff
commands = {
    "-": top_list.subtract,
    "+": top_list.add,
    "!ranking": ranking,
    "!name": top_list.change_name,
    "history": top_list.history,
    "!cite": top_list.save_cite
} 


# If something happens on discord
@client.event
# If this something is a message
async def on_message(message):
    # Print author
    #print(message.author.id)

    """
    if message.author.id == "170604046388953089":
        print("YES")
    """

    # This is just so the bot does not answer itself and become a loop
    if message.author == client.user:
        return

    if str(message.guild) == GUILD:
        # Once methods are rewritten a bit the commands structure can be even more generic in such a way that:
        #
        # if message.content.split()[0] in commands:
        #     commands[message.content.split()[0]](message)
        #
        # The args can be made generic by letting the functions in commands use **kwargs and *args or wahtever

        # If !ranking is written, it will print all the points for each person. The other stuff is for formating

        # To see if its a reply of a previous message
        #print(message.reference)            

        if message.content.split()[0] == "!ranking":
            if str(message.channel) == CHANNEL_RATING:
                print("Running the ranking script")
                # Call the command (Which we know exists) with the correct args
                await commands[message.content.split()[0]](message)
            else:
                print("Command sent in wrong channel")
                # This might should tell the person where it is possible to say some commands?

        elif message.content.split()[0] == "!alias":
            print("alias")
        
        elif message.content.split()[0] == "!name":
            if commands[message.content.split()[0]](str(message.author.id), message.content.split()[1]):
                response = f"Your new name is {message.content.split()[1]}"
            else:
                response = f"{message.content.split()[1]} is not avalible"

            await message.channel.send(response)
        
        elif message.content.split()[0] == "!ping":
            # This does not work, because of timezones
            time_sent = int(message.created_at.strftime("%y%m%d%H%M%S%f")) // 100
            time_now = int(datetime.datetime.now().strftime("%y%m%d%H%M%S%f"))//100
            print(f"{(time_now-time_sent)} ")
            print(f"now {time_now} before {time_sent}")

        elif message.content.split()[0] == "!cite":
            # This will cite a sent message
            if message.reference == None:
                # This is just to print a random cited message
                cited_message = top_list.get_cite()
                response = f"\"{cited_message[1]}\" ~ {cited_message[0]}"
            else:
                #print(message.reference)
                search_limit = 100
                try:
                    if int(message.content.split()[1]) > search_limit:
                        search_limit = int(message.content.split()[1])
                except:
                    pass

                if search_limit > 1000000:
                    response = "To high search limit, max limit is 1000000"
                    await message.channel.send(response)
                    return -1

                async for old_message in message.channel.history(limit=search_limit):
                    response = ""
                    if old_message.id == message.reference.message_id:
                        return_value = top_list.save_cite(old_message.author.id, old_message.content, old_message.id)
                        if return_value == 1:
                            response = "Message was cited"
                            break
                        elif return_value == -1:
                            response = "There was some problem with citing that message"
                            break
                    
                print(response)
                if response == "":
                    response = "Message could not be found, try higher search limit ex) \"!cite 10000\""
        
        elif message.content[0] == "+":
            print("here")
            if await ranking_handle.add(message) == -1:
                print("Error  wohooo")


            #await message.channel.send(response)
            return 1


        # New giving or taking rating-points
    else:
        pass

        #print(f"Message sent in {message.guild}")

client.run(TOKEN)