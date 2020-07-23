#! /usr/bin/bash

scp boot.sh config.py TEMP_API.py temperature_db.db apiuser@192.168.0.102:~/src
scp app/__init__.py app/apiexception.py app/db_sqlite.py apiuser@192.168.0.102:~/src/app
scp app/eventpool.py app/handlers.py app/mitigate.py app/routes.py apiuser@192.168.0.102:~/src/app
