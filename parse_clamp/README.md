# CLAMP Annotation Parser
This is a simple tool to convert a directory of `.xmi` files containing annotations to a one-hot encoded `.csv` file for analysis. The tool assumes all annotations are in separate files in the directory `parse_clamp/input_data/`, though a different target may be specified.

## Dependencies
I have not written this to be production level code. It has been tested on OSX systems only. It is written for Python3.7.6 with no regard for backwards compatibility. My conda env has been exported in the file `annotation_tools/parse_clamp/FULL_CONDA_ENV.txt`.


## Usage
The tool's use is straightforward:

```
python3 parse_clamp/ [--i <OPTIONAL TARGET DIR>]
```

By default the tool will parse documents in the path `annotation_tools/parse_clamp/input_data/`.
