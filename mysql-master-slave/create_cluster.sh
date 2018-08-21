#!/bin/bash

/usr/local/bin/docker-compose down
rm -rf ./master/data/*
rm -rf ./slave/data/*
/usr/local/bin/docker-compose build
/usr/local/bin/docker-compose up -d



#export $(grep -v '^#' master/mysql_master.env  | xargs)

#MYSQL_M_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
#MYSQL_M_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
#MYSQL_M_USER=${MYSQL_USER}
#MYSQL_M_PASSWORD=${MYSQL_PASSWORD}
#MYSQL_M_DATABASE=${MYSQL_DATABASE}

#export $(grep -v '^#' slave/mysql_slave.env | xargs)

#MYSQL_S_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
#MYSQL_S_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
#MYSQL_S_USER=${MYSQL_USER}
#MYSQL_S_PASSWORD=${MYSQL_PASSWORD}
#MYSQL_S_DATABASE=${MYSQL_DATABASE}



#export $(grep -v '^#' master/mysql_master.env  | xargs)

MYSQL_M_ROOT_PASSWORD=MyPassword12
MYSQL_M_USER=mydb_user
MYSQL_M_PASSWORD=mydb_pwd
MYSQL_M_DATABASE=mydb

#export $(grep -v '^#' slave/mysql_slave.env | xargs)

MYSQL_S_ROOT_PASSWORD=MyPWD123
MYSQL_S_USER=mydb_slave_user1
MYSQL_S_PASSWORD=mydb_slave_pwd1
MYSQL_S_DATABASE=mydb

until docker exec mysql_master sh -c 'export MYSQL_PWD='${MYSQL_M_ROOT_PASSWORD}'; mysql -u root -e ";"'
do
    echo "Waiting for mysql_master database connection..."
    sleep 4
done

priv_stmt='GRANT REPLICATION SLAVE ON *.* TO "'${MYSQL_S_USER}'"@"%" IDENTIFIED BY "'${MYSQL_S_PASSWORD}'"; FLUSH PRIVILEGES;'
docker exec mysql_master sh -c "export MYSQL_PWD='${MYSQL_M_ROOT_PASSWORD}'; mysql -u root -e '$priv_stmt'"

until /usr/local/bin/docker-compose exec mysql_slave sh -c 'export MYSQL_PWD='${MYSQL_S_ROOT_PASSWORD}'; mysql -u root -e ";"'
do
    echo "Waiting for mysql_slave database connection..."
    sleep 4
done

docker-ip() {
    docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$@"
}

MS_STATUS=`docker exec mysql_master sh -c 'export MYSQL_PWD='${MYSQL_M_ROOT_PASSWORD}'; mysql -u root -e "SHOW MASTER STATUS"'`
CURRENT_LOG=`echo $MS_STATUS | awk '{print $6}'`
CURRENT_POS=`echo $MS_STATUS | awk '{print $7}'`

start_slave_stmt="CHANGE MASTER TO MASTER_HOST='$(docker-ip mysql_master)',MASTER_USER='"${MYSQL_S_USER}"',MASTER_PASSWORD='"${MYSQL_S_PASSWORD}"',MASTER_LOG_FILE='$CURRENT_LOG',MASTER_LOG_POS=$CURRENT_POS; START SLAVE;"
start_slave_cmd='export MYSQL_PWD='${MYSQL_S_ROOT_PASSWORD}'; mysql -u root -e "'
start_slave_cmd+="$start_slave_stmt"
start_slave_cmd+='"'
docker exec mysql_slave sh -c "$start_slave_cmd"

docker exec mysql_slave sh -c "export MYSQL_PWD='${MYSQL_S_ROOT_PASSWORD}'; mysql -u root -e 'SHOW SLAVE STATUS \G'"
