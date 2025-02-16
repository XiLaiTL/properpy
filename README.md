# ProperPy - Declarative Configuration Using *Python* Itself

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

[👉中文](./README.zh.md)

**ProperPy** is a Python-based declarative configuration parsing tool and structured data generation tool, integrating component-based development ideas with Python's native syntax, offering:

- Definition file (`schema.py`) — like JSON Schema
  - 🧩 **React/Compose style component-based configuration building**
  - 🔒 **Pydantic constraint support**
- Configuration file (`.proper.py`) — like JSON/TOML/YAML
  - 🐍 **Pure Python syntax to implement DSL**
  - ⚙️ **Declarative configuration syntax**
  - ✍ **IDE type hints based on Python when writing**
- Parsing configuration — like GSON
  - 🛡️ **Dynamic dependency resolution and type safety**

## Quick Start

### Installation
```bash
pip install properpy
```

### Basic Usage

#### Writing Definition File (`config_schema.py`)

The definition file refers to the file that defines the number of configuration items and the types of configuration items. It is usually used to verify the legality of configuration items and provide type hints when writing.
ProperPy provides two decorators to help build definition files.
1. `component` decorator. Wraps the function used to validate parameters into a component function that can support input of various dictionaries and subcomponents.
2. `config_wraper(RECEIVER)` decorator factory. Same as above.

Functions wrapped by these two decorators are called **components**, which are a series of functions for parameter validation. Components will return a dictionary representing the component structure. For `config_wraper`, if RECEIVER is a dictionary, the result will be updated into RECEIVER; if it is a function, the result will be passed as a parameter to call this function.

According to the parameters passed to the component, the content of the result dictionary is as follows. If the positional parameters passed to the component are dictionaries and contain the `tag` key, they are treated as subcomponents; if they do not contain the `tag` key, they are merged into the result dictionary; if the parameters are keyword arguments, they are merged into the result dictionary.
  - 'tag': tag name (function name of the component)
  - 'children': subcomponents
  - ...attribute: keyword arguments parsed as dictionary attributes

The following example defines two components and a result receiving component.

```python
from properpy import component, config_wrapper

@component
def html(title: str, class_: str = ""):
    pass

@component
def div(content: str, style: dict = None):
    pass

RESULT = {}
@config_wrapper(RESULT)
def define_config(html_component, title: str):
    pass
```

#### Writing Configuration File (`config.proper.py`)

The configuration file refers to the file that users need to configure based on the configuration item information provided by the definition file.
Please use `.proper.py` as the suffix for ProperPy configuration files.

ProperPy provides the `attrs` function to help write configuration items.

The `attrs` function accepts any positional parameters (dictionary type) and keyword arguments, and merges them into a dictionary. It is mainly used to help convert keyword writing forms into dictionary writing forms.

The following example demonstrates how to call the result wrapper component and build the configuration file through component construction.
```python
from config_schema import html, div, define_config
from properpy import attrs

other = "wrong"
define_config(
    html(
        div(
            attrs(style={"color": "red"}),
            "Dynamic content"
        ),
        class_="container"
    ),
    title="My App"
)
```

#### Parsing Configuration

ProperPy provides two ways to parse configurations and corresponding functions.

##### Parsing by Import
When using this method, you need to provide a receiving function or receiving dictionary in the definition file, and use `config_wrapper` to wrap the component. As in the `RESULT` in the above code.

Global variables in the configuration file need to be referenced through the imported module.

`import_config`: Dynamically import the module under a certain path and name it `module_name`
- Parameters:
  - `file_path:str`: Path of the configuration file to import
  - `module_name:str`: Module naming, can be left blank (because the configuration file name contains illegal `.proper`, it will automatically be replaced with `_`)
- Return value`:ModuleType`

Example code:

```python
from properpy import import_config
from config_schema import RESULT

module = import_config("path/to/config.proper.py")
print(json.dumps(RESULT, indent=2))
# module.other is used to reference the global variable other
```
Output:
```json
{
  "tag": "define_config",
  "children": [
    {
      "tag": "html",
      "children": [
        {
          "tag": "div",
          "children": [
            "Dynamic content"
          ],
          "style": {
            "color": "red"
          }
        }
      ],
      "class_": "container"
    }
  ],
  "title": "My App"
}
```


##### Parsing by Parser

This method performs static analysis on the entire file, and then dynamically executes the code in a sandbox after analysis, so a list of modules supported by the sandbox needs to be provided.

In this method, global variables will be added to the parsing result dictionary.

`parse_config`:
- Parameters:
  - `file_path_or_code:str|PathLike[str]|PathLike[bytes]`: Configuration file path or configuration file code
  - `supported_modules:list[str]`: List of supported modules
  - `supported_builtin_modules:list[ModuleTag]`: List of supported Python built-in module types
    - `ModuleTag.MONITOR`: Built-in modules that require behavior monitoring
    - `ModuleTag.NORMAL`: Regular built-in modules
    - `ModuleTag.RISK`: Built-in modules containing risky behaviors
    - `ModuleTag.BLOCKED`: Built-in modules that should be blocked from parsing
  - `module_paths:list[str]`: Module search paths, default is empty
- Return value`:dict`: Parsing result

Example code:

```python
from properpy import parse_config, ModuleTag

result = parse_config("path/to/config.proper.py", ["config_schema"], [ModuleTag.NORMAL])
print(json.dumps(result, indent=2))
```

Output:
```json
{
  "children": [
    {
      "tag": "define_config",
      "children": [
        {
          "tag": "html",
          "children": [
            {
              "tag": "div",
              "children": [
                "Dynamic content"
              ],
              "style": {
                "color": "red"
              }
            }
          ],
          "class_": "container"
        }
      ],
      "title": "My App"
    }
  ],
  "other": "wrong"
}
```

## Contribution Guide

Package management tool uses [uv](https://docs.astral.sh/uv/)

```bash
# Development environment setup
git clone https://github.com/yourusername/properpy.git
cd properpy
uv install
```