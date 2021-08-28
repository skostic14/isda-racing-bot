import discord
import threading, queue
import asyncio
from discord.ext import tasks
from BotCredentials import BOT_TOKEN, RACE_CONTROL_STAFF_CHANNEL_ID, RACE_CONTROL_PUBLIC_CHANNEL_ID


class ISDABot(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_task.start()
        self.incident_queue = queue.Queue()

    def run_bot(self):
        threading.Thread(target=self.run, args=(BOT_TOKEN,), daemon=True).start()

    async def on_ready(self):
        await self.change_presence(activity=discord.Game("ISDA Dashboard"))
    
    async def post_incident_to_staff_channel(self, incident):
        involved_cars = ''
        for car in incident['involved_cars']:
            involved_cars += '\n\t* {}'.format(car)
        message = ("--- INCIDENT REPORT RECEIVED ---\n"
                   "Incident reported by: {}\n"
                   "Race: {}\n"
                   "Car(s) involved: {}\n"
                   "Lap and Turn: {}\n"
                   "Description: {}\n".format(incident['reported_by'],
                                              incident['race'],
                                              involved_cars,
                                              incident['incident_location'],
                                              incident['description']))
        staff_channel = self.get_channel(RACE_CONTROL_STAFF_CHANNEL_ID)
        await staff_channel.send(message)
    
    async def post_incident_to_public_channel(self, incident):
        involved_cars = ''
        for car in incident['involved_cars']:
            involved_cars += '\n\t* {}'.format(car)
        message = ("--- INCIDENT REPORT RECEIVED ---\n"
                   "Race: {}\n"
                   "Car(s) involved: {}\n"
                   "Lap and Turn: {}\n".format(incident['race'],
                                               involved_cars,
                                               incident['incident_location']))
        public_channel = self.get_channel(RACE_CONTROL_PUBLIC_CHANNEL_ID)
        await public_channel.send(message)

    @tasks.loop(seconds=10)
    async def background_task(self):
        await self.wait_until_ready()
        try:
            incident = self.incident_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            await self.post_incident_to_staff_channel(incident)
            await self.post_incident_to_public_channel(incident)
            self.incident_queue.task_done()      
