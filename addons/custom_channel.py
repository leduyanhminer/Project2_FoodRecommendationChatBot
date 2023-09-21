import asyncio
import inspect
import discord
from sanic import Sanic, response
from sanic.request import Request
from typing import Text, Callable, Awaitable

from rasa.core.channels.channel import InputChannel, UserMessage, CollectingOutputChannel
intents = discord.Intents.default()
intents.typing = False
intents.presences = False

client = discord.Client(intents=intents)  # Define the client instance

class MyIO(InputChannel):
    @classmethod
    def name(cls) -> Text:
        return "myio"

    @staticmethod
    async def on_new_message(
        text: Text, output_channel: CollectingOutputChannel, sender_id: Text, input_channel: Text, metadata: dict
    ) -> None:
        collector = output_channel

        collector.messages.append({"text": text, "sender_id": sender_id, "input_channel": input_channel, "metadata": metadata})

    def blueprint(
        self, on_new_message: Callable[[Text, CollectingOutputChannel, Text, Text, dict], Awaitable[None]]
    ) -> Sanic:
        custom_webhook = Sanic(__name__)

        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> response.HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> response.HTTPResponse:
            sender_id = request.json.get("sender")
            text = request.json.get("text")
            input_channel = self.name()
            metadata = self.get_metadata(request)

            collector = CollectingOutputChannel()

            await on_new_message(
                UserMessage(
                    text,
                    collector,
                    sender_id,
                    input_channel=input_channel,
                    metadata=metadata,
                )
            )

            return response.json(collector.messages)

        return custom_webhook

intents = discord.Intents.default()         
intents.typing = False
intents.presences = False

async def rasa_to_discord(text: Text, channel: discord.TextChannel):
    # Send user message to Rasa and get Rasa's response
    input_channel = "myio"
    sender_id = str(channel.guild.id)
    metadata = {}

    collector = CollectingOutputChannel()
    print(collector)
    await MyIO.on_new_message(text, collector, sender_id, input_channel, metadata)

    collected_messages = collector.messages
    print("Collected Messages:", collected_messages)

    if collected_messages:
        rasa_response = collected_messages[-1].get("text", "")
        if rasa_response.strip():  # Check if the response is not empty or only contains whitespace
            print("Rasa Response:", rasa_response)
            await channel.send(rasa_response)
        else:
            print("Rasa Response is empty.")
    else:
        print("No messages collected from Rasa.")


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Handle the received message here and send it to Rasa
    if isinstance(message.channel, discord.TextChannel):
        await rasa_to_discord(message.content, message.channel)

client.run("TOKEN")
