import argparse
import json
from pathlib import Path


class CategoryJsonCombiner:
    """Combine category-to-items JSON files from a directory."""

    def __init__(self, directory):
        self.directory = Path(directory)
        self._combined_data = self._load_category_files()

    def _load_category_files(self):
        combined_data = {}

        for json_path in sorted(self.directory.glob("*.json")):
            with json_path.open("r", encoding="utf-8") as file:
                category_data = json.load(file)

            if not isinstance(category_data, dict):
                raise ValueError(
                    f"JSON file '{json_path}' must contain an object at the root level"
                )

            for category, items in category_data.items():
                if not isinstance(items, list):
                    raise ValueError(
                        f"Value for category '{category}' in '{json_path}' must be a list"
                    )
                combined_data.setdefault(category, []).extend(items)

        return combined_data

    def get_combined_json_data(self):
        """Return the combined category mapping."""
        return self._combined_data

    def save_to_json(self, output_file):
        """Save the combined mapping to a JSON file and return its path."""
        output_path = Path(output_file)
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(self._combined_data, file, ensure_ascii=False, indent=4)
            file.write("\n")
        return output_path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Combine category mapping JSON files from a directory."
    )
    parser.add_argument("directory", help="Directory containing category JSON files")
    parser.add_argument("output_file", help="Filename for the combined category JSON")
    args = parser.parse_args(argv)

    output_path = CategoryJsonCombiner(args.directory).save_to_json(args.output_file)
    print(f"Combined category file saved to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())