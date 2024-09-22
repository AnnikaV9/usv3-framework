import yaml
import argparse
import subprocess
import readline

class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False) -> None:
        return super(Dumper, self).increase_indent(flow, False)

class QuotedString(str):
    pass

def quoted_scalar(dumper, data) -> yaml.representer.Node:
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')

Dumper.add_representer(QuotedString, quoted_scalar)

def register_module(event, name) -> None:
    try:
        with open("config/modules.yml", "r") as module_registry:
            module_map = yaml.safe_load(module_registry)

        module_map[event][name] = {}
        if event in ("command", "whisper"):
            if event == "command":
                desc = input("Enter a description for this command: ")
                usage = input("Enter usage instructions for this command: ")
                module_map[event][name]["desc"] = f"{desc}\nUsage:\n{usage}"

            alias = input("Enter an alias for this command (Leave blank for none): ")
            if alias:
                module_map[event][name]["alias"] = alias

        module_map[event][name]["module"] = f"{event}.{name}"
        deps = input("""\nSpecify dependencies for this module
Comma separated, leave blank for none.
Format: name@version,name@version
See https://python-poetry.org/docs/dependency-specification/ on how to specify version constraints.
Enter dependencies: """)
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
    parser = argparse.ArgumentParser(description="Register a new module")
    parser.add_argument("event", type=str, help="event type (command/message/join/leave/whisper)", choices=["command", "message", "join", "leave", "whisper"], metavar="event")
    parser.add_argument("name", type=str, help="module name (filename without extension or path)")

    args = parser.parse_args()
    register_module(args.event, args.name)
