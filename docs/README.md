# usv3
An extensible bot framework for [hack.chat](https://hack.chat)


## Setting up
usv3 requires Python ^3.10 and [Poetry](https://python-poetry.org/)
1. Set up the project with `poetry install`
2. Configure the bot in [config](../config)
3. Run the bot with `poetry run usv3`


## Adding your own stuff
usv3 can be extended by adding modules that get triggered on various events.

A basic module for the command event looks like this:
```python
class Module:
    # Metadata, all optional. Can have the following:
    # - description
    # - usage
    # - min_args (Sends usage if not met)
    # - max_args (Sends usage if exceeded)
    # - alias
    # - groups (list of groups that can access the command)
    description = "Your command's help text"
    usage = "<arg1> [arg2] [arg3]"
    min_args = 1
    max_args = 3

    @staticmethod
    async def run(bot, namespace, text, args, sender, trip, ulevel):
```
If your module needs to do stuff on load, use `on_load()`:
```python
class Module:
    ...metadata...

    @staticmethod
    def on_load(bot, namespace):
        namespace.mylist = []
        # Whatever else that needs to be done

    @staticmethod
    async def run(bot, namespace, text, args, sender, trip, ulevel):
```

Different events take different arguments for `run()`:
|Events|Arguments|
|--|--|
|command, whisper|`bot` `namespace` `text` `args` `sender` `trip` `ulevel`|
|message|`bot` `namespace` `text` `sender` `trip` `ulevel`|
|join, leave|`bot` `namespace` `sender` `hash` `trip`|

Here's a breakdown of all the arguments:
|Argument|Description|
|--|--|
|`bot`|Main usv3 instance, see warning below.|
|`namespace`|Module's namespace.|
|`text`|Full message text without the command stripped.|
|`args`|Text trailing the command split into a list of arguments.|
|`sender`|Sender's nickname.|
|`hash`|Sender's connection hash.|
|`trip`|Sender's tripcode.|
|`ulevel`|Sender's user level. See [hack-chat/main/commands/utility/_UAC.js](https://github.com/hack-chat/main/blob/752d172dd58022f5c65dc8d002ebc9da71949b1d/commands/utility/_UAC.js#L51-L60)|

> [!WARNING]
> The `bot` object is the main usv3 instance, messing with its attributes can result in crashes. Safe methods you can call from `bot` are `send()`, `reply()` and `whisper()`. These are documented in the next section.

A namespace is created for each module. This can be used as a safe place to store data that needs to be accessed later or shared between different modules. Within the same module, this is available as `namespace`. A different module's namespace can be accessed with `bot.namespaces.<event>.<name>`.

A few example modules are shipped with the framework. You can use them as reference when creating your own. More modules that aren't examples/essentials can found in a [separate repository](https://github.com/AnnikaV9/usv3-modules).


After creating a module, place it in its respective event in [usv3/events](../usv3/events). The module will be found and loaded automatically. If your module has any dependencies, add them to [pyproject.toml](../pyproject.toml) under `tool.poetry.group.cmd.dependencies` and run `poetry update`.

For chat/whisper commands, the name of the module will be the command that calls it. You can add an alias for each one if a shorter alternate command is needed.

The `reload` command live reloads all loaded modules and any new modules that have been added. Note that this will re-run `on_load()` in all modules that have it. The configuration file [config/extra_config.yml](../config/extra_config.yml) will also be reloaded.


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


## Useful attributes
The `bot` object manages a few useful attributes that can be read from within modules:
|Attribute|Description|
|--|--|
|`online_users`|*List* of online nicknames.|
|`online_trips`|*Dictionary* of online nicknames and their respective trips.|
|`online_hashes`|*Dictionary* of online nicknames and their respective connection hashes.|

> [!WARNING]
> These attributes are meant to be read-only. Modifying them from a module can result in crashes.


## Cython modules
usv3 supports the building and loading of cython modules. Dependencies required for this are not installed by default, they can be with `poetry install -E cython`.

Adding a cython module is pretty much the same as adding a pure python module, just drop the pyx file into its respective event. After that, run `poetry run build_cython` to build all cython modules.

> [!NOTE]
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
Edit to match your setup and place it in `~/.config/systemd/user/`.

Run `systemctl --user daemon-reload` and `systemctl --user enable --now usv3` to start and enable the service.

Once the service is up, you can run `systemctl --user status usv3` or `journalctl --user -e -u usv3` to view resource usage or logs.

> [!NOTE]
> If you have issues with usv3 being killed when you log out, enable lingering with `sudo loginctl enable-linger $USER`.
