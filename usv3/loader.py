"""
Module loader that handles loading and reloading of modules.
"""

# stdlib
import importlib
import os
from types import SimpleNamespace

# external
from loguru import logger
from ruamel.yaml import YAML


def load(bot, reload: bool = False) -> tuple[int, int]:
    """
    Entry point for loading or reloading configuration and modules.
    """
    logger.info(f"{'Reloading' if reload else 'Loading'} configuration and modules")
    load_config(bot, reload)
    return load_modules(bot, reload)


def load_modules(bot, reload: bool) -> tuple[int, int]:
    """
    Loads or reloads modules, returning the number of successful and failed loads.
    """
    module_map, num_modules = find_modules()
    modules = {"command": {}, "message": {}, "join": {}, "leave": {}, "whisper": {}}
    commands = {"command": {}, "whisper": {}}
    cooldowns = {"command": {}, "whisper": {}}
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
            if event in commands:
                commands[event][name] = {"w_args": [], "wo_args": []}
                prefix = bot.prefix if event == "command" else ""
                commands[event][name]["w_args"].append(f"{prefix}{name} ")
                commands[event][name]["wo_args"].append(f"{prefix}{name}")
                mod_config = {}
                if module.Module.__doc__:
                    yaml = YAML(typ="safe")
                    mod_config = yaml.load(module.Module.__doc__)

                if "alias" in mod_config:
                    commands[event][name]["w_args"].append(f"{prefix}{mod_config['alias']} ")
                    commands[event][name]["wo_args"].append(f"{prefix}{mod_config['alias']}")
                    module_map[event][name]["alias"] = mod_config["alias"]

                if "desc" in mod_config:
                    module_map[event][name]["desc"] = mod_config["desc"]

                if "usage" in mod_config:
                    module_map[event][name]["usage"] = mod_config["usage"]

                if "min_args" in mod_config:
                    module_map[event][name]["min_args"] = mod_config["min_args"]

                if "max_args" in mod_config:
                    module_map[event][name]["max_args"] = mod_config["max_args"]

                if "groups" in mod_config:
                    module_map[event][name]["groups"] = mod_config["groups"]

                if "cooldown" in mod_config:
                    cooldowns[event][name] = 0
                    module_map[event][name]["cooldown"] = mod_config["cooldown"]

    exc_logger = logger.error if failed > 0 else logger.success
    num_modules -= failed
    exc_logger(f"{'Reloaded' if reload else 'Loaded'} modules ({num_modules} succeeded, {failed} failed)")
    bot.modules, bot.cmd_map, bot.commands, bot.cooldowns = modules, module_map, commands, cooldowns
    return num_modules, failed


def load_config(bot, reload: bool) -> None:
    """
    Loads or reloads configuration from config/extra_config.yml.
    """
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
    """
    Searches for modules in the usv3/events directory.
    """
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
    """
    Unloads a list of modules.
    """
    for module in modules:
        event, name = module.split(".")
        del bot.modules[event][name]
        del bot.cmd_map[event][name]
        logger.info(f"Unloaded module {event}.{name}")


def reinitialize(bot) -> None:
    """
    Re-runs the on_load method for all loaded modules and resets their
    namespaces.
    """
    for event in bot.modules:
        for module in bot.modules[event]:
            setattr(getattr(bot.namespaces, event), module, SimpleNamespace())
            if hasattr(bot.modules[event][module], "on_load"):
                bot.modules[event][module].on_load(bot, getattr(getattr(bot.namespaces, event), module))
