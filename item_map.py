import json
from pathlib import Path


ITEM_TO_CATAGORY_MAP_FILE = Path(__file__).resolve().with_name(
    "shopname_category_mapping.json"
)


def get_item_map(json_filename=None):
    """Load the item-to-category mapping and return its reversed form."""
    mapping_path = Path(json_filename) if json_filename is not None else ITEM_TO_CATAGORY_MAP_FILE

    try:
        with mapping_path.open("r", encoding="utf-8") as file:
            original_dict = json.load(file)

        if not isinstance(original_dict, dict):
            raise ValueError("JSON file must contain a dictionary at the root level")

        reversed_dict = {}
        for category, items in original_dict.items():
            if not isinstance(items, (list, tuple)):
                raise ValueError(f"Value for key '{category}' must be a list")
            for item in items:
                try:
                    hash(item)
                except TypeError as error:
                    raise ValueError(
                        f"Value '{item}' for key '{category}' is not hashable and cannot be used as a dictionary key"
                    ) from error
                reversed_dict[item] = category

        return reversed_dict
    except FileNotFoundError as error:
        raise Exception(f"JSON file '{mapping_path}' not found") from error
    except json.JSONDecodeError as error:
        raise Exception(f"Invalid JSON format in file '{mapping_path}': {error}") from error
    except Exception as error:
        raise Exception(f"Error processing JSON file '{mapping_path}': {error}") from error