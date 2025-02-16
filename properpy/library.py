import sys
from functools import wraps
from importlib.util import module_from_spec, spec_from_file_location
from inspect import signature, Parameter
from os import PathLike
from os.path import isfile
from re import sub, search
from types import ModuleType
from typing import Union, Callable, Any

from properpy.parser import Parser
from properpy.module_guard import ModuleTag


def component(func:Callable):
    """
    Decorator. Marks the input function as a component and automatically filters valid parameters to pass into
    the decorated function, generating a component structure based on the parameters passed to the component.

    Dictionary structure returned by the component:
        - 'tag': The name of the component (i.e., the name of the decorated function).
        - 'children': A list of sub-components of the component (positional arguments passed in).
        - ...attribute: Keyword arguments passed in.

    Examples::

        @component
        def my_component(name, age=None, extra=None):
            return {'extra_data': extra}

        result = my_component("Alice", age=30, extra={'key': 'value'})

        # Result

        {
            'tag': 'my_component',
            'children': ['Alice'],
            'age': 30,
            'extra_data': {'key': 'value'}
        }

    :param func: The function to be decorated.
    :return: Returns a wrapped function that returns a dictionary representing the component structure.
    """
    """
        1. 获取被装饰函数的参数签名，并提取位置参数名称列表。
        2. 包装函数中，处理传入的位置参数和关键字参数：
           - 如果位置参数与关键字参数冲突，优先使用关键字参数。
           - 筛选合法参数并调用原函数。
        3. 构建组件结构：
           - 位置参数：如果参数是字典且包含 'tag' 键，则将其视为子组件；否则，更新属性或直接添加到子元素列表。
           - 关键字参数：更新组件的属性。
        4. 合并原函数的返回值：
           - 如果返回值是字典，则将其合并到组件结构中。
           - 如果返回值不是字典且不为 None，则将其作为子元素添加。
    """
    func._is_component = True

    # 获取原函数的参数签名
    sig = signature(func)
    parameters = sig.parameters

    # 获取位置参数名称列表
    pos_param_names = [name for name, param in parameters.items() if
                       param.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)]

    @wraps(func)
    def wrapper(*args, **kwargs):

        # 初始化最终的位置参数和关键字参数
        final_args = []
        final_kwargs = {}

        # 处理位置参数
        seen_args = set()
        arg_index = 0
        for i, arg in enumerate(args):
            if arg_index < len(pos_param_names):
                name = pos_param_names[arg_index]
                if name not in kwargs:
                    final_args.append(arg)
                    seen_args.add(name)
                else:
                    # 如果位置参数和关键字参数冲突，忽略位置参数
                    pass
                arg_index += 1

        # 处理关键字参数
        for name, value in kwargs.items():
            if name in parameters:
                final_kwargs[name] = value
        # 如果原函数没有 **kwargs，忽略剩余的关键字参数
        func_result = func(*final_args, **final_kwargs)
        # 处理所有位置参数和关键字参数生成组件结构
        children = []
        attributes = {}

        # 处理位置参数
        for arg in args:
            if isinstance(arg, dict):
                if 'tag' in arg:
                    children.append(arg)
                else:
                    attributes.update(arg)
            else:
                children.append(arg)

        # 处理关键字参数
        attributes.update(kwargs)
        # 构建结果字典
        result = {
            'tag': func.__name__,
            'children': children,
            **attributes
        }

        # 合并原函数的结果
        if isinstance(func_result,dict):
            result.update(func_result)
        elif func_result is not None:
            result['children'].append(func_result)
        return result

    return wrapper

