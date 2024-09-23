#
#  Module loader that handles loading and reloading of modules.
#

import os
import yaml
import importlib

def load(bot, reload=False) -> int:
    with (open("config/cmd_config.yml", "r") as cmd_config,
          open("config/api_keys.yml", "r") as api_keys,
          open("config/admins.yml", "r") as admins):
        bot.cmd_config = yaml.safe_load(cmd_config)
        bot.api_keys = yaml.safe_load(api_keys)
        bot.admins = yaml.safe_load(admins)

    module_map = find_modules()
    modules = {"command": {}, "message": {}, "join": {}, "leave": {}, "whisper": {}}
    num_modules = 0
    for event in module_map:
        for name in module_map[event]:
            module = importlib.import_module(f"usv3.events.{module_map[event][name]['module']}")
            if reload:
                importlib.reload(module)

            modules[event][name] = module.Module
            if hasattr(module.Module, "on_load"):
                module.Module.on_load(bot)

            if hasattr(module.Module, "description"):
                module_map[event][name]["description"] = module.Module.description

            if hasattr(module.Module, "usage"):
                module_map[event][name]["usage"] = module.Module.usage

            if hasattr(module.Module, "alias"):
                module_map[event][name]["alias"] = module.Module.alias

            if hasattr(module.Module, "admin_only"):
                module_map[event][name]["admin_only"] = module.Module.admin_only

            num_modules += 1

    print(f"Loaded {num_modules} modules {'(reloaded)' if reload else ''}")
    bot.modules, bot.cmd_map = modules, module_map
    return num_modules

def find_modules() -> dict:
    module_map = {"command": {}, "message": {}, "join": {}, "leave": {}, "whisper": {}}
    for root, _, files in os.walk("usv3/events"):
        for file in files:
            if file.endswith(".py"):
                event = os.path.basename(root)
                name = os.path.splitext(file)[0]
                module_map[event][name] = {"module": f"{event}.{name}"}

    return module_map
