# backuper

backup config tool for db mysqldump, mongodump, pg_dump


## install 

require python2, pip

> pip install backuper


## config

- edit /etc/backuper.conf 

- add database config files to /etc/backuper/databases

- add cron task 

file /etc/crontab

> 10 1    * * *   root    /usr/local/bin/backuper -c /etc/backuper