from unittest import TestCase

from properpy import attrs


class TestLibrary(TestCase):
    def testAttrs(self):
        # 示例 1: 纯关键字参数
        self.assertEqual(attrs(title="Test"),{"title": "Test"})

        # 示例 2: 纯字典位置参数
        self.assertEqual(attrs({"title": "Test"}),{"title": "Test"})

        # 示例 3: 混合字典位置参数和关键字参数
        self.assertEqual(attrs({"title": "Test"}, other="None"),{"title": "Test", "other": "None"})

        # 示例 4: 多个字典位置参数合并
        self.assertEqual(attrs({"a": 1}, {"b": 2}, c=3),{"a": 1, "b": 2, "c": 3})

        # 示例 5: 关键字参数覆盖位置参数
        self.assertEqual(attrs({"a": 1}, a=2),{"a": 2})

        # 错误示例: 传递非字典位置参数
        self.assertEqual(attrs(123),{}) # 抛出 TypeError
        self.assertEqual(attrs({"a": 1}, "invalid"),{"a": 1}) # 抛出 TypeError

