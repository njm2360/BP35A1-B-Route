import re
import json
import dataclasses
from typing import Dict, Type, TypeVar

T = TypeVar("T", bound="JsonSerializable")


def snake_to_camel(snake_str: str) -> str:
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def camel_to_snake(camel_str: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()


class JsonSerializable:
    def to_json(self, file_path: str = None) -> str:
        data = {snake_to_camel(k): v for k, v in dataclasses.asdict(self).items()}
        json_str = json.dumps(data, indent=4)

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_str)

        return json_str

    @classmethod
    def from_json(cls: Type[T], json_str: str = None, file_path: str = None) -> T:
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = json.loads(json_str)

        snake_data = {camel_to_snake(k): v for k, v in data.items()}

        valid_fields = {field.name for field in dataclasses.fields(cls)}
        filtered_data: Dict[str, object] = {
            k: v for k, v in snake_data.items() if k in valid_fields
        }

        if set(filtered_data.keys()) != set(snake_data.keys()):
            raise ValueError("Invalid fields found in JSON data.")

        return cls(**filtered_data)
