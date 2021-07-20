import aiofiles
import discord
from discord.ext import tasks
import json
import os
import random
import sys
import arrow

class PotdBot(discord.Client):
    def __init__(self):
        super().__init__()

        self.bot_invocation_str = '!potdbot'
        self.image_paths = []
        self.already_posted = []
        self.cache_open_mode = 'a'

        self.api_key = None
        self.default_caption = None
        self.image_dir = None
        self.posted_image_cache_filename = None
        self.post_time = None # HH:mm:ss
        self.post_channel_name = None
        self.post_channel = None

        self.has_initialized = False
        
        self.init_config()
        self.init_posted_images_cache()
        self.scan_images()
        self.init_post_scheduler(seconds=self.calc_delta_seconds(self.post_time))

    def init_config(self):
        try:
            config = None
            with open('config.json', 'r') as fp:
                config = json.load(fp)
            self.api_key = config['api_key']
            self.default_caption = config['default_caption']
            self.image_dir = config['image_dir']
            self.posted_image_cache_filename = config['posted_images_cache']
            self.post_time = arrow.get(config['post_time'], 'HH:mm:ss')
            self.post_channel_name = config['post_channel']

        except Exception as ex:
            print("Critical error. Failed to read config.json. Exception:\n", ex)
            sys.exit(-1)

    def calc_delta_seconds(self, time):
        a = arrow.now()
        b = a.replace(hour=time.hour, minute=time.minute, second=time.second)
        # if time has already passed for today, schedule for tomorrow
        if a > b:
            b = b.shift(days=+1)
        return (b - a).seconds

    def init_post_scheduler(self, seconds=0, minutes=0, hours=0):
        self.post_image_task = tasks.Loop(self._post_random_image, seconds, hours, minutes, None, True, None)
        self.post_image_task.start()

    def get_default_post_channel(self):
        if not self.post_channel_name:
            print("Critical error. Unable to parse post channel from config.json. Please fix!\n")
            sys.exit(-1)

        channel = discord.utils.get(self.get_all_channels(), name=self.post_channel_name)

        if not channel:
            print(f"Unable to find channel {self.post_channel_name}, please confirm channel exists on Discord server.\n")
            sys.exit(-1)

        return channel

    async def on_ready(self):
        print(f'Bot has logged in as {self.user}')
        
        self.post_channel = self.get_default_post_channel()

    async def on_guild_join(self, guild):
        print(f'Bot has joined server {guild.name}')

    # async def on_message(self, message):
    #     # ignore bot sent messages
    #     if message.author == self.user:
    #         return

    #     if message.content.startswith(self.bot_invocation_str):
    #         tokens = message.content.split(' ')
    #         await self.post_random_image(message.channel)

    def scan_images(self):
        for f in os.listdir(self.image_dir):
            if os.path.isfile(os.path.join(self.image_dir, f)) and f not in self.already_posted:
                self.image_paths.append(f)

    def init_posted_images_cache(self):
        # two stage open.
        # sync open for read to help detect malformatted or corrupted caches 
        # and then async open for write in appropriate mode
        self.already_posted = self.load_posted_images_cache(self.posted_image_cache_filename) or []
        if not self.already_posted:
            self.cache_open_mode = 'w'  # truncate since file might be fkd and not empty

    def load_posted_images_cache(self, cache_filename):
        try:
            if os.path.isfile(cache_filename):
                with open(cache_filename, 'r') as fp:
                    return [line.strip() for line in fp]
        except Exception as ex:
            print("Caught exception:", ex)
        return None

    async def _post_random_image(self):
        if self.has_initialized: 
            await self.post_random_image(self.post_channel)

            self.post_image_task.cancel()
            self.init_post_scheduler(hours=24)
            self.has_initialized = False
        else:
            self.has_initialized = True

    async def post_random_image(self, channel):
        if len(self.image_paths) < 1:
            print('Warning: out of unique images to post!')
            return
        
        idx = random.randint(0, len(self.image_paths) - 1)
        image_path = self.image_paths.pop(idx)
        await self.send_image(channel, os.path.join(self.image_dir, image_path), self.default_caption)

        self.already_posted.append(image_path)
        print(f'Posted image: {image_path}\n')

        try:
            async with aiofiles.open(self.posted_image_cache_filename, mode=self.cache_open_mode) as fp:
                await fp.write(image_path +'\n')
        except Exception as ex:
            print("Warning: unable to write to posted image cache. Exception:\n", ex)

    async def send_image(self, channel, image_path, caption=None):
        # cant do async send without reimplementing discord.textchannel.send() :(
        with open(image_path, 'rb') as fp:
            await channel.send(content=caption, file=discord.File(fp))

    def run(self, *args, **kwargs):
        super().run(self.api_key, *args, **kwargs)

bot = PotdBot()
bot.run()
