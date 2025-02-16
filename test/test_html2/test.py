import json
from unittest import TestCase


class TestHtml2(TestCase):

    def testEvalutor(self):
        from properpy import import_config
        from config_schema import RESULT

        module = import_config("config.proper.py")
        print(json.dumps(RESULT, indent=2))

    def testDirect(self):
        from properpy import parse_config, ModuleTag

        result = parse_config("config.proper.py", ["config_schema"], [ModuleTag.NORMAL])
        print(json.dumps(result, indent=2))