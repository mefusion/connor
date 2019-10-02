import discord
from Saber.SaberCore import SECONDARY_COLOR, WARNING_COLOR, ERROR_COLOR, DEFAULT_COLOR, SUCCESS_COLOR, MAIN_LOGS_CHANNEL
import datetime

MOD_ACTION_COLOR = ERROR_COLOR


class Log:
    def __init__(self, log_type='info', log_data='Data was not specified'):
        self.type = log_type
        self.data = log_data

    async def send(self, client_object, send_to=MAIN_LOGS_CHANNEL):
        triggered_at = datetime.datetime.utcnow()

        log_embed = discord.Embed(
            description=self.data
        )

        log_embed.timestamp = triggered_at
        del triggered_at

        if self.type == 'info':
            log_embed.colour = SECONDARY_COLOR
        elif self.type == 'warning':
            log_embed.colour = WARNING_COLOR
        elif self.type == 'error':
            log_embed.colour = ERROR_COLOR
        elif self.type == 'success':
            log_embed.colour = SUCCESS_COLOR
        elif self.type == 'mod_action':
            log_embed.colour = MOD_ACTION_COLOR
        else:
            log_embed.colour = DEFAULT_COLOR

        channel = discord.Client.get_channel(client_object, send_to)
        return await channel.send(embed=log_embed)
