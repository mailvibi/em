import json
import tempfile
import unittest
from pathlib import Path

from src.find_uncategorized_items import extract_uncategorized_items


class FindUncategorizedGermanCsvTests(unittest.TestCase):
    def test_extract_uncategorized_items_reads_german_statement_csv(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            source_path = Path(temporary_directory) / "german_statement.csv"
            source_path.write_text(
                "\ufeffBuchungstag;Wertstellung;Buchungstext;Betrag;Währung\n"
                "2026-09-30;2026-09-30;Known Store;-10.00;EUR\n"
                "2026-09-29;2026-09-29;Unknown Vendor;-15.50;EUR\n",
                encoding="utf-8",
            )
            mapping_path = Path(temporary_directory) / "mapping.json"
            mapping_path.write_text(
                json.dumps({"FOOD": ["Known Store"]}),
                encoding="utf-8",
            )

            result = extract_uncategorized_items(
                source_path, mapping_file=mapping_path
            )

            self.assertEqual(
                result.to_dict("records"),
                [
                    {
                        "Booking Date": "2026-09-29",
                        "Partner Name": "Unknown Vendor",
                        "CSV File Name": "german_statement.csv",
                        "Occurrences": 1,
                    }
                ],
            )


if __name__ == "__main__":
    unittest.main()