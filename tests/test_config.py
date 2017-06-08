import ConfigParser
import unittest

from backuper import config
from os import path


class GetListFromConfigValueTest(unittest.TestCase):
    def test_without_spaces(self):
        self.assertListEqual(['tb_1', 'tb2'], config.get_list_from_config_value('tb_1,tb2'))

    def test_with_spaces(self):
        self.assertListEqual(['tb_1', 'tb_654'], config.get_list_from_config_value('tb_1,   tb_654  '))


class ConvertConfigItemsToDict(unittest.TestCase):
    items = [
        ('key', 'value1'),
        ('iter_field', 'iter_val_1,  iter_val_2  ,iter_val_3'),
        ('key2', 'val2'),
        ('iter_field_2', 'simple_val'),
    ]

    def test_without_iterable_fields(self):
        self.assertDictEqual(
            {
                'key': 'value1',
                'iter_field': 'iter_val_1,  iter_val_2  ,iter_val_3',
                'key2': 'val2',
                'iter_field_2': 'simple_val',
            },
            config.convert_config_items_to_dict(self.items)
        )

    def test_iterable_fields(self):
        self.assertDictEqual(
            {
                'key': 'value1',
                'iter_field': ['iter_val_1', 'iter_val_2', 'iter_val_3', ],
                'key2': 'val2',
                'iter_field_2': ['simple_val', ],
            },
            config.convert_config_items_to_dict(self.items, ['iter_field', 'iter_field_2', ])
        )


class FtpConfigKeeperTest(unittest.TestCase):
    ftp_config_keeper = None

    def setUp(self):
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(path.join(path.dirname(__file__), 'data', 'test_backuper.conf'))
        self.ftp_config_keeper = config.FtpConfigKeeper(config_parser)

    def test_min_with_extend(self):
        self.assertDictEqual(
            {
                'extends': 'full_ftp_config',
                'user': 'pbx',
                'host': '192.168.123.113',
                'password': 'Pw5LpPw5Lp',
                'directory': 'test_dir',
            },
            self.ftp_config_keeper.get_full_config({
                'extends': 'full_ftp_config',
                'directory': 'test_dir'
            })
        )

    def test_without_extend(self):
        self.assertDictEqual(
            {
                'directory': 'test_dir',
            },
            self.ftp_config_keeper.get_full_config({
                'directory': 'test_dir'
            })
        )
