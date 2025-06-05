# Requirements for the `markdown-to-data` cli tool

## Important

This cli tool is a feature of the python library `markdown-to-data`. The development of the cli tool is highly bundled to the development of `markdown-to-data`
The cli tool's code is located in `/src/cli_tool` of the `markdown-to-data` repository

## Technology

- Python cli application built using `typer` for the cli tool application and `rich` for the visualization
- The cli tool is an extra/optional dependency of the `markdown-to-data` library and can be install via `pip install markdown-to-data[cli]`. In case of `pip install markdown-to-data` the cli tool would not be installed
- This repository uses `uv` (not `pip` or `poetry`) to manage its dependencies and to built and publish the package

## Philosophy of Coding

The CLI tool will be mainly used to process markdown files but also to analyse them. As common for a CLI tool, the analysis commands will print the outcome into the terminal, while the processing commands will print an information whether if the process was successful or not, plus some summary about the process outcome itself.
But, as there is planned to also use the commands in further features of this library, it needs be to be considered to create reusable functions which return data and use the print methods at the latest level of the process.
As `typer` comes whith type hints capabilities, the development of the cli tool for `markdown-to-data` is also using type hints.

## Additional Features

- tab completion for commands and files
  - includes a command to enable/install tab completion
  - tab completion for commands and options (dynamically)
  - tab completion for files and folders (dynamically)
- interactive mode via `m2d init`

## Commands

**Overview of commands**:

- command `tree` for visualization of the files within the directory
- command `search` to search for files or content
  - in specific directory or all sub-directories
- single file and also batch processing commands:
  - commands for single files are...
    - `convert`
    - `extract`
    - `info`
    - `md`
  - commands for batch processing are...
    - `batch-convert`
    - `batch-extract`
      - should support for code the type of programming language
    - `batch-info`
    - `batch-md`

| Command   | Input         | Output        | Purpose                    |
| --------- | ------------- | ------------- | -------------------------- |
| `tree`    | Directory     | Terminal/Text | Visualize file structure   |
| `info`    | `.md`         | Terminal      | Analyze markdown files     |
| `convert` | `.md`         | `.json`       | Convert to structured data |
| `extract` | `.md`         | `.json`       | Extract specific elements  |
| `md`      | `.md`/`.json` | `.md`         | Process/filter markdown    |
| `search`  | Directory     | Terminal      | Find content/patterns      |

### `tree`

Prints the tree structure of markdown-files in the terminal with option to store the tree as `.txt` file.

```bash
m2d tree --save tree_structure.txt

Command: tree
--> Saved file: `tree_structure.txt`
```

**Arguments**:

- Required: None
- Optional: `<directory>` (default current directory)
  - example with directory as argument: `m2d tree /docs`
  - example without directory as argument: `m2d tree`

**Options**:

- `--save` - to save a `.txt` file in the directory. Can receive an argument for the file name or path. Default is `tree.txt`.
- `--no-subdirs` - exclude subdirectories

**Examples of print outputs**:

```bash
m2d tree

Command: tree
<directory>:
|-folder1
| |-file2.md
| |-file3.md
|-folder2
| |-sub-folder1
| | |-file5.md
| | |-file6.md
| |-file5.md
|-file1.md
```

```bash
m2d tree --save tree/tree_file.txt

Command: tree
--> Saved file: tree/tree_file.txt
<directory>:
|-folder1
| |-file2.md
| |-file3.md
|-folder2
| |-sub-folder1
| | |-file5.md
| | |-file6.md
| |-file5.md
|-file1.md
```

```bash
m2d tree --no-subdirs

Command: tree
>directory>:
|-file1.md
```

#### Error Handling

- No files
- Permission errors: Helpful message about file permissions

### `info` and `batch-info`

The `info` commands are used to get information about a file or several files when processing with `batch-info`. Can process markdown files.
The info output can be just printed or saved into a file or files.

**Infos when single file processing with `info`**:

