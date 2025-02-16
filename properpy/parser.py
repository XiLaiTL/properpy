import ast
import importlib
import sys
from contextlib import contextmanager
from types import ModuleType

from properpy.module_guard import get_module_by_level, ModuleTag


class Parser:
    def __init__(self, module_paths:list[str]=None):
        """
        :param module_paths: A list of additional paths to search for modules during parsing. Defaults to None.
        """
        self.module_paths = module_paths or ["."]  # 添加模块搜索路径
        self.sandbox = ModuleType("__sandbox__")  # 安全沙箱环境
        self.function_registry = {}  # 存储普通函数的注册信息
        self.module_registry = set()  # 白名单
        self.module_registry.add("properpy")
        self.module_registry.add("pydantic")

    def _preload_modules(self):
        """预加载必要模块"""
        for mod in self.module_registry:
            try:
                module = importlib.import_module(mod)
                self.sandbox.__dict__.update(module.__dict__)
            except ImportError:
                pass

    def _setup_import_hook(self):
        """自定义导入处理"""
        """准备安全沙箱环境"""
        # 阻止访问危险属性，置为None
        blocked = {k: None for k in dir(__builtins__) if not k.islower() }
        builtins = {
            '__import__': self._safe_importer,
            **blocked,
        }
        self.sandbox.__dict__["__builtins__"].update(builtins)

    def _safe_importer(self, name, globals=None, locals=None, fromlist=(), level=0):
        """安全导入处理器"""
        if name not in self.module_registry:
            raise ImportError(f"Module {name} is not allowed")

        # 使用上下文管理器确保路径安全
        with temporary_sys_path(self.module_paths):
            module = importlib.import_module(name)
            # 仅注入白名单中的符号
            # allowed_symbols = {'safe_function', 'safe_class'}
            # for symbol in allowed_symbols:
            #     if hasattr(module, symbol):
            #         self.sandbox.__dict__[symbol] = getattr(module, symbol)
            self.sandbox.__dict__.update(module.__dict__)
            return module


    def register_var(self, name, func):
        """
        Registers a regular function or variable into the sandbox environment.

        :param name: The name under which the function or variable will be registered in the sandbox.
        :param func: The callable object (function) or variable to be registered.
        """
        setattr(self.sandbox, name, func)
        if callable(func):
            self.function_registry[name] = func

    def register_module(self, *name:str):
        """
        Registers one or more module names into the module registry.

        :param name: Variable-length argument list of module names to be registered.
        :type name: str
        """
        for _name in name:
            self.module_registry.add(_name)


    def register_builtin_module(self,*tag:ModuleTag):
        """
        Registers one or more built-in modules based on the provided `ModuleTag` enumeration values.

        :param tag: Variable-length argument list of `ModuleTag` values representing built-in modules.
        """
        for tag_ in tag:
            self.module_registry.update(get_module_by_level(tag_))


    def parse(self, code: str) -> dict:
        """
        Parses the provided Python code string into a structured dictionary representation in the sandbox.

        :param code: The Python code string to be parsed.
        :return: A dictionary representing the parsed structure of the code.
        """
        # 预处理：加载依赖模块
        self._preload_modules()
        self._setup_import_hook()

        # 注册函数
        self._prepare_sandbox()

        # 解析组件结构
        return self._parse_ast(ast.parse(code))


    def _prepare_sandbox(self):
        self.sandbox.__dict__.update({
            **self.function_registry
        })

    def _parse_ast(self, tree: ast.AST) -> dict:
        """解析AST结构"""
        children = []
        attributes = {}

        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                self._safe_importer(node.module)
            elif isinstance(node, ast.Assign):
                parsed = self._parse_value(node.value)
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        attributes[var_name] = parsed
            elif isinstance(node, ast.Expr):
                parsed = self._parse_value(node.value)
                if isinstance(parsed,dict):
                    if 'tag' in parsed:
                        children.append(parsed)
                    else:
                        attributes.update(parsed)
                elif parsed is not None:
                    children.append(parsed)

        result = {
            'children': children,
            **attributes
        }
        return result

    def _parse_value(self, node) -> any:
        """解析值节点"""
        try:
            return ast.literal_eval(node)
        except Exception as e:
            """直接求值方案"""
            try:
                # 编译为表达式
                expr = ast.Expression(node)
                code = compile(expr, '<string>', 'eval')

                # 在沙箱中执行
                return eval(code, self.sandbox.__dict__)
            except Exception as e:
                return f"<Evaluation Error: {str(e)}>"

@contextmanager
def temporary_sys_path(paths):
    original_sys_path = sys.path.copy()
    sys.path.extend(paths)
    try:
        yield
    finally:
        sys.path = original_sys_path