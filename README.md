# ProperPy - Declarative Configuration Using *Python* Itself

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

**ProperPy** 是一个基于 Python 的声明式配置解析工具与结构化数据生成工具，融合了组件化开发思想与 Python 原生语法，提供：

- 定义文件（`schema.py`）—— 如JSON Schema
  - 🧩 **React/Compose 风格的组件化配置构建**
  - 🔒 **Pydantic 约束支持**
- 配置文件（`.proper.py`）—— 如JSON/TOML/YAML
  - 🐍 **纯 Python 语法实现 DSL**
  - ⚙️ **声明式配置语法**
  - ✍ **基于 Python 的书写时IDE类型提示**
- 解析配置 —— 如GSON
  - 🛡️ **动态依赖解析与类型安全**


## 快速开始

### 安装
```bash
pip install properpy
```

### 基本使用

#### 定义文件编写 (`config_schema.py`)

定义文件指的是定义配置项的数目、配置项的类型的文件。通常用于验证配置项的合法性，并提供书写时的类型提示。
ProperPy提供了两个装饰器用于帮助构建定义文件。
1. `component`装饰器。将用于验证参数的函数包装成可以支持输入各种字典、子组件的组件函数。
2. `config_wraper(RECEIVER)`装饰器工厂。同上。

被这两个装饰器包装后的函数称为**组件**，组件是一系列进行参数校验的函数。组件将返回一个表示组件结构的字典。对于`config_wraper`来说，RECEIVER如果是字典，则将结果更新进RECEIVER；如果是函数，则将结果作为参数调用这个函数。

根据传入组件的参数，结果字典的内容如下。传入组件的位置参数如果是字典，且含有`tag`键名，则作为子组件；如果不含`tag`键名，则合并到结果字典；传入的参数如果是关键字参数，则合并到结果字典。
  - 'tag': 标签名（组件的函数名）
  - 'children': 子组件
  - ...attribute: 关键字参数解析为字典的属性

以下示例定义了两个组件以及一个结果接收组件。

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

#### 配置文件编写 (`config.proper.py`)

配置文件指的是，根据定义文件提供的配置项信息，需要用户进行配置的文件。
ProperPy的配置文件后缀名请使用`.proper.py`。

ProperPy提供了`attrs`函数帮助进行配置项的书写。

`attrs`函数接收任意位置参数（字典类型）和关键字参数，并将它们合并为一个字典。主要用于帮助将关键字书写形式转为字典书写形式。

以下示例演示了如何调用结果包装组件，并通过组件搭建的形式构建配置文件。
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

#### 配置解析

ProperPy提供了两种解析配置的方式，并提供了相应的函数。

##### 通过导入进行解析
这种方式使用时，需要在定义文件中提供接收函数或者接收字典，并使用`config_wrapper`包装组件。如上面代码中的`RESULT`。

配置文件中的全局变量需要通过导入后的模块引用到。

`import_config`：动态导入某路径下的模块，并命名为`module_name`
- 参数：
  - `file_path:str`：导入的配置文件的路径
  - `module_name:str`：模块命名，可以不填（因为配置文件名包含不合法的`.proper`，所以会自动将其替换为`_`）
- 返回值`:ModuleType`

示例代码：

```python
from properpy import import_config
from config_schema import RESULT

module = import_config("path/to/config.proper.py")
print(json.dumps(RESULT, indent=2))
# module.other 用于引用全局变量other
```
输出:
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


##### 通过解析器进行解析

这种方式将整个文件进行静态分析，分析后再在沙箱内进行代码的动态执行，因此需要提供沙箱支持的模块列表。

这种方式全局变量将被加入到解析结果字典中。

`parse_config`：
- 参数：
  - `file_path_or_code:str|PathLike[str]|PathLike[bytes]`：配置文件路径或配置文件代码
  - `supported_modules:list[str]`：支持的模块列表
  - `supported_builtin_modules:list[ModuleTag]`：支持的Python内置模块类型
    - `ModuleTag.MONITOR`：需要进行行为监控的内置模块
    - `ModuleTag.NORMAL`：常规内置模块
    - `ModuleTag.RISK`：包含危险行为的内置模块
    - `ModuleTag.BLOCKED`：应被禁止解析的内置模块
  - `module_paths:list[str]`： 模块的搜索路径， 默认为空
- 返回值`:dict`：解析结果

示例代码：

```python
from properpy import parse_config, ModuleTag

result = parse_config("path/to/config.proper.py", ["config_schema"], [ModuleTag.NORMAL])
print(json.dumps(result, indent=2))
```

输出:
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

## 贡献指南

包管理工具使用[uv](https://docs.astral.sh/uv/)

```bash
# 开发环境设置
git clone https://github.com/yourusername/properpy.git
cd properpy
uv install
```

