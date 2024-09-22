# usv3
An extensible bot framework for [hack.chat](https://hack.chat)


## Setting up
1. Install dependencies in [setup/core_requirements.txt](setup/core_requirements.txt)
   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -r setup/core_requirements.txt
   ```

3. Configure the bot with the files inside [config](config)
4. Run the bot with `python main.py`


## Adding modules
usv3 can be extended by adding modules to events in [usv3/events](usv3/events)

A basic module for the command event looks like this:
```python
class Module:
    async def run(bot, text, sender, trip, ulevel):
```
If your module needs to do stuff on load, you can do so with `on_load()`:
```python
class Module:
    def on_load(bot):
        bot.myglobalvar = 1
        # Whatever else that needs to be done

    async def run(bot, text, sender, trip, ulevel):
```
`on_load()` should not be asynchronous.

Different events take different arguments for `run()`:
|Event|Arguments|
|--|--|
|command|bot, text, sender, trip, ulevel|
|message|bot, text, sender, trip|
|join|bot, sender, hash, trip|
|leave|bot, sender|
|whisper|bot, text, sender, trip, ulevel|

Configuration options from [config/admins.yml](config/admins.yml), [config/api_keys.yml](config/api_keys.yml), [config/core_config.yml](config/core_config.yml) and [config/cmd_config.yml](config/cmd_config.yml) are loaded as `bot.admins`, `bot.api_keys`, `bot.config` and `bot.cmd_config` respectively.

After adding modules, you can register them by adding them to [config/modules.yml](config/modules.yml)

For chat/whisper commands, the name that you register the module as will be the command that calls it. You can add an alias for each one if a shorter alternate command is needed.

The `reload` command can be used for live reloading every module and any new modules that have been registered without disconnecting the bot. Note that this will re-run `on_load()` in all modules that have it. Every configuration file except [config/core_config.yml](config/core_config.yml) will be reloaded.

## Replying to the server
The `bot.send()` function can be used to reply to the server. It's defined in the core framework as:
```python
async def send(self, cmd="chat", **kwargs) -> None:
    await self.ws.send(json.dumps({"cmd": cmd, **kwargs}))
```
To send a chat command:
```python
await bot.send(text="Hello World!")
```
An alternate command:
```python
await bot.send(cmd="changecolor", color="ff0000")
```
