import json
import importlib

def load(bot, reload=False) -> int:
    with open("config/modules.json", "r", encoding="utf-8") as module_map_file:
        module_map = json.load(module_map_file)

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
