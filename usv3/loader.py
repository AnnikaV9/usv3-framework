import yaml
import importlib

def load(bot, reload=False) -> int:
    with (open("config/modules.yml", "r") as module_registry,
          open("config/cmd_config.yml", "r") as cmd_config,
          open("config/api_keys.yml", "r") as api_keys,
          open("config/admins.yml", "r") as admins):
        module_map = yaml.safe_load(module_registry)
        bot.cmd_config = yaml.safe_load(cmd_config)
        bot.api_keys = yaml.safe_load(api_keys)
        bot.admins = yaml.safe_load(admins)


    modules = {"command": {}, "message": {}, "join": {}, "leave": {}, "whisper": {}}
    num_modules = 0
    for event in module_map:
        for name in module_map[event]:
            module = importlib.import_module(f"usv3.events.{module_map[event][name]['module']}")
            if reload:
                importlib.reload(module)

            modules[event][name] = module.Module
            if hasattr(modules[event][name], "on_load"):
                modules[event][name].on_load(bot)

            num_modules += 1

    print(f"Loaded {num_modules} modules {'(reloaded)' if reload else ''}")
    bot.modules, bot.cmd_map = modules, module_map
    return num_modules
