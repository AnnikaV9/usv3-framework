"""
The main bot class that handles the connection to the server
and triggers appropriate events.
"""

# stdlib
import asyncio
import json
import time
from types import SimpleNamespace
from typing import Literal

# external
import uvloop
import websockets.asyncio.client
import websockets.exceptions
from loguru import logger

# internal
import usv3.loader
import usv3.runner


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class Bot:
    def __init__(self, config: dict) -> None:
        """
        Initializes the bot by loading configuration and modules.
        """
        self.config = config
        self.modules: dict
        self.cmd_map: dict
        self.commands: dict
        self.cooldowns: dict
        self.cmd_config: dict
        self.api_keys: dict
        self.groups: dict
        self.prefix: str
        self.reconnect: bool
        self.namespaces: SimpleNamespace
        usv3.loader.load(self)

        self.online_users = []
        self.online_hashes = {}
        self.online_trips = {}

    def reset_state(self) -> None:
        """
        Resets the bot state by clearing online users reinitializing the loader.
        """
        self.online_users = []
        self.online_hashes = {}
        self.online_trips = {}
        self.groups["mods"] = []
        usv3.loader.reinitialize(self)

    def get_namespace(self, event: str, name: str) -> SimpleNamespace:
        """
        Returns the namespace for a given event and name.
        """
        return getattr(getattr(self.namespaces, event), name)

    async def send(self, cmd: str = "chat", **kwargs) -> None:
        """
        Sends a packet to the server.
        """
        await self.ws.send(json.dumps({"cmd": cmd, **kwargs}))

    async def main(self) -> None:
        """
        Connects to the server, joins the channel and starts the recv loop.
        """
        logger.info(f"Waiting for connection from {self.config['server']}")
        async for ws in websockets.asyncio.client.connect(self.config["server"], ping_timeout=None):
            logger.success(f"Connected to {self.config['server']}")
            try:
                self.ws = ws
                await self.send(cmd="join", nick=f"{self.config['nick']}#{self.config['password']}", channel=self.config["channel"])
                loop = asyncio.create_task(self.recv_loop())
                await loop

            except websockets.exceptions.ConnectionClosedError:
                if self.reconnect:
                    logger.error("Connection closed, resetting state")
                    loop.cancel()
                    self.reset_state()
                    logger.info(f"Waiting for connection from {self.config['server']}")
                    continue

                raise Exception("Connection closed, reconnect disabled")

    async def recv_loop(self) -> None:
        """
        Main loop that receives packets from the server and triggers events.
        """
        while True:
            resp = await self.ws.recv()
            resp = json.loads(resp)
            match resp["cmd"]:
                case "chat":
                    await self.handle_chat(resp)

                case "info":
                    if resp.get("type") == "whisper":
                        await self.handle_whisper(resp)

                case "onlineAdd":
                    await self.handle_join(resp)

                case "onlineRemove":
                    await self.handle_leave(resp)

                case "onlineSet":
                    await self.handle_set(resp)

                case "warn":
                    await self.handle_warn(resp)

    async def handle_chat(self, resp: dict) -> None:
        """
        Handles chat messages and runs the command handler.
        """
        trip = resp.get("trip")
        if trip == "":
            trip = None

        if resp["nick"] != self.config["nick"]:
            for handler in self.modules["message"]:
                asyncio.create_task(
                    usv3.runner.run(
                        self.modules["message"][handler].run, f"message.{handler}", self.config["debug"], self, self.get_namespace("message", handler), resp["text"], resp["nick"], trip, resp["level"]
                    )
                )

            await self.parse_handle_command("command", trip, resp["nick"], resp["level"], resp["text"])

    async def handle_whisper(self, resp: dict) -> None:
        """
        Handles whisper messages and runs the command handler.
        """
        trip = resp.get("trip")
        if trip == "":
            trip = None

        if resp["from"] != self.config["nick"] and not resp["text"].startswith("You whispered to"):
            text = resp["text"].removeprefix(f"{resp['from']} whispered: ")
            await self.parse_handle_command("whisper", trip, resp["from"], resp["level"], text)

    async def parse_handle_command(self, event: Literal["command", "whisper"], trip: str | None, nick: str, level: int, text: str) -> None:
        """
        Triggers the appropriate command/whisper event.
        """
        reply, prefix = (self.reply, self.prefix) if event == "command" else (self.whisper, "")
        for command in self.modules[event]:
            commands = self.commands[event][command]
            if text.startswith(tuple(commands["w_args"])) or text in commands["wo_args"]:
                groups = self.cmd_map[event][command].get("groups", [])
                allowed = []
                for group in groups:
                    if group in self.groups:
                        allowed.extend(self.groups[group])

                if trip not in allowed and len(allowed) > 0:
                    await reply(nick, "You don't have permission to use this command")
                    return

                args = text.split()[1:]
                n_args = len(args)
                if "min_args" in self.cmd_map[event][command] and n_args < self.cmd_map[event][command]["min_args"]:
                    await reply(nick, f"Usage: {prefix}{command} {self.cmd_map[event][command]['usage']}")
                    return

                if "max_args" in self.cmd_map[event][command] and n_args > self.cmd_map[event][command]["max_args"]:
                    await reply(nick, f"Usage: {prefix}{command} {self.cmd_map[event][command]['usage']}")
                    return

                cooldown = True if "cooldown" in self.cmd_map[event][command] else False
                if cooldown:
                    left = self.cmd_map[event][command]["cooldown"] - (int(time.time()) - self.cooldowns[event][command])
                    if left > 0:
                        await reply(nick, f"This command is on cooldown ({left} {'seconds' if left > 1 else 'second'} left)")
                        return

                asyncio.create_task(
                    usv3.runner.run(
                        self.modules[event][command].run, f"{event}.{command}", self.config["debug"], self, self.get_namespace(event, command), text, args, nick, trip, level
                    )
                )

                if cooldown:
                    self.cooldowns[event][command] = int(time.time())

    async def handle_join(self, resp: dict) -> None:
        """
        Handles join events.
        """
        trip = resp.get("trip")
        if trip == "":
            trip = None

        nick = resp["nick"]
        self.online_users.append(nick)
        self.online_hashes[nick] = resp["hash"]
        self.online_trips[nick] = trip
        if resp["level"] >= 999999:
            self.groups["mods"].append(trip)

        for handler in self.modules["join"]:
            asyncio.create_task(
                usv3.runner.run(
                    self.modules["join"][handler].run, f"join.{handler}", self.config["debug"], self, self.get_namespace("join", handler), resp["nick"], resp["hash"], resp["trip"]
                )
            )

    async def handle_leave(self, resp: dict) -> None:
        """
        Handles leave events.
        """
        nick = resp["nick"]
        for handler in self.modules["leave"]:
            asyncio.create_task(
                usv3.runner.run(
                    self.modules["leave"][handler].run, f"leave.{handler}", self.config["debug"], self, self.get_namespace("leave", handler), resp["nick"], self.online_hashes[nick], self.online_trips[nick]
                )
            )

        if self.online_trips[nick] in self.groups["mods"]:
            self.groups["mods"].remove(self.online_trips[nick])

        self.online_users.remove(nick)
        self.online_hashes.pop(nick)
        self.online_trips.pop(nick)

    async def handle_set(self, resp: dict) -> None:
        """
        Handles the set event upon joining a channel.
        """
        logger.success(f"Joined channel: {resp['channel']}")
        for user in resp["users"]:
            nick = user["nick"]
            self.online_users.append(nick)
            self.online_hashes[nick] = user["hash"]
            self.online_trips[nick] = user["trip"] if user["trip"] != "" else None
            if user["level"] >= 999999:
                self.groups["mods"].append(user["trip"])

        logger.success("usv3 is now live!")

    async def handle_warn(self, resp: dict) -> None:
        """
        Passes warn messages to the logger.
        """
        logger.warning(f"Server sent a warn: {resp['text']}")

    async def reply(self, nick: str, text: str) -> None:
        """
        Sends a message to the chat, mentioning the user.
        Format: **@nick** text
        """
        await self.send(text=f"**@{nick}** {text}")

    async def whisper(self, nick: str, text: str) -> None:
        """
        Sends a whisper to a user.
        Format:
                usv3 whispered: -
                Hello
        """
        await self.send(cmd="whisper", nick=nick, text=f"\\-\n{text}")
