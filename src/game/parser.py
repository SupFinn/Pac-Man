import json
from typing import Any, Dict


class Parser:
    def __init__(self, filepath: str) -> None:
        """Store the path of the config file."""
        self.filepath = filepath

    def load_config(self) -> dict:
        """Read the config, skip comment lines and validate the JSON."""
        try:
            with open(self.filepath, "r") as file:
                lines = file.readlines()
            config = ""
            for line in lines:
                # ignore comments that starts with # and c++ style comments
                if (not line.lstrip().startswith('#') and
                   not line.lstrip().startswith("//")):
                    config += line
            data = json.loads(config)
            return self._data_validation(data)
        except FileNotFoundError:
            raise Exception(f"Invalid path to file: '{self.filepath}'")
        except PermissionError:
            raise Exception("You don't have permission to access the file")
        except Exception as e:
            raise e

    def _data_validation(self, data: dict) -> Dict[str, Any]:
        """Check keys and types, and lowercase the config keys."""
        VALIDKEYS = [
            "highscore_filename",
            "lives",
            "points_per_pacgum",
            "points_per_super_pacgum",
            "points_per_ghost",
            "seed",
            "levels",
        ]
        LEVEL_KEYS = ["width", "height", "max_time"]
        # Validate config file keys
        for key in data.keys():
            # making sure that the provided key is valid
            if key.lower() not in VALIDKEYS:
                raise ValueError(f"{key} is not a valid key !")
            # if key is highscore file name , it should ends with .txt
            elif key.lower() == "highscore_filename":
                if not data[key].endswith(".json"):
                    raise ValueError(
                        "highscore_filaname should .json file"
                    )
            # if the key is level we should over each level and check the dicts
            elif key.lower() == "levels":
                for level in data[key]:
                    for subkey, value in level.items():
                        if subkey.lower() not in LEVEL_KEYS:
                            raise ValueError(
                                f"{subkey} is not a valid key, "
                                f"please use one of the following:{LEVEL_KEYS}"
                            )
                        try:
                            level[subkey] = int(value)
                        except Exception:
                            raise ValueError(
                                f"{subkey} value should be a valid integer"
                            )
                        self._maze_dimentions_validator(
                            subkey, level[subkey]
                        )
            # else it should be a valid integer
            else:
                try:
                    data[key] = int(data[key])
                except Exception:
                    raise ValueError(
                        f"{key} value should be a valid integer"
                    )
        data = {key.lower(): value for key, value in data.items()}
        return data

    def _maze_dimentions_validator(self, key: str, value: int) -> None:
        """Raise an error if a maze width or height is out of range."""
        min_height = 9
        max_height = 41
        min_width = 9
        max_width = 41

        if key == "height":
            if value <= min_height:
                raise ValueError(
                    f"the min height of the maze should be {min_height}, "
                    f"you provided: {value}"
                )
            if value >= max_height:
                raise ValueError(
                    f"the max height of the maze should be {max_height}, "
                    f"you provided: {value}"
                )

        if key == "width":
            if value <= min_width:
                raise ValueError(
                    f"the min width of the maze should be {min_width}, "
                    f"you provided: {value}"
                )
            if value >= max_width:
                raise ValueError(
                    f"the max width of the maze should be {max_width}, "
                    f"you provided: {value}"
                )
