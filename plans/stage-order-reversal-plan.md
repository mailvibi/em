# Plan: Reverse Pipeline Stages 1 and 2

## Goal

Add a preparation sequence before the existing processing stages. Stage 0_1 adds a `csvfilename` column to every source CSV, Stage 0_2 is an explicit pass-through placeholder with no data transformation, and Stage 0_3 validates required columns in every prepared CSV. Stage 1 then removes unwanted columns from each file, and Stage 2 combines the cleaned files. All later stages must continue to receive the expected combined schema.

## Current behavior

`sm.py` currently calls `stage1_combine_csv_files`, which reads all source files, adds `csvfilename`, concatenates them, and writes a combined CSV. `stage2_remove_columns_from_csv` then selects `Booking Date`, `Partner Name`, `Amount (EUR)`, and `csvfilename` from that combined file. In non-debug runs, both stage files are deleted; debug runs retain them.

## Proposed implementation

1. **Source discovery:** Resolve the input and output directories, including symlink aliases, and snapshot the input CSV file list before generating artifacts. Require the output directory to be outside the input directory (not equal to it or a descendant), so generated files cannot become source inputs on this or later runs. Detect and reject known legacy pipeline CSV artifacts already present in the input directory, with a clear message to move them before retrying. Preserve the snapshot order through all preparation stages.
2. **Stage 0_1, add source filename:** For each source CSV, add or overwrite `csvfilename` with that source file's stem. Preserve all original columns and rows. Write prepared copies only into a unique run-scoped working directory, never beside source files.
3. **Stage 0_2, pass through:** Represent this as an orchestration-only identity step: receive and return the same prepared-file list and metadata, emit the stage progress event, and create no file or copy.
4. **Stage 0_3, validate required columns:** Validate the parsed header of every prepared file before Stage 1 begins. Required source headers are `Booking Date`, `Partner Name`, and `Amount (EUR)`; `csvfilename` is excluded because Stage 0_1 creates it. Report unreadable files and missing columns with the source filename. Reject structurally malformed rows with inconsistent field counts and include the source filename and row when available. This is a schema/CSV-structure check only; cell-level null, date, and amount validation remains with existing downstream stages. A zero-byte or unparsable CSV fails; a valid header-only CSV passes. If the complete input set has zero transaction rows, fail clearly instead of producing an empty report. On any preparation or validation failure, remove the current run's working directory and do not leave partial stage artifacts.
5. **Stage 1, remove unwanted columns:** For every validated prepared file, select exactly `DEFAULT_COLUMNS_TO_KEEP` in its declared order. Write a uniquely named artifact per source file in the run-scoped working directory; do not reuse the current fixed output path for each file.
6. **Stage 2, combine:** Concatenate the exact ordered list of Stage 1 artifacts, preserving within-file row order and all selected values. Do not regenerate or alter `csvfilename` during combination. Keep the resulting schema compatible with Stage 3 and later stages.
7. Write all intermediate CSVs from Stages 0_1 through 5 into the current run's unique working directory. In debug mode, retain that run directory and return/document its location; in normal mode, remove it after report creation. Do not let fixed stage filenames in the shared output directory be used for intermediates. Keep the final HTML report at the existing `stage6_csv_to_html_output.html` path for compatibility, but publish it only after successful generation using an atomic replace. Serialize runs targeting the same output directory with a process-safe advisory lock held through final publication, so they cannot overwrite each other's in-progress intermediates or report. Cleanup only the current run's working directory.
8. Leave categorization and later stages unchanged unless focused tests reveal a direct compatibility issue.

## Risks and regressions to guard against

- **Lost or overwritten provenance:** Stage 0_1 must reliably set `csvfilename` from the source file stem before Stage 1 selects columns. If an input already has a `csvfilename` column, define and test that the generated source stem overwrites it.
- **Unclear pass-through semantics:** Stage 0_2 should not accidentally mutate files, duplicate them, or alter stage ordering; define whether it is represented as an explicit pipeline step only or also has a debug artifact/progress event.
- **Schema variation:** independently cleaned files may have different extra headers or column order. Selection must produce the same ordered schema, while missing configured input columns must fail rather than silently creating blank values.
- **Stage artifact compatibility:** consumers or users may depend on existing stage-named intermediate CSV paths, including debug output. Moving debug artifacts under a unique run directory changes their paths; document this or provide a compatibility export if evidence shows external consumers rely on the old paths.
- **Incorrect progress or cleanup:** GUI/CLI progress text and cleanup may still assume the old ordering or filenames. Debug mode must retain only that run's complete intermediate set, and non-debug mode must remove only that run's working directory.
- **Input/output overlap and legacy artifacts:** reject output directories equal to or nested under the resolved source directory, snapshot source files, and reject known legacy stage CSV outputs already in the source directory. Test symlink aliases as well as ordinary paths.
- **Concurrent runs:** fixed stage filenames in the shared output directory can collide. Use a process-safe output-directory lock and run-scoped intermediates; retain the current final report path and replace it atomically only after a successful run.
- **Empty or invalid inputs:** distinguish no source files, zero-byte/unparsable files, valid header-only files, and an input set with no transaction rows. Report parse/validation errors with the source filename.
- **Partial preparation:** stage artifacts must be created in a unique run-scoped work directory and removed on failure; cleanup must never delete source files or artifacts belonging to another run.
- **Ordering changes:** `Path.glob` ordering is not guaranteed; this activity should not accidentally promise a new cross-file row order. Within each source file, preserve row order.
- **Performance and memory:** concatenation still requires holding cleaned records; avoid needless read/write cycles for per-file intermediates unless debug behavior requires them.

## Validation plan

1. Test Stage 0_1: each source receives its own stem in `csvfilename`, original values/rows are preserved, and an existing `csvfilename` is overwritten. Verify prepared files go into a unique run-scoped directory.
2. Verify Stage 0_2 passes through the same ordered file list and metadata, makes no copies, and reports its progress event.
3. Test Stage 0_3: each absent required source header fails with source filename and missing column names; source `csvfilename` is not required; all files are validated before Stage 1 writes artifacts. Zero-byte/unparsable input and inconsistent row widths fail with source/row context; valid header-only input passes when other files contain rows; an entirely rowless input set fails clearly. Confirm cell-level null/date/amount behavior is not silently changed by schema validation.
4. Test Stage 1 with multiple valid files containing extra columns and different header orders. Assert each source gets a distinct output path with exactly the configured columns in order.
5. Test Stage 2 consumes only the supplied Stage 1 artifacts, preserves the original source-stem values in `csvfilename`, and preserves values and within-file row order.
6. Test no source files, output directory equal to or nested under input, symlink aliases, known legacy stage artifacts in input, repeated runs, and debug/non-debug cleanup. Confirm source files and artifacts from other runs are untouched and no prior output can enter source discovery.
7. Test two simultaneous runs targeting the same output directory: the advisory lock must serialize them, intermediates must remain isolated, and the stable final report path must contain a complete successful run rather than partial output.
8. Run a full CLI pipeline smoke test with representative statements. Confirm downstream report generation, progress labels for stages 0_1 through 2, run-scoped intermediate retention/cleanup, and stable final report path. Check whether the repository has an existing test runner before selecting or adding one.
9. Review the final diff for stale stage names and verify documentation or executable configuration only changes if the pipeline interface actually requires it.

## Approval gate

No implementation changes are included in this plan. Wait for the user to approve this plan before editing source code or tests.