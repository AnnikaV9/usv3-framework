#
#  Setup wizard for registering new modules. This script will
#  prompt the user for various information required to register
#  a new module with the bot. The module will then be copied to
#  the appropriate event folder and added to the module registry.
#  Module dependencies will be added to pyproject.toml.
#

import os
import yaml
import argparse
import subprocess
from rich.prompt import Prompt, Confirm

class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False) -> None:
        return super(Dumper, self).increase_indent(flow, False)

class QuotedString(str):
    pass

def quoted_scalar(dumper, data) -> yaml.representer.Node:
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')

Dumper.add_representer(QuotedString, quoted_scalar)

def register_module(file) -> None:
    try:
        with open("config/modules.yml", "r") as module_registry:
            module_map = yaml.safe_load(module_registry)

        name = os.path.splitext(os.path.basename(file))[0]
        event = Prompt.ask("Enter the event type for this module", choices=["command", "message", "join", "leave", "whisper"], default="command")
        with open(file, "r") as source:
            try:
                with open(f"usv3/events/{event}/{name}.py", "x") as module:
                    module.write(source.read())

            except FileExistsError:
                overwrite = Confirm.ask(f"Module {name}.py already exists in usv3/events/{event}, overwrite?", default=False)
                if not overwrite:
                    raise SystemExit

                with open(f"usv3/events/{event}/{name}.py", "w") as module:
                    module.write(source.read())

        module_map[event][name] = {}
        if event in ("command", "whisper"):
            if event == "command":
                desc = Prompt.ask("Enter a description for this command")
                usage = Prompt.ask("Enter usage instructions for this command")
                module_map[event][name]["desc"] = f"{desc}\nUsage:\n{usage}"

            alias = Prompt.ask("Enter an alias for this command (Leave blank for none)")
            if alias:
                module_map[event][name]["alias"] = alias

        module_map[event][name]["module"] = f"{event}.{name}"
        print("""\nSpecify dependencies for this module
Comma separated, leave blank for none.
Format: name@version,name@version
See https://python-poetry.org/docs/dependency-specification/ on how to specify version constraints.""")
        deps = Prompt.ask("Enter dependencies: ")
        if deps:
            deps = deps.split(",")
            subprocess.run(["poetry", "add", "-G", f"cmd_{name}", "--lock"] + deps, check=True)

        for name in module_map["command"]:
            module_map["command"][name]["desc"] = QuotedString(module_map["command"][name]["desc"])

        with open("config/modules.yml", "w") as module_registry:
            yaml.dump(module_map, module_registry, sort_keys=False, Dumper=Dumper, default_flow_style=False)

    except KeyboardInterrupt:
        raise SystemExit

def main() -> None:
    parser = argparse.ArgumentParser(description="register a new module")
    parser.add_argument("file", type=str, help="the file to register")
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        raise SystemExit(f"register: error: file {args.file} could not be found")

    register_module(args.file)
