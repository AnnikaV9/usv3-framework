#
#  The main bot class that handles the connection to the server
#  and triggers appropriate events.
#

import json
import yaml
import asyncio
import websockets

import usv3.loader

class Bot:
    def __init__(self) -> None:
        self.ws: websockets.WebSocketClientProtocol
        with open("config/core_config.yml", "r") as core_config:
            self.config = yaml.safe_load(core_config)

        self.modules = {}
        self.cmd_map = {}
        self.cmd_config = {}
        self.api_keys = {}
        self.admins = []
        usv3.loader.load(self)

        self.online_users = []
        self.online_hashes = {}
        self.online_trips = {}

    async def send(self, cmd="chat", **kwargs) -> None:
        await self.ws.send(json.dumps({"cmd": cmd, **kwargs}))

    async def main(self) -> None:
        async with websockets.connect(self.config["server"], ping_timeout=None) as ws:
            self.ws = ws
            await self.send(cmd="join", nick=f"{self.config['nick']}#{self.config['password']}", channel=self.config["channel"])
            await asyncio.gather(self.ping_loop(), self.receive_loop())

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

    async def handle_chat(self, resp) -> None:
        trip = resp.get("trip")
        if trip == "":
            trip = None

        if resp["nick"] != self.config["nick"]:
            for handler in self.modules["message"]:
                asyncio.create_task(self.modules["message"][handler].run(self, resp["text"], resp["nick"], trip))

            for command in self.modules["command"]:
                cmds_with_args = [f"{self.config['prefix']}{command} "]
                cmds = [f"{self.config['prefix']}{command}"]
                if "alias" in self.cmd_map["command"][command]:
                    cmds_with_args.append(f"{self.config['prefix']}{self.cmd_map['command'][command]['alias']} ")
                    cmds.append(f"{self.config['prefix']}{self.cmd_map['command'][command]['alias']}")

                if resp["text"].startswith(tuple(cmds_with_args)) or resp["text"] in cmds:
                    if self.cmd_map["command"][command].get("admin_only", False) and trip not in self.admins:
                        await self.reply(resp["nick"], "You don't have permission to use this command")

                    else:
                        asyncio.create_task(self.modules["command"][command].run(self, resp["text"], resp["nick"], trip, resp["level"]))

    async def handle_whisper(self, resp) -> None:
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
                    if self.cmd_map["whisper"][command].get("admin_only", False) and trip not in self.admins:
                        await self.send(cmd="whisper", nick=resp["from"], text="You don't have permission to use this command")

                    else:
                        asyncio.create_task(self.modules["whisper"][command].run(self, text, resp["from"], trip, resp["level"]))

    async def handle_join(self, resp) -> None:
        trip = resp.get("trip")
        if trip == "":
            trip = None

        nick = resp["nick"]
        self.online_users.append(nick)
        self.online_hashes[nick] = resp["hash"]
        self.online_trips[nick] = trip
        for handler in self.modules["join"]:
            asyncio.create_task(self.modules["join"][handler].run(self, resp["nick"], resp["hash"], trip))

    async def handle_leave(self, resp) -> None:
        nick = resp["nick"]
        for handler in self.modules["leave"]:
            asyncio.create_task(self.modules["leave"][handler].run(self, resp["nick"]))

        self.online_users.remove(nick)
        self.online_hashes.pop(nick)
        self.online_trips.pop(nick)

    async def handle_set(self, resp) -> None:
        print(f"Joined {resp['channel']} on {self.config['server']}")
        for user in resp["users"]:
            nick = user["nick"]
            self.online_users.append(nick)
            self.online_hashes[nick] = user["hash"]
            self.online_trips[nick] = user["trip"] if user["trip"] != "" else None

    async def reply(self, nick, text) -> None:
        await self.send(text=f"**@{nick}** {text}")
