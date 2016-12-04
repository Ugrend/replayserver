#!/bin/bash

#Disable SElinux just to make things easier :(
sed -i 's/^SELINUX=enforcing/SELINUX=permissive/g' /etc/sysconfig/selinux
setenforce 0

sudo yum update -y
sudo yum -y install yum-utils
sudo yum -y groupinstall development
sudo yum install lzma xz-devel wget zlib-devel openssl-devel -y
sudo yum install -y https://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-centos96-9.6-3.noarch.rpm
sudo yum install -y postgresql96-server postgresql96-contrib postgresql96-devel
yum install epel-release -y
yum install erlang -y
yum install https://www.rabbitmq.com/releases/rabbitmq-server/v3.6.5/rabbitmq-server-3.6.5-1.noarch.rpm -y
systemctl start rabbitmq-server
systemctl enable rabbitmq-server

cd /tmp

wget https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz
tar xf Python-3.5.2.tgz
cd Python-3.5.2
./configure
sudo make install
PATH=$PATH:/usr/pgsql-9.6/bin
export PATH
postgresql96-setup initdb
sed -i 's/local   all             all                                     peer/local   all             all                                     trust/' /var/lib/pgsql/9.6/data/pg_hba.conf

systemctl start postgresql-9.6.service
systemctl enable postgresql-9.6.service
/usr/local/bin/pip3 install psycopg2 cherrypy requests hashids Celery cachetools
/usr/bin/psql -U postgres -c 'CREATE DATABASE osu'
/usr/bin/psql -U postgres -d osu -f /vagrant/schema.sql