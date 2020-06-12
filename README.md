# attack-json-to-csv
Translates ATT&amp;CK Navigator JSON files into CSV format

## Requirements
* Python 3
* click
* requests

```bash
pip install -r requirements.txt
```

## Usage

```
Usage: build.py [OPTIONS] TECHNIQUE_JSON OUTPUT_FILENAME

  Takes a JSON file from ATT&CK Navigator and converts it to CSV format

  Args:

      technique_json (click.Path): ATT&CK Navigator JSON file
      output_filename (string): Name of the file to be saved
      fetch_techniques (bool): Flag to fetch remote techniques

Options:
  --fetch-techniques
  --help              Show this message and exit.
```

The script depends on a JSON file of Mitre ATT&CK techniques on the filesystem. If running the script for the first time, add the `--fetch-techniques` flag to the end of the command:

```bash
python build.py Sample_OSX_Operation_TTPs.json sample --fetch-techniques
```

## Demo
![](https://s3.us-east-2.amazonaws.com/gifs.stevecoward.com/demo.gif)