- metadata
- table of content
- words count (exluding the metadata and symbols)
- building blocks (table with overview)

**Infos when batch processing with `batch-info` or `b-info`**:

- a merged overview of single processed files (see above)

#### `info`

**Arguments**:

- Required: `<file_path>` - markdown file to process. Accepts only `.md` files
- Optional: None

**Options**:

- `--include` - for specifying what info needs to be displayed
  - `metadata`
  - `toc` - table of content
  - `words` - number of words within file
  - `blocks`- overview of markdown elements within the file
  - combine values in quotation marks, e.g. `"metadata toc"`
  - default will include all

**Example input**:

```markdown
---
title: Example title
author: John Doe
tags: [tag1, tag2]
---

# Header level 1

Some text as paragraph

## Header level 2

- list item 1
- list item 2

## Header level 2
```

**Example output**:

```bash
m2d info file.md

Command: info
--> Processed file: `file.md`
|------------------------------------------------------------|
| file    | metadata             | table_of_content | blocks |
|---------|----------------------|------------------|--------|
| file.md | title: Example title | Header level 1   | h1: 1  |
|         | author: Johne Doe    | |-Header level 2 | h2: 1  |
|         | tags: [tag1, tag2]   | |-Header level 2 | p: 1   |
|         |                      |                  | l: 1   |
|------------------------------------------------------------|
```

#### `batch-info`

**Arguments**:

- Required: None
- Optional: `<directory>` (default: current directory)
  - example with directory: `m2d batch-info /docs`
  - example without directory: `m2d batch-info`

**Options**:

- all optional arguments from `info` (see above)
- `--no-subdirs` - exclude subdirectories

**Example input**:

markdown file file1.md:

```markdown
---
title: Example title
author: John Doe
tags: [tag1, tag2]
---

# Header level 1

Some text as paragraph

## Header level 2

- list item 1
- list item 2

## Header level 2
```

markdown file file2.md

```markdown
---
title: Example title 2
author: Anna White
tags: [tag1, tag2]
---

# Header level 1

## Header level 2

Some paragraph

# Header level 1
```

**Example output**:

```bash
m2d batch-info

Command: batch-info
--> Processed files: 2
|---------------------------------------------------------------|
| file     | metadata               | table_of_content | blocks |
|----------|------------------------|------------------|--------|
| file1.md | title: Example title   | Header level 1   | h1: 1  |
|          | author: Johne Doe      | |-Header level 2 | h2: 1  |
|          | tags: [tag1, tag2]     | |-Header level 2 | p: 1   |
|          |                        |                  | l: 1   |
|----------|------------------------|------------------|--------|
| file2.md | title: Example title 2 | Header level 1   | h1: 2  |
|          | author: Anna White     | |-Header level 2 | h2: 1  |
|          | tags: [tag1, tag2]     | Header level 1   | p: 1   |
|---------------------------------------------------------------|
```

#### Error Handling

- Unsupported file types: Display error message and list supported formats
- Missing files: Clear "file not found" message
- Permission errors: Helpful message about file permissions

### `convert` and `batch-convert`

The `convert` and `batch-convert` commands are used to convert a single or a batch of markdown files into structured json (saved in files). All created files will be saved in the original directory structure unless `--output` directory is provided.

#### `convert`

```bash
m2d convert file.md --structure list --output docs/converted_file.json

Command: convert
--> Processed file: `file.md`
--> Saved file: `docs/converted_file.json`
```

```bash
m2d convert file.md

Command: convert
--> Processed file: `file.md`
--> Saved file: `file.json`
```

For single file processing the command `convert` is used

**Arguments**:

- Required: `<file_path>` - markdown file to process. Accepts only `.md` files
- Optional: None

**Options**:

- `--structure` - setting the output structure to be `list` or `dict` (default `dict`)
- `--output` - output file path

#### `batch-convert`

For multiple files processing the command `batch-convert` is used.

**Arguments**:

- Required: None
- Optional: `<directory>` (default: current directory)
  - example: `m2d batch-convert /docs`

**Options**:

- `--structure` - for setting the output structure to be `list` or `dict`
  - accepts `dict` or `list`
  - example: `m2d batch-convert docs/ --structure list`
- `--prefix` - setting a prefix in front of each file
  - example: `m2d batch-convert /docs --prefix json_`
- `--no-subdirs` - exclude subdirectories
- `--output` - directory to store files
  - example: `m2d batch-convert --output processed/`

#### Error Handling

- Unsupported file types: Display error message and list supported formats
- Missing files: Clear "file not found" or "No files found" message
- Permission errors: Helpful message about file permissions

### `extract` and `batch-extract`

Parse a `.md` file into a `.json` file with structured data in an array/list.

#### `extract`

```bash
# Extract specific markdown elements from files
m2d extract <file_path> --elements "table code" --output extracted_data.json
```

**Purpose**: Extract specific markdown building blocks without full conversion

**Arguments**:

- Required: `<file_path>` - markdown file to process. Accepts only `.md` files
- Optional: None

**Options**:

- `--elements` - specify which elements to extract
  - Accepts: `metadata`, `headers`, `paragraph`, `blockquote`, `list`, `def_list`, `table`, `code`, `separator`, `h1`-`h6`
  - Example: `m2d extract file.md --elem "table h1 code"`
- `--output` - output file path
  - Default: `<filename>_extracted.json`
- `--combine` - combine all extracted elements into single structure
  - Default: separate by element type

#### `batch-extract`

```bash
# Batch extract from multiple files
m2d batch-extract /docs --elements "table"
```

**Arguments**:

- Optional: `<directory>` (default: current directory)

**Options**:

- All options from `extract` command
- `--no-subdirs` - exclude subdirectories
- `--prefix` - add prefix to output files
- `--output` - directory to store files

#### Error Handling

- Unsupported file types: Display error message and list supported formats
- Missing files: Clear "file not found" message
- Permission errors: Helpful message about file permissions

### `md` and `batch-md`

This command can process to kinds of file types:

- `.md`
- `.json`

The output is always a `.md` file.

When a `.md` file is provided, the command `md` uses the method `to_md` of the class `Markdown` of the `markdown-to-data` library. This will first parse the content of the `.md` file into a `list` of structured data and return the markdown content again to store it in a new `.md` file. Within this process the parsed content can be manipulated with the options `--include`, `--exclude` and `--spacer`.
When providing a `.json` file, the command `md` uses the function `to_md_parser` instead. This function is also used by the `to_md` method of the class `Markdown` but receives a `list` of an already parsed `.md` file. The output is a `.md` file while the options `--include`, `--exclude` and `--spacer` can also be applied to manipulate the content before saved in the `.md` file.

#### `md`

For single file processing the command `md` is used.

**Arguments**:

- Required: `<file_path>` - markdown file to process. Accepts `.md` and `.json` files
  - example: `m2d md file.md` or `m2d md file.json`
- Optional: None

**Options**:

- `--include` - only provided elements will be included.
  - `metadata`
  - `headers` or `h1`, `h2`, `h3`, `h4`, `h5` or `h6`
  - `paragraph`
  - `blockquote`
  - `list`
  - `def_list`
  - `table`
  - `code`
  - `separator`
  - `all` - to include all elements. Is default when not usind `--include`
  - example: `m2d md file.md --include "h1 code table separator"`
- `--exclude` - exclude provided elements. Overwrites `--include` parameters. Default is no excluded elements
  - `metadata`
  - `headers` or `h1`, `h2`, `h3`, `h4`, `h5` or `h6`
  - `paragraph`
  - `blockquote`
  - `list`
  - `def_list`
  - `table`
  - `code`
  - `separator`
  - `all` - will exclude all elements which results in an empty file
  - example: `m2d md file.md --exclude "h1 code table separator"`
