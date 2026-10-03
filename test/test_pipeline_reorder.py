import shutil
import unittest
from pathlib import Path

import pandas as pd

from src.combine_csv import stage0_1_add_csvfilename, stage0_2_normalize_german_columns
from src.sm import run_pipeline


def _write_csv(path: Path, rows, columns):
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False)


class PipelineStageReorderTests(unittest.TestCase):
    def test_stage0_2_renames_german_statement_columns(self):
        with self.subTest():
            source_dir = Path("/tmp") / "statement_pipeline_german_test"
            if source_dir.exists():
                shutil.rmtree(source_dir)
            source_dir.mkdir()
            source_path = source_dir / "german.csv"
            source_path.write_text(
                "\ufeffBuchungstag;Wertstellung;Buchungstext;Betrag;Währung\n"
                "2026-09-30;2026-09-30;Grocer;19,52;EUR\n"
                "2026-10-01;2026-10-01;Cafe;'-19,52;EUR\n",
                encoding="utf-8",
            )

            prepared_path = stage0_1_add_csvfilename(source_path, source_dir / "prepared")
            normalized_paths = stage0_2_normalize_german_columns([prepared_path])
            df = pd.read_csv(normalized_paths[0])

            self.assertEqual(
                list(df.columns),
                ["Booking Date", "Wertstellung", "Partner Name", "Amount (EUR)", "Währung", "csvfilename"],
            )
            self.assertEqual(df["Partner Name"].tolist(), ["Grocer", "Cafe"])
            self.assertEqual(df["Amount (EUR)"].tolist(), [19.52, -19.52])

    def test_stage0_1_add_csvfilename_sets_source_stem(self):
        with self.subTest():
            source_dir = Path("/tmp") / "statement_pipeline_stage0_test"
            source_dir.mkdir(exist_ok=True)
            source_path = source_dir / "bank_01.csv"
            _write_csv(
                source_path,
                [["2026-01-10", "Grocer", -15.5, "extra"], ["2026-01-11", "Taxi", -7.0, "extra"]],
                ["Booking Date", "Partner Name", "Amount (EUR)", "Other"],
            )

            prepared_path = stage0_1_add_csvfilename(source_path, source_dir / "prepared")
            df = pd.read_csv(prepared_path)

            self.assertEqual(
                list(df.columns),
                ["Booking Date", "Partner Name", "Amount (EUR)", "Other", "csvfilename"],
            )
            self.assertEqual(df["csvfilename"].tolist(), ["bank_01", "bank_01"])

    def test_run_pipeline_reorders_stages_and_keeps_csvfilename(self):
        with self.subTest():
            source_dir = Path("/tmp") / "statement_pipeline_stage2_test"
            output_dir = Path("/tmp") / "statement_pipeline_stage2_out"
            if source_dir.exists():
                shutil.rmtree(source_dir)
            if output_dir.exists():
                shutil.rmtree(output_dir)

            source_dir.mkdir()
            output_dir.mkdir()

            _write_csv(
                source_dir / "first.csv",
                [["2026-01-10", "Grocer", -15.5, "x1"], ["2026-01-11", "Taxi", -7.0, "x2"]],
                ["Booking Date", "Partner Name", "Amount (EUR)", "Other"],
            )
            _write_csv(
                source_dir / "second.csv",
                [["2026-01-12", "Cafe", -22.0, "x3"]],
                ["Booking Date", "Partner Name", "Amount (EUR)", "Other"],
            )

            mapping_file = source_dir / "mapping.json"
            mapping_file.write_text('{"FOOD": ["Grocer", "Cafe"], "TRAVEL": ["Taxi"]}', encoding="utf-8")

            report_path = run_pipeline(source_dir, output_dir, mapping_file=str(mapping_file), debug=True)

            self.assertEqual(report_path, str(output_dir / "stage6_csv_to_html_output.html"))
            self.assertTrue(Path(report_path).exists())
            self.assertFalse((output_dir / ".statement_pipeline.lock").exists())

            stage2_files = sorted(output_dir.rglob("stage2_combine_csv_files_output.csv"))
            self.assertEqual(len(stage2_files), 1)

            combined = pd.read_csv(stage2_files[0])
            self.assertEqual(
                list(combined.columns),
                ["Booking Date", "Partner Name", "Amount (EUR)", "csvfilename"],
            )
            self.assertEqual(combined["csvfilename"].tolist(), ["first", "first", "second"])


if __name__ == "__main__":
    unittest.main()
