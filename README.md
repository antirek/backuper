# backuper

backup tool for db mysqldump, mongodump, pg_dump

- backup databases: mysql, mongodb, postgresql

- move backup to ftp

- send notification to email

- use one conf file per database in ini-format 


## install 

require python2, pip

> pip install backuper

also require mysqldump, mongodump 3.2+, pg_dump

install mysqldump 

> apt-get install mysql-clients

install mongodump 3.2+ 

install pg_dump

> apt-get install postgre-co


## config

- edit /etc/backuper.conf 

- add database config files to /etc/backuper/databases

- add cron task to /etc/crontab

> 10 1    * * *   root    /usr/local/bin/backuper -c /etc/backuper


## restore

mongorestore --host=mongohost --db=mongodb --archive=mongo.archive
