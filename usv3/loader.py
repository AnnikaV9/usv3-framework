#
#  Module loader that handles loading and reloading of modules.
#

import os
import importlib
from types import SimpleNamespace
from loguru import logger
from ruamel.yaml import YAML


def load(bot, reload: bool = False) -> tuple[int, int]:
    logger.info(f"{'Reloading' if reload else 'Loading'} configuration and modules")
    load_config(bot, reload)
    return load_modules(bot, reload)


def load_modules(bot, reload: bool) -> tuple[int, int]:
    module_map, num_modules = find_modules()
    modules = {"command": {}, "message": {}, "join": {}, "leave": {}, "whisper": {}}
    bot.namespaces = SimpleNamespace()
    failed = 0
    for event in module_map:
        setattr(bot.namespaces, event, SimpleNamespace())
        for name in module_map[event]:
            try:
                module = importlib.import_module(f"usv3.events.{module_map[event][name]['module']}")
                if reload:
                    importlib.reload(module)

                setattr(getattr(bot.namespaces, event), name, SimpleNamespace())
                if hasattr(module.Module, "on_load"):
                    module.Module.on_load(bot, getattr(getattr(bot.namespaces, event), name))

            except Exception as e:
                exc_logger = logger.exception if bot.config["debug"] else logger.error
                exc_logger(f"Failed to load module {event}.{name} ({type(e).__name__} {e})")
                failed += 1
                continue

            modules[event][name] = module.Module
            if hasattr(module.Module, "description"):
                module_map[event][name]["description"] = module.Module.description

            if hasattr(module.Module, "usage"):
                module_map[event][name]["usage"] = module.Module.usage

            if hasattr(module.Module, "min_args"):
                module_map[event][name]["min_args"] = module.Module.min_args

            if hasattr(module.Module, "max_args"):
                module_map[event][name]["max_args"] = module.Module.max_args

            if hasattr(module.Module, "alias"):
                module_map[event][name]["alias"] = module.Module.alias

            if hasattr(module.Module, "groups"):
                module_map[event][name]["groups"] = module.Module.groups

    exc_logger = logger.error if failed > 0 else logger.success
    exc_logger(f"{'Reloaded' if reload else 'Loaded'} modules ({num_modules} succeeded, {failed} failed)")
    bot.modules, bot.cmd_map = modules, module_map
    return num_modules, failed


def load_config(bot, reload: bool) -> None:
    yaml = YAML(typ="safe")
    with open("config/extra_config.yml", "r") as extra_config:
        extra_config = yaml.load(extra_config)

    bot.cmd_config = extra_config["cmd_config"]
    bot.api_keys = extra_config["api_keys"]
    bot.reconnect = extra_config["reconnect"]
    extra_config["groups"]["mods"] = []
    if reload:
        extra_config["groups"]["mods"].extend(bot.groups["mods"])

    bot.groups = extra_config["groups"]
    bot.prefix = extra_config["prefix"]
    logger.success(f"{'Reloaded' if reload else 'Loaded'} config/extra_config.yml")


def find_modules() -> tuple[dict[str, dict[str, dict[str, str]]], int]:
    logger.info("Searching for modules")
    num_modules = 0
    module_map = {"command": {}, "message": {}, "join": {}, "leave": {}, "whisper": {}}
    for root, _, files in os.walk("usv3/events"):
        for file in sorted(files):
            if file.endswith((".py", ".so")):
                event = os.path.basename(root)
                name = file.split(".")[0]
                module_map[event][name] = {"module": f"{event}.{name}"}
                num_modules += 1

    logger.info(f"Found {num_modules} modules")
    return module_map, num_modules


def unload(bot, modules: list) -> None:
    for module in modules:
        event, name = module.split(".")
        del bot.modules[event][name]
        del bot.cmd_map[event][name]
        logger.info(f"Unloaded module {event}.{name}")


def reinitialize(bot) -> None:
    for event in bot.modules:
        for module in bot.modules[event]:
            setattr(getattr(bot.namespaces, event), module, SimpleNamespace())
            if hasattr(bot.modules[event][module], "on_load"):
                bot.modules[event][module].on_load(bot, getattr(getattr(bot.namespaces, event), module))
