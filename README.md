# backuper

backup tool for db mysqldump, mongodump, pg_dump

- backup databases: mysql, mongodb, postgresql

- move backup to ftp

- send notification to email

- use one conf file per database in ini-format 


## install 

require python2, pip

> pip install backuper


## config

- edit /etc/backuper.conf 

- add database config files to /etc/backuper/databases

- add cron task to /etc/crontab

> 10 1    * * *   root    /usr/local/bin/backuper -c /etc/backuper