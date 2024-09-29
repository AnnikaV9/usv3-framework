#
#  The main bot class that handles the connection to the server
#  and triggers appropriate events.
#

import json
import asyncio
import websockets.asyncio.client
import websockets.exceptions
from types import SimpleNamespace
from loguru import logger

import usv3.loader
import usv3.runner


class Bot:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.modules: dict
        self.cmd_map: dict
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
        self.online_users = []
        self.online_hashes = {}
        self.online_trips = {}
        self.groups["mods"] = []
        usv3.loader.reinitialize(self)

    def get_namespace(self, event: str, name: str) -> SimpleNamespace:
        return getattr(getattr(self.namespaces, event), name)

    async def send(self, cmd: str = "chat", **kwargs) -> None:
        await self.ws.send(json.dumps({"cmd": cmd, **kwargs}))

    async def main(self) -> None:
        logger.info(f"Waiting for connection from {self.config['server']}")
        async for ws in websockets.asyncio.client.connect(self.config["server"], ping_timeout=None):
            logger.success(f"Connected to {self.config['server']}")
            try:
                self.ws = ws
                await self.send(cmd="join", nick=f"{self.config['nick']}#{self.config['password']}", channel=self.config["channel"])
                loops = asyncio.gather(self.ping_loop(), self.receive_loop())
                await loops

            except websockets.exceptions.ConnectionClosedError:
                if self.reconnect:
                    logger.error("Connection closed, resetting state")
                    if "loops" in locals():
                        loops.cancel()

                    self.reset_state()
                    logger.info(f"Waiting for connection from {self.config['server']}")
                    continue

                raise Exception("Connection closed, reconnect disabled")

    async def ping_loop(self) -> None:
        while True:
            await asyncio.sleep(60)
            await self.send(cmd="ping")

    async def receive_loop(self) -> None:
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
        trip = resp.get("trip")
        if trip == "":
            trip = None

        if resp["nick"] != self.config["nick"]:
            for handler in self.modules["message"]:
                asyncio.create_task(
                    usv3.runner.run(
                        self.modules["message"][handler].run, f"message.{handler}", self.config["debug"], self, self.get_namespace("message", handler), resp["text"], resp["nick"], trip
                    )
                )

            for command in self.modules["command"]:
                cmds_with_args = [f"{self.prefix}{command} "]
                cmds = [f"{self.prefix}{command}"]
                if "alias" in self.cmd_map["command"][command]:
                    cmds_with_args.append(f"{self.prefix}{self.cmd_map['command'][command]['alias']} ")
                    cmds.append(f"{self.prefix}{self.cmd_map['command'][command]['alias']}")

                if resp["text"].startswith(tuple(cmds_with_args)) or resp["text"] in cmds:
                    groups = self.cmd_map["command"][command].get("groups", [])
                    master_list = []
                    for group in groups:
                        if group in self.groups:
                            master_list.extend(self.groups[group])

                    if trip not in master_list and len(groups) > 0:
                        await self.reply(resp["nick"], "You don't have permission to use this command")

                    else:
                        asyncio.create_task(
                            usv3.runner.run(
                                self.modules["command"][command].run, f"command.{command}", self.config["debug"], self, self.get_namespace("command", command), resp["text"], resp["nick"], trip, resp["level"]
                            )
                        )

    async def handle_whisper(self, resp: dict) -> None:
        trip = resp.get("trip")
        if trip == "":
            trip = None

        if resp["from"] != self.config["nick"] and not resp["text"].startswith("You whispered to"):
            text = resp["text"].removeprefix(f"{resp['from']} whispered: ")
            for command in self.modules["whisper"]:
                cmds_with_args = [f"{command} "]
                cmds = [command]
                if "alias" in self.cmd_map["whisper"][command]:
                    cmds_with_args.append(f"{self.cmd_map['whisper'][command]['alias']} ")
                    cmds.append(self.cmd_map['whisper'][command]['alias'])

                if text.startswith(tuple(cmds_with_args)) or text in cmds:
                    groups = self.cmd_map["whisper"][command].get("groups", [])
                    master_list = []
                    for group in groups:
                        if group in self.groups:
                            master_list.extend(self.groups[group])

                    if trip not in master_list and len(groups) > 0:
                        await self.whisper(resp["from"], "You don't have permission to use this command")

                    else:
                        asyncio.create_task(
                            usv3.runner.run(
                                self.modules["whisper"][command].run, f"whisper.{command}", self.config["debug"], self, self.get_namespace("whisper", command), text, resp["from"], trip, resp["level"]
                            )
                        )

    async def handle_join(self, resp: dict) -> None:
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
        nick = resp["nick"]
        for handler in self.modules["leave"]:
            asyncio.create_task(
                usv3.runner.run(
                    self.modules["leave"][handler].run, f"leave.{handler}", self.config["debug"], self, self.get_namespace("leave", handler), resp["nick"]
                )
            )

        if self.online_trips[nick] in self.groups["mods"]:
            self.groups["mods"].remove(self.online_trips[nick])

        self.online_users.remove(nick)
        self.online_hashes.pop(nick)
        self.online_trips.pop(nick)

    async def handle_set(self, resp: dict) -> None:
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
        logger.warning(f"Server sent a warn: {resp['text']}")

    async def reply(self, nick: str, text: str) -> None:
        await self.send(text=f"**@{nick}** {text}")

    async def whisper(self, nick: str, text: str) -> None:
        await self.send(cmd="whisper", nick=nick, text=f"\\-\n{text}")
