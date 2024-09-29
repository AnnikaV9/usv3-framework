# usv3
An extensible bot framework for [hack.chat](https://hack.chat)


## Setting up
usv3 requires >= Python 3.10 and [poetry](https://python-poetry.org/)
1. Set up the project with `poetry install`
3. Configure the bot in [config](config)
4. Run the bot with `poetry run usv3`


## Adding your own stuff
usv3 can be extended by adding modules that get triggered on various events.

A basic module for the command event looks like this:
```python
class Module:
    # Metadata, all optional. Can have the following:
    # - description
    # - usage
    # - alias
    # - groups (list of groups that can access the command)
    description = "Your command's help text"
    usage = "[args1], [args2], [args3]..."

    @staticmethod
    async def run(bot, text, sender, trip, ulevel):
```
If your module needs to do stuff on load, use `on_load()`:
```python
class Module:
    ...metadata...

    @staticmethod
    def on_load(bot):
        bot.myglobalvar = 1
        # Whatever else that needs to be done

    @staticmethod
    async def run(bot, text, sender, trip, ulevel):
```

Different events take different arguments for `run()`:
|Event|Arguments|
|--|--|
|command|bot, text, sender, trip, ulevel|
|message|bot, text, sender, trip|
|join|bot, sender, hash, trip|
|leave|bot, sender|
|whisper|bot, text, sender, trip, ulevel|

A few example modules are shipped with the framework. You can use them as a reference to create your own.

After creating a module, place it in its respective event in [usv3/events](usv3/events). The module will be found and loaded automatically. If your module has any dependencies, add them to [pyproject.toml](pyproject.toml) under `tool.poetry.group.cmd.dependencies` and run `poetry update`

For chat/whisper commands, the name of the module will be the command that calls it. You can add an alias for each one if a shorter alternate command is needed.

The `reload` command live reloads all loaded modules and any new modules that have been added. Note that this will re-run `on_load()` in all modules that have it. The configuration file [config/extra_config.yml](config/extra_config.yml) will also be reloaded.


## Replying to the server
`bot.send()` can be used to reply to the server. It's defined in the core framework as:
```python
async def send(self, cmd: str = "chat", **kwargs) -> None:
    await self.ws.send(json.dumps({"cmd": cmd, **kwargs}))
```
To send a chat message:
```python
await bot.send(text="Hello World!")
```
An alternate command:
```python
await bot.send(cmd="changecolor", color="ff0000")
```
To reply to users in chat with a consistent format, use `bot.reply()`:
```python
await bot.reply(sender, "Hello!")
```
A whisper shortcut is also provided:
```python
await bot.whisper(sender, "Don't tell anyone")
```


## Cython modules
usv3 supports the building and loading of cython modules. Dependencies required for this are not installed by default, they can be with `poetry install -E cython`

Adding a cython module is pretty much the same as adding a pure python module, just drop the pyx file into its respective event. After that, run `poetry run build_cython` to build all cython modules.

> [!IMPORTANT]
> Unlike pure python modules, cython modules will not reflect changes after rebuilding when using the `reload` command. You will have to restart the bot to load the changes.


## Systemd
If you want to run usv3 as a systemd service, here's a sample unit file:
```ini
# usv3.service

[Unit]
Description=usv3
After=network-online.target

[Service]
ExecStart=/path/to/poetry run -n usv3
ExecStartPre=/path/to/poetry check -n --lock
WorkingDirectory=/home/<user>/path/to/usv3/directory
Restart=always
RestartSec=60
Type=simple

[Install]
WantedBy=default.target
```
Edit to match your setup and place it in `~/.config/systemd/user/`

Run `systemctl --user daemon-reload` and `systemctl --user enable --now usv3` to start and enable the service.

Once the service is up, you can run `systemctl --user status usv3` or `journalctl --user -e -u usv3` to view resource usage or logs.

> [!NOTE]
> If you have issues with usv3 being killed when you log out, enable lingering with `sudo loginctl enable-linger $USER`
