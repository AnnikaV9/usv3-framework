import json
import yaml
import asyncio
import websockets

import usv3.loader

class Bot:
    def __init__(self) -> None:
        self.ws: websockets.WebSocketClientProtocol
        with (open("config/core_config.yml", "r") as core_config,
              open("config/cmd_config.yml", "r") as cmd_config,
              open("config/api_keys.yml", "r") as api_keys,
              open("config/admins.yml", "r") as admins):
            self.config = yaml.safe_load(core_config)
            self.cmd_config = yaml.safe_load(cmd_config)
            self.api_keys = yaml.safe_load(api_keys)
            self.admins = yaml.safe_load(admins)

        self.modules = {}
        self.cmd_map = {}
        usv3.loader.load(self)

        self.online_users = []
        self.online_hashes = {}
        self.online_trips = {}

    async def send(self, cmd="chat", **kwargs) -> None:
        await self.ws.send(json.dumps({"cmd": cmd, **kwargs}))

    async def main(self) -> None:
        channel, server = self.config["channel"], self.config["server"]
        async with websockets.connect(server, ping_timeout=None) as ws:
            self.ws = ws
            await self.send(cmd="join", nick=f"{self.config['nick']}#{self.config['password']}", channel=channel)
            print(f"Joined {channel} on {server}")
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
                    trip = resp.get("trip")
                    if trip == "":
                        trip = None

                    if resp["nick"] != self.config["nick"]:
                        for handler in self.modules["message"]:
                            asyncio.create_task(self.modules["message"][handler].run(self, resp["text"], resp["nick"], trip))

                        for command in self.modules["command"]:
                            if resp["text"].startswith(f"{self.config['prefix']}{command} ") or resp["text"] == f"{self.config['prefix']}{command}":
                                asyncio.create_task(self.modules["command"][command].run(self, resp["text"], resp["nick"], trip, resp["level"]))

                            if "alias" in self.cmd_map["command"][command]:
                                if resp["text"].startswith(f"{self.config['prefix']}{self.cmd_map['command'][command]['alias']} ") or resp["text"] == f"{self.config['prefix']}{self.cmd_map['command'][command]['alias']}":
                                    asyncio.create_task(self.modules["command"][command].run(self, resp["text"], resp["nick"], trip, resp["level"]))

                case "info":
                    if resp.get("type") == "whisper":
                        trip = resp.get("trip")
                        if trip == "":
                            trip = None

                        if resp["from"] != self.config["nick"] and not resp["text"].startswith("You whispered to"):
                            text = resp["text"].removeprefix(f"{resp['from']} whispered: ")
                            for command in self.modules["whisper"]:
                                if resp["text"].startswith(f"{command} ") or resp["text"] == f"{command}":
                                    asyncio.create_task(self.modules["whisper"][command].run(self, text, resp["from"], trip))

                                if "alias" in self.cmd_map["whisper"][command]:
                                    if resp["text"].startswith(f"{self.cmd_map['whisper'][command]['alias']} ") or resp["text"] == f"{self.cmd_map['whisper'][command]['alias']}":
                                        asyncio.create_task(self.modules["whisper"][command].run(self, text, resp["from"], trip))

                case "onlineAdd":
                    trip = resp.get("trip")
                    if trip == "":
                        trip = None

                    nick = resp["nick"]
                    self.online_users.append(nick)
                    self.online_hashes[nick] = resp["hash"]
                    self.online_trips[nick] = trip
                    for handler in self.modules["join"]:
                        asyncio.create_task(self.modules["join"][handler].run(self, resp["nick"], resp["hash"], trip))

                case "onlineRemove":
                    nick = resp["nick"]
                    for handler in self.modules["leave"]:
                        asyncio.create_task(self.modules["leave"][handler].run(self, resp["nick"]))

                    self.online_users.remove(nick)
                    self.online_hashes.pop(nick)
                    self.online_trips.pop(nick)

                case "onlineSet":
                    for user in resp["users"]:
                        nick = user["nick"]
                        self.online_users.append(nick)
                        self.online_hashes[nick] = user["hash"]
                        self.online_trips[nick] = user["trip"] if user["trip"] != "" else None
