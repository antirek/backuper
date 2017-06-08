# coding: utf-8

import datetime
import logging
import smtplib
from email.mime import text as mime_text

import abc
import os
from os import path

DEFAULT_LOCAL_BACKUP_DIR_PATH = '/var/tmp/'


class DatabaseBackuper:
    __metaclass__ = abc.ABCMeta

    def __init__(self, db_config, ftp_config, logger=None):
        """

        :type db_config: dict[str,str]
        :type ftp_config: dict[str,str]
        :type logger: logging.Logger
        """
        self.db_config = db_config
        self._ftp_config = ftp_config
        self.logger = logger or logging.getLogger('backuper.database')
        self._backup_file_name = None
        self._temp_backup_file_path = None

    def backup(self):
        self.logger.info('Database backup started')
        self._backup_file_name = self._generate_backup_file_name()
        self._temp_backup_file_path = path.join(DEFAULT_LOCAL_BACKUP_DIR_PATH, self._backup_file_name)

        self.before_do_backup()
        self._do_backup()
        self.after_do_backup()
        self._copy_backup_file_to_ftp()
        os.system('rm ' + self._temp_backup_file_path)
        self.logger.info('Backup file deleted')
        self.logger.info('Database backup finished')

    def _generate_backup_file_name(self):
        name = '{}-{}'.format(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), self.db_config['name'])
        if 'type' in self.db_config:
            name += '-' + self.db_config['type']
        name += '.{}.gz'.format(self.get_backup_file_extension())
        return name

    @abc.abstractmethod
    def get_backup_file_extension(self):
        pass

    @abc.abstractmethod
    def before_do_backup(self):
        pass

    def _do_backup(self):
        os.system(self.get_backup_command() + ' | gzip > ' + self._temp_backup_file_path)
        self.logger.info('Backup file created')

    @abc.abstractmethod
    def get_backup_command(self):
        pass

    @abc.abstractmethod
    def after_do_backup(self):
        pass

    def _copy_backup_file_to_ftp(self):
        ftp = self._ftp_config
        command = 'ftp -n ' + ftp['host'] + ' <<End-Of-Session\n'
        command += 'user ' + ftp['user'] + ' ' + ftp['password'] + '\n'
        command += 'put {} '.format(self._temp_backup_file_path)
        if 'directory' in ftp:
            command += ftp['directory'] + '/'
        command += self._backup_file_name + '\n'
        command += 'bye\n'
        command += 'End-Of-Session\n'
        os.system(command)
        self.logger.info('Backup file copied to FTP')


class MysqlBackuper(DatabaseBackuper):
    def __init__(self, db_config, ftp_config, logger=None):
        super(MysqlBackuper, self).__init__(db_config, ftp_config, logger)

    def get_backup_file_extension(self):
        return 'sql'

    def before_do_backup(self):
        if self.is_replication_enabled():
            self._stop_slave()

    def is_replication_enabled(self):
        return 'replication' in self.db_config

    def _stop_slave(self):
        self._run_db_command('slave stop')
        self.logger.info('Slave stopped')

    def _run_db_command(self, command_text):
        os.system(self.get_command_base_text() + "-e '{}'".format(command_text))

    def get_command_base_text(self):
        command = 'mysql -u' + self.db_config['user'] + ' -p' + self.db_config['password']
        if 'host' in self.db_config:
            command += ' -h' + self.db_config['host']
        if 'port' in self.db_config:
            command += ' -P' + self.db_config['port']
        return command

    def get_backup_command(self):
        command = 'mysqldump -u{} -p{} -h{}'.format(
            self.db_config['user'], self.db_config['password'], self.db_config['host']
        )
        if 'port' in self.db_config:
            command += ' -P' + self.db_config['port']
        if 'where' in self.db_config:
            command += ' --where="' + self.db_config['where'] + '"'
        command += ' ' + self.db_config['name']
        if 'tables' in self.db_config:
            command += ''.join(map(lambda table_name: ' ' + table_name, self.db_config['tables']))
        if 'ignore' in self.db_config:
            command += ''.join(
                map(
                    lambda table_name: ' --ignore-table=' + self.db_config['name'] + '.' + table_name,
                    self.db_config['ignore']
                )
            )
        return command

    def after_do_backup(self):
        if self.is_replication_enabled():
            self._start_slave()

    def _start_slave(self):
        self._run_db_command('slave start')
        self.logger.info('Slave started')