- `--spacer` - number of empty lines between elements. Default is 1. Accepts integers >=0
  - example: `m2d md --spacer 2`
- `--output` - name or file path. Default is current diretory and file name with prefix `new_`.

```bash
m2d md file.md --exclude "metadata separator"

Command: md
--> Processed file: file.md
--> Saved file: new_file.md
```

```bash
m2d md file.md --spacer 2 --output docs/file_processed.md

Command: md
--> Processed file: file.md
--> Saved file: docs/file_processed.md
```

```bash
m2d md file.json

Command: md
--> Processed file: file.json
--> Saved file: new_file.md
```

#### `batch-md`

For batch processing `batch-md` is used. All created files will be saved in the original directory structure unless `--output` directory is provided.

**Arguments**:

- Required: None
- Optional: `<directory>` (default: current directory)
  - example: `m2d batch-md /docs`

**Options**:

- `--include` - only provided elements will be included.
  - `metadata`
  - `headers` or `h1`, `h2`, `h3`, `h4`, `h5` or `h6`
  - `paragraph`
  - `blockquote`
  - `list`
  - `def_list`
  - `table`
  - `code`
  - `separator`
  - `all` - to include all elements. Is default when not usind `--include`
  - example: `m2d batch-md --include "h1 code table separator"`
- `--exclude` - exclude provided elements. Overwrites `--include` parameters. Default is no excluded elements
  - `metadata`
  - `headers` or `h1`, `h2`, `h3`, `h4`, `h5` or `h6`
  - `paragraph`
  - `blockquote`
  - `list`
  - `def_list`
  - `table`
  - `code`
  - `separator`
  - `all` - will exclude all elements which results in an empty file
  - example: `m2d batch-md --exclude "h1 code table separator"`
- `--spacer` - number of empty lines between elements. Default is 1. Accepts integers >=0
  - example: `m2d batch-md --spacer 2`
- `--prefix` for setting a prefix in front of the file. Default is `new_` to not overwrite the existing files
  - example: `m2d batch-md /docs --prefix new_`
- `--no-subdirs` - exclude subdirectories
- `--output` - directory to store files
  - example: `m2d batch-md --output processed/`

#### JSON Structure Validation:

- Must be a list of dictionaries in the `md_list` format of `markdown-to-data`
- Each dictionary should represent a markdown element
- Invalid structure will show validation errors with details

#### Error Handling

- Unsupported file types: Display error message and list supported formats
- Invalid JSON structure: Show validation error with line number
- Missing files: Clear "file not found" or "No files found" message
- Permission errors: Helpful message about file permissions

### `search`

Search for specific content, patterns, or structural elements.

```bash
# Search for content or patterns in markdown files
m2d search "function" --type content --in code
```

````

**Arguments**:

- Required: `<query>` - search term or pattern
- Optional: `<directory>` (default: current directory)

**Options**:

- `--type` - search type
  - `content` - search in text content
  - `structure` - search for structural patterns
  - `metadata` - search in frontmatter
- `--in` - limit search to specific elements
  - Accepts same values as `--elements` in extract
- `--regex` - treat query as regex pattern
- `--case-sensitive` - case-sensitive search
- `--no-subdirs` - exclude subdirectories

**Example outputs**:

```bash
m2d search "TODO" --type content

Command: search
Found 3 matches in 2 files:
├── docs/readme.md:15: "TODO: Add more examples"
├── src/main.md:8: "- [ ] TODO: Implement feature"
└── src/main.md:23: "TODO: Review this section"
```

#### Error Handling

- No files
- Permission errors: Helpful message about file permissions

### `m2d init` for interactive mode

**Features in interactive mode**:

- Tab completion for commands and files
- Command history
- Simplified command syntax (no `m2d` prefix needed)

```bash
m2d init

Welcome to m2d interactive mode!
type 'help' for available commands, 'exit' to quit.

m2d>
```
````
