from __future__ import annotations

import sys

from rich.console import Console

from src.game.game import Game
from src.game.parser import Parser

from src.media.paths import resource_path, user_data_path
from pathlib import Path


def main() -> None:
    """Check the arguments, load the config and run the game."""
    if len(sys.argv) == 1 and getattr(sys, "frozen", False):
        sys.argv.append(resource_path("config.json"))
    if len(sys.argv) != 2:
        raise ValueError("Expected exactly one configuration file.")
    if not sys.argv[1].endswith(".json"):
        raise ValueError("Configuration file must be a JSON file.")

    data = Parser(sys.argv[1]).load_config()
    if getattr(sys, "frozen", False):
        name = Path(data.get("highscore_filename", "highscores.json")).name
        data["highscore_filename"] = user_data_path(name)
    Game(data).run()


if __name__ == "__main__":
    console = Console()
    try:
        main()
    except Exception as e:
        console.print("[red]❌ Something went wrong:[/red]", e)
