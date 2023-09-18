from distutils.core import setup

setup(
    name='backuper',
    version='0.1.4',
    author='Denis Krashnikov',
    author_email='mgpwanderer@gmail.com',
    maintainer='Sergey Dmitriev',
    maintainer_email='serge.dmitriev@gmail.com',
    packages=['backuper', ],
    url='https://github.com/antirek/backuper',
    download_url='https://github.com/antirek/backuper/archive/0.1.4.tar.gz',
    scripts=['bin/backuper', ],
    data_files=[
        ('/etc/backuper', ['config/backuper.conf']),
        ('/etc/backuper/databases', ['config/databases/mysql.conf']),
    ],
)
