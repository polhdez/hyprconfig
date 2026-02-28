#!/usr/bin/env python3
import json
from dataclasses import dataclass
from subprocess import PIPE, Popen

SUPER = 64
ALT = 8
CTRL = 4
SHIFT = 1


@dataclass
class Response:
    return_code: int
    std_out: str
    std_err: str


def send_command(cmd: str) -> Response:
    shell = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    std_out, std_err = shell.communicate()
    return Response(
        shell.returncode, std_out.decode().strip(), std_err.decode().strip()
    )


def get_keys_from_mask(mask: int) -> list[str]:
    modifiers = []
    if mask >= SUPER:
        mask -= SUPER
        modifiers.append("SUPER")
    if mask >= ALT:
        mask -= ALT
        modifiers.append("Alt")
    if mask >= CTRL:
        mask -= CTRL
        modifiers.append("Ctrl")
    if mask == SHIFT:
        modifiers.append("Shift")
    return modifiers


def main() -> None:
    binds = json.loads(send_command("hyprctl binds -j").std_out)
    binds_map = {}
    for binding in binds:
        line_input = get_keys_from_mask(binding["modmask"])
        line_input.append(binding["key"])
        line_input = "+".join(line_input)
        line_input += " ➤ " + binding["dispatcher"] + " " + binding["arg"]
        binds_map[f"{line_input}"] = binding
    rofi_input = "\n".join(binds_map.keys())
    choice = send_command(f"echo '{rofi_input}' | wofi -p 'Hyprland Binds' -dmenu").std_out
    if choice:
        binding = binds_map[choice]
        command = f"{binding["dispatcher"]} {binding["arg"]}"
        send_command(f"hyprctl dispatch -- {command}")


if __name__ == "__main__":
    main()
