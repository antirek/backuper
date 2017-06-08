import unittest

from backuper import backup


class MysqlBackuperTest(unittest.TestCase):
    min_db_config = {
        'host': 'stub_host',
        'name': 'test_db_min',
        'user': 'test_user_min',
        'password': 'test_pass_min',
    }
    full_db_config = {
        'name': 'test_db',
        'user': 'test_user',
        'host': 'test_host',
        'port': 'test_port',
        'password': 'test_pass',
        'where': 'test where query',
        'tables': ['test_table1', 'test_table2', ],
        'ignore': ['ignore_table_1', 'ignore_table_2', ],
        'replication': 'true',
    }

    def test_get_backup_command_with_min_options(self):
        expected_command = 'mysqldump -utest_user_min -ptest_pass_min -hstub_host test_db_min'
        self.assertEqual(expected_command, backup.MysqlBackuper(self.min_db_config, {}).get_backup_command())

    def test_get_backup_command_with_all_options(self):
        expected_command = ' '.join([
            'mysqldump',
            '-utest_user',
            '-ptest_pass',
            '-htest_host',
            '-Ptest_port',
            '--where="test where query"',
            'test_db',
            'test_table1',
            'test_table2',
            '--ignore-table=test_db.ignore_table_1',
            '--ignore-table=test_db.ignore_table_2',
        ])
        self.assertEqual(expected_command, backup.MysqlBackuper(self.full_db_config, {}).get_backup_command())


class MongoBackuperTest(unittest.TestCase):
    min_db_config = {
        'name': 'test_db_min',
    }
    full_db_config = {
        'name': 'test_db',
        'host': 'test_host',
        'port': 'test_port',
    }

    def test_get_backup_command_with_min_options(self):
        expected_command = 'mongodump --archive --db test_db_min'
        self.assertEqual(expected_command, backup.MongoBackuper(self.min_db_config, {}).get_backup_command())

    def test_get_backup_command_with_all_options(self):
        expected_command = 'mongodump --archive --db test_db --host test_host --port test_port'
        self.assertEqual(expected_command, backup.MongoBackuper(self.full_db_config, {}).get_backup_command())


class PostgresqlBackuperTest(unittest.TestCase):
    min_db_config = {
        'name': 'test_db_min',
        'host': 'stub_host',
        'user': 'test_user_min',
        'password': 'test_pass_min',
    }
    full_db_config = {
        'name': 'test_db',
        'user': 'test_user',
        'password': 'test_pass',
        'host': 'test_host',
        'port': 'test_port',
        'tables': ['test_table1', 'test_table2', ],
        'ignore': ['ignore_table_1', 'ignore_table_2', ],
    }

    def test_get_backup_command_with_min_options(self):
        expected_command = 'pg_dump -w --dbname=postgresql://test_user_min:test_pass_min@stub_host/test_db_min'
        self.assertEqual(expected_command, backup.PostgresqlBackuper(self.min_db_config, {}).get_backup_command())

    def test_get_backup_command_with_all_options(self):
        expected_command = ' '.join([
            'pg_dump',
            '-w',
            '--dbname=postgresql://test_user:test_pass@test_host:test_port/test_db',
            '-t test_table1',
            '-t test_table2',
            '-T ignore_table_1',
            '-T ignore_table_2',
        ])
        self.assertEqual(expected_command, backup.PostgresqlBackuper(self.full_db_config, {}).get_backup_command())


class DatabaseBackuperFactory(unittest.TestCase):
    expected_type_to_class_data = {
        'mysql': backup.MysqlBackuper,
        'mongo': backup.MongoBackuper,
        'postgresql': backup.PostgresqlBackuper,
    }

    def test_get_backuper_class(self):
        for db_type, expected_class in self.expected_type_to_class_data.items():
            self.assertEqual(expected_class, backup.DatabaseBackuperFactory().get_backuper_class(db_type))

    def test_get_backuper_class_raise_exception_for_invalid_type(self):
        self.assertRaises(
            backup.InvalidDatabaseTypeError,
            backup.DatabaseBackuperFactory().get_backuper_class,
            'invalid_db_type'
        )
