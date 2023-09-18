FROM python:2.7.18

RUN apt-get update && apt-get install -y python-pip 

RUN apt-get install -y default-mysql-client

RUN apt-get install -y ftp

RUN pip install backuper==0.1.4

RUN apt-get install -y gnupg

RUN curl -fsSL https://pgp.mongodb.com/server-6.0.asc | \
   gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg \
   --dearmor

RUN echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list

RUN apt-get --allow-releaseinfo-change update

RUN apt-get update && apt-get install -y mongodb-org-tools htop

RUN apt-get install -y postgresql-client postgresql-client-common libpq-dev
