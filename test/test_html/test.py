# 测试案例
import json
from unittest import TestCase

from config_schema import RESULT
from properpy import ModuleTag, Parser, import_config, parse_config


class TestHtml(TestCase):

    def testEvalutor(self):
        # 初始化解析器
        parser = Parser()

        parser.register_builtin_module(ModuleTag.NORMAL)
        # 注册普通函数
        parser.register_module("config_schema", "utils")
        with open("./config.proper.py", 'r') as file:
            test_code = file.read()
        print(test_code)
        print("==>result")
        result = parser.parse(test_code)
        print(json.dumps(result, indent=2))

    def testParseConfig(self):
        file_path = "config.proper.py"
        result = parse_config(
            file_path,
            ["config_schema", "utils"],
            [ModuleTag.NORMAL]
        )
        print(result)

    def testImportConfig(self):
        module_name = "config_proper"
        file_path = "config.proper.py"
        module = import_config(file_path,module_name)
        print(module.test)
        print(RESULT)

