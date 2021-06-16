import unittest
from typing import Any, List

from config_builder.generator.stemma_conf import StemmaConfGenerator


class SingleFieldConf(StemmaConfGenerator):
    ENV = 'latest'


class ListFieldConfig(StemmaConfGenerator):
    ENV = 'latest'
    SERIES: List[Any] = []


class NestedSubConf(StemmaConfGenerator):
    INSIDE = 'this'


class NestedConf(StemmaConfGenerator):
    ABOOL = True
    ASTRING = 'false'
    NESTED = NestedSubConf()
    ALIST: List[Any] = []


class TestStemmaConfGenerator(unittest.TestCase):

    def setUp(self) -> None:
        self.testConf = SingleFieldConf(ENV='new')
        self.nestedConf = NestedConf(
            ABOOL=False,
            ASTRING='true',
            NESTED=NestedSubConf(),
            ALIST=[self.testConf, self.testConf]
        )
        self.listConf = ListFieldConfig(
            ENV='new',
            SERIES=['one', 'two']
        )

    def test_generator_create(self) -> None:
        self.assertEqual(self.testConf.ENV, 'new')
        with self.assertRaisesRegex(Exception, 'does not exist'):
            SingleFieldConf(
                ENV='new',
                INVALID='other'
            )

    def test_flatten(self) -> None:
        self.assertEqual([1, 3, 7, 9, 11], list(StemmaConfGenerator._flatten([1, [3], [7, [9, 11]]])))

    def test_is_conf_item(self) -> None:
        self.assertTrue(self.testConf._is_conf_item('ENV'))
        self.assertFalse(self.testConf._is_conf_item('_ENV'))
        self.assertFalse(self.testConf._is_conf_item('build_yaml'))

    def test_build_yaml(self) -> None:
        self.assertEqual({'ENV': 'new'}, self.testConf.build_yaml())
        self.assertEqual({'ENV': 'new', 'SERIES': ['one', 'two']}, self.listConf.build_yaml())
        self.assertEqual({'ABOOL': False,
                          'ASTRING': 'true',
                          'NESTED': {'INSIDE': 'this'},
                          'ALIST': [{'ENV': 'new'}, {'ENV': 'new'}]}, self.nestedConf.build_yaml())

    def test_build_env(self) -> None:
        self.assertEqual([{'key': 'ENV', 'value': 'new'}], self.testConf.build_env())

        self.assertEqual([{'key': 'ENV', 'value': 'new'}], self.listConf.build_env())
        self.assertEqual([{'key': 'ABOOL', 'value': 'False'},
                          {'key': 'ASTRING', 'value': 'true'},
                          {'key': 'INSIDE', 'value': 'this'}], self.nestedConf.build_env())