def config_wrapper(receiver:Union[dict,Callable[[dict],Any]]):
    """
    Decorator. Marks the input function as a component, automatically filters valid parameters to pass into
    the decorated function, generates a component structure based on the parameters passed to the component,
    and passes the result of the component to a specified receiver.

    Dictionary structure returned by the component:
        - 'tag': The name of the component (i.e., the name of the decorated function).
        - 'children': A list of sub-components of the component (positional arguments passed in).
        - ...attribute: Keyword arguments passed in.

    Example 1: Using a dictionary as the receiver::

        data = {}

        @config_wrapper(data)
        def example_component():
            return {"key": "value"}

        example_component()
        print(data)  # Output: {'key': 'value'}

    Example 2: Using a function as the receiver::

        def process_result(result: dict):
            print("Processed Result:", result)

        @config_wrapper(process_result)
        def example_component():
            return {"key": "value"}

        example_component()  # Output: Processed Result: {'key': 'value'}

    :param receiver: The object that receives the result of the component.
        - Dictionary: If `receiver` is a dictionary, the component result is updated into this dictionary using
            the `update` method.
        - Callable: If `receiver` is a function, the component result is passed as an argument to this function.
    :return: Returns a wrapped function that returns a dictionary representing the component structure.
    """
    def component_wrapper(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            first_func = component(func)
            result = first_func(*args,**kwargs)
            # 根据 receiver 类型执行不同操作
            if isinstance(receiver, dict):
                receiver.update(result)  # 如果是字典，更新字典
            elif callable(receiver):  # 如果是函数，调用函数并传入 result
                receiver(result)
            return result
        return wrapper
    return component_wrapper

def attrs(*args, **kwargs):
    """
    Merge dictionary positional arguments and keyword arguments to generate an attribute dictionary.

    This function processes all positional arguments, expecting them to be dictionaries. It then updates the
    resulting dictionary with keyword arguments, where keyword arguments will override keys with the same name.


    Example 1: Merging dictionaries with keyword arguments::

        result = attrs({"a": 1, "b": 2}, {"b": 3, "c": 4}, a=5, d=6)
        print(result)  # Output: {'a': 5, 'b': 3, 'c': 4, 'd': 6}

    Example 2: Ignoring non-dictionary positional arguments::

        result = attrs("invalid", {"a": 1}, b=2)
        print(result)  # Output: {'a': 1, 'b': 2}

    :param args: Variable-length positional arguments. Only dictionaries are accepted; non-dictionary arguments are ignored.
    :param kwargs: Keyword arguments that will be merged into the resulting dictionary. If a key in ``kwargs`` conflicts with a key from ``args``, the value from ``kwargs`` takes precedence.
    :return: A dictionary containing the merged attributes.

    """
    result = {}
    # 处理所有位置参数（仅字典类型）
    for arg in args:
        if not isinstance(arg, dict):
            # raise TypeError("Positional arguments must be dictionaries")
            continue
        result.update(arg)
    # 合并关键字参数（覆盖同名键）
    result.update(kwargs)
    return result

def to_valid_module_name(module_name:str,default_name:str = "config_file")->str:
    """
    Converts a given string into a valid Python module name by replacing invalid characters and ensuring
    the name adheres to Python's naming rules.


    Conversion Rules:
        1. If the input string contains no valid characters (letters, digits, or underscores), the function
           returns the `default_name`.
        2. Replaces all invalid characters with underscores (`_`) and merges consecutive underscores into one.
        3. Ensures the resulting name does not start with a digit. If it does, a leading underscore is added.

    Example 1: Validating and cleaning a module name::

        result = to_valid_module_name("my-module_name1")
        print(result)  # Output: my_module_name1

    Example 2: Handling names with invalid starting characters::

        result = to_valid_module_name("1invalid_name")
        print(result)  # Output: _1invalid_name

    Example 3: Handling strings with no valid characters::
        result = to_valid_module_name("!@#$%^&*()")
        print(result)  # Output: config_file

    :param module_name: The original string to be converted into a valid module name.
    :param default_name: The fallback name to use if the original string contains no valid characters. Defaults to "config_file".
    :return: A valid Python module name derived from the input string.
    """

    # 检查原字符串是否全不合法
    if not search(r'[a-zA-Z0-9_]', module_name):
        return default_name

    # 替换非法字符为下划线并合并连续下划线
    module_name = sub(r'[^a-zA-Z0-9_]', '_', module_name)
    module_name = sub(r'_+', '_', module_name)

    # 确保名称不以数字开头
    if not module_name[0].isalpha() and module_name[0] != '_':
        module_name = '_' + module_name

    return module_name

def import_config(file_path:str,module_name:str="config_file")->ModuleType:
    """
    Dynamically imports a Python configuration file as a module.

    This function takes the path to a Python file and optionally a module name, validates the module name,
    and dynamically loads the file as a Python module. The loaded module is registered in `sys.modules`
    for future reference.

    Example: Importing a configuration file as a module::

        config_module = import_config("path/to/config.proper.py", module_name="my_config")

        # Accessing attributes from the imported module
        print(config_module.some_variable)  # Assuming 'some_variable' is defined in the config file

    :param file_path: The absolute or relative path to the Python configuration file to be imported.
    :param module_name: The name under which the module will be registered. It must follow Python's naming
                        rules for valid module names. Defaults to "config_file".
    :return: The dynamically loaded Python module object.
    """
    module_name = to_valid_module_name(module_name)
    # 动态加载模块
    spec = spec_from_file_location(module_name, file_path)
    module = module_from_spec(spec)
    # 注册到 sys.modules
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module  # 返回模块对象

def parse_config(
        file_path_or_code:str|PathLike[str]|PathLike[bytes],
        supported_modules:list[str] = None,
        supported_builtin_modules:list[ModuleTag] = None,
        module_paths:list[str] = None
                 )->dict:
    """
    Parses a configuration file or code string and extracts relevant information using a parser.

    This function initializes a parser, optionally registers supported modules and built-in modules,
    reads the configuration file (if provided as a path), and parses the code to return a dictionary
    containing the extracted information.

    Notes:

    - If `file_path_or_code` is a file path, it must exist and be readable.
    - If `file_path_or_code` is a code string, it should contain valid Python code.

    Example 1: Parsing a configuration file::
        config_data = parse_config("config.py",
                                   supported_modules=["my_module"],
                                   supported_builtin_modules=[ModuleTag.NORMAL])
        print(config_data)

    Example 2: Parsing a code string::
        code_string = "x = 42; y = 'hello'"
        config_data = parse_config(code_string)
        print(config_data)

    :param file_path_or_code: The configuration file path (as a string or path-like object) or the code
                              string to be parsed. If a file path is provided, it must point to an existing
                              file.
    :param supported_modules: A list of module names to register with the parser. These modules will be
                              recognized during parsing. Defaults to None.
    :param supported_builtin_modules: A list of built-in module tags to register with the parser. These
                                      modules are predefined and available for use during parsing. Defaults
                                      to None.
    :param module_paths: A list of additional paths to search for modules during parsing. Defaults to None.
    :return: A dictionary containing the parsed configuration data.
    """
    parser = Parser(module_paths)
    if supported_modules is not None:
        parser.register_module(*supported_modules)
    if supported_builtin_modules is not None:
        parser.register_builtin_module(*supported_builtin_modules)
    if (isinstance(file_path_or_code, str) or isinstance(file_path_or_code,PathLike))and isfile(file_path_or_code):
        with open(file_path_or_code, 'r') as file:
            test_code = file.read()
    else:
        test_code = file_path_or_code
    return parser.parse(test_code)