class MongoBackuper(DatabaseBackuper):
    def get_backup_file_extension(self):
        return 'archive'

    def before_do_backup(self):
        pass

    def get_backup_command(self):
        command = 'mongodump --archive --db {}'.format(self.db_config['name'])
        if 'host' in self.db_config:
            command += ' --host {}'.format(self.db_config['host'])
        if 'port' in self.db_config:
            command += ' --port {}'.format(self.db_config['port'])
        return command

    def after_do_backup(self):
        pass


class PostgresqlBackuper(DatabaseBackuper):
    def get_backup_file_extension(self):
        return 'sql'

    def before_do_backup(self):
        pass

    def get_backup_command(self):
        command = 'pg_dump -w --dbname={}'.format(self.get_connection_uri())
        if 'tables' in self.db_config:
            command += ''.join(map(lambda table_name: ' -t {}'.format(table_name), self.db_config['tables']))
        if 'ignore' in self.db_config:
            command += ''.join(map(lambda table_name: ' -T {}'.format(table_name), self.db_config['ignore']))
        return command

    def get_connection_uri(self):
        result = 'postgresql://{}:{}@{}'.format(
            self.db_config['user'],
            self.db_config['password'],
            self.db_config['host']
        )
        if 'port' in self.db_config:
            result += ':' + self.db_config['port']
        result += '/' + self.db_config['name']
        return result

    def after_do_backup(self):
        pass


class EmailSender:
    def __init__(self, smtp_config, logger=None):
        """

        :type smtp_config: dict
        :type logger: logging.Logger
        """
        self._smtp_config = smtp_config
        self._logger = logger or logging.getLogger('backuper.database')

    def set_logger(self, logger):
        self._logger = logger

    def send_message(self, message):
        self._logger.info('Email sending started')
        text = mime_text.MIMEText(message.encode('utf-8'))
        text['Subject'] = self._smtp_config['subject']
        text['From'] = self._smtp_config['sender']
        for email in self._smtp_config['emails']:
            self._send_mime_text_to_email(text, email)
        self._logger.info('Email sending finished')

    def _send_mime_text_to_email(self, text, email):
        """

        :type text: mime_text.MIMEText
        :type email: str
        :return:
        """
        text['To'] = email
        try:
            pass
            connection = smtplib.SMTP(self._smtp_config['host'])
            connection.ehlo()
            connection.starttls()
            connection.ehlo()
            connection.login(self._smtp_config['username'], self._smtp_config['password'])
            connection.sendmail(self._smtp_config['sender'], email, text.as_string())
            connection.quit()
        except smtplib.SMTPException:
            self._logger.exception('Unable to send email to address "{}"'.format(email))


class Backuper:
    def __init__(self, db_config, ftp_config, email_sender, logger):
        """

        :type db_config: dict
        :type ftp_config: dict
        :type email_sender: EmailSender
        :type logger: logging.Logger
        """
        self._db_config = db_config
        self._ftp_config = ftp_config
        self._email_sender = email_sender
        self._logger = logger

    def backup(self):
        try:
            self.get_database_backuper_class()(self._db_config, self._ftp_config, self._logger).backup()
            self._email_sender.set_logger(self._logger)
            self._email_sender.send_message(self.get_email_message())
        except Exception:
            self._logger.exception('Exception occurred during backup')

    def get_database_backuper_class(self):
        return DatabaseBackuperFactory().get_backuper_class(self._db_config.get('type'))

    def get_email_message(self):
        message = u'Осуществлено бэкапирование базы данных {} на хосте {}'.format(
            self._db_config['name'], self._db_config['host']
        )
        if 'port' in self._db_config:
            message += u' порт:' + self._db_config['port']
        message += u'. Бэкап отправлен на ftp по адресу {}@{}'.format(
            self._ftp_config['user'], self._ftp_config['host']
        )
        return message


class DatabaseBackuperFactory:
    def __init__(self):
        pass

    def get_backuper_class(self, db_type):
        if db_type == 'mysql':
            return MysqlBackuper
        elif db_type == 'mongo':
            return MongoBackuper
        elif db_type == 'postgresql':
            return PostgresqlBackuper
        else:
            raise InvalidDatabaseTypeError(db_type)


class InvalidDatabaseTypeError(Exception):
    def __init__(self, db_type, *args, **kwargs):
        message = 'Invalid database type {}'.format(db_type)
        super(InvalidDatabaseTypeError, self).__init__(message, *args, **kwargs)
