# usv3
An extensible bot framework for [hack.chat](https://hack.chat)


## Setting up
1. Install dependencies in [setup/core_requirements.txt](./setup/core_requirements.txt)
2. Configure the bot with the files inside [config](./config)
3. Run the bot with `python main.py`


## Adding modules
usv3 can be extended by adding modules to events in [usv3/events](usv3/events)

A basic module for the command event looks like this:
```python
class Module:
    async def run(bot, text, sender, tripcode, ulevel):
        # Whatever you want here
```
If your module needs to do stuff on load, you can do so with `on_load()`:
```python
class Module:
    def on_load(bot):
        bot.myglobalvar = 1
        # Whatever else that needs to be done

    async def run(bot, text, sender, tripcode, ulevel):
        # Whatever you want here
```
Different events take different arguments for `run()`:
|Event|Arguments|
|--|--|
|command|bot, text, sender, tripcode, ulevel|
|message|bot, text, sender, tripcode|
|join|bot, sender, hash, trip|
|leave|bot, sender|
|whisper|bot, text, sender, tripcode|

After adding modules, you can register them by adding them to [config/modules.json](config/modules.json)

For chat/whisper commands, the name that you register the module as will be the command that calls it. You can add an alias for each one if a shorter alternate command is needed.

The `reload` module is provided for live reloading every module and any new modules that have been registered without disconnecting the bot. Note that this will re-run `on_load()` in all modules that have it. 
