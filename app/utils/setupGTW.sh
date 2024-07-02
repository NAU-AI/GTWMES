#!/bin/bash

# Update and upgrade the system
sudo apt-get update -y
sudo apt-get upgrade -y
echo "System updated and ugraded with success"

# Install dotenv
sudo apt-get install -y dotenv
echo "Dotenv installed with success"

# Load environment variables from .env file
if [[ -f ".env" ]]; then
    export $(cat .env | xargs)
else
    echo ".env file not found!"
    exit 1
fi

# Retrieve PostgreSQL user and database name from environment variables
pg_user=$PG_USER
pg_password=$PG_PASSWORD
db_name=$DB_NAME

# Install Pip
python -m pip install --upgrade pip
echo "Pip installed"

# Install PostgreSQL
sudo apt install postgresql libpq-dev postgresql-client postgresql-client-common -y
echo "PostgreSQL installed with success!"

# Create DB user
sudo -u postgres psql -c "CREATE USER $pg_user WITH PASSWORD $pg_password;"
echo "$pg_user created with success!"

# Create database
sudo -u postgres psql -c "CREATE DATABASE $db_name OWNER $pg_user;"
echo "Database $db_name created with success!"

# Retrieve version from environment variables
db_version=$DB_VERSION

# Create tables - para o create_all_tables
$sql_file = "./db/persistence/$db_version/create_all_tables.sql"
if [[ -f "$sql_file" ]]; then
    sudo -u postgres psql -d GTW -f "$sql_file"
    echo "Tables created with success!"
else
    echo "SQL file not found!"
    exit 1
fi

# Do changes to the tables if needed because version changed
$sql_folder = "./db/version/$db_version"
if [[ -d "$sql_folder" ]]; then
    for sql_file in "$sql_folder"/*.sql; then
        if [[ -f "$sql_file" ]]; then
            sudo -u postgres psql -d GTW -f "$sql_file"
        fi
    done
    echo "Tables changed with success!"
else
    echo "SQL folder not found!"
fi

# Create virtual environment
python3 -m venv pgadmin4
echo "Virtual environment created successfully"

# Activate the virtual environment
source /home/admin/pgadmin4/bin/activate
echo "Virtual environment activated"

# Install PGadmin4
pip install pgadmin4
echo "pgAdmin4 installed"

# Configure file for virtual environment
$pythonVersion = python --version
SE=' '
arr <<< $pythonVersion
SE='.'
arr2 <<< ${arr[1]}
pathForPython = ${arr[0]} + ${arr2[0]} + "." + ${arr2[1]}
print(pathForPython)
# Retrieve email and password for pgAdmin data from environment variables
pg_email=$PG_EMAIL_ACCESS
pg_password_access=$PG_PASSWORD_ACCESS

echo "PGADMIN_DEFAULT_EMAIL = '$pg_email'" >> /home/admin/pgadmin4/lib/${pathForPython}/site-packages/config_local.py
echo "PGADMIN_DEFAULT_PASSWORD  = '$pg_password'" >> /home/admin/pgadmin4/lib/${pathForPython}/site-packages/config_local.py
echo "LOG_FILE = '/home/admin/pgadmin4/var/log'" >> /home/admin/pgadmin4/lib/${pathForPython}/site-packages/config_local.py
echo "SQLITE_PATH = '/home/admin/pgadmin4/var/pgadmin4.db'" >> /home/admin/pgadmin4/lib/${pathForPython}/site-packages/config_local.py
echo "SESSION_DB_PATH = '/home/admin/pgadmin4/var/sessions'" >> /home/admin/pgadmin4/lib/${pathForPython}/site-packages/config_local.py
echo "STORAGE_DIR = '/home/admin/pgadmin4/var/storage'" >> /home/admin/pgadmin4/lib/${pathForPython}/site-packages/config_local.py

# Install all packages needed for GTW code (não se se preciso, uma vez que a ideia é usar o executável)
#pip install python-dotenv paho-mqtt configparser psycopg2 boto3 
if [[ -f "./package/packages.txt" ]]; then
    pip install -r ./package/packages.txt
    echo "packages installed with success"
else
    echo "packages.txt not found!"
    exit 1
fi

# Create Thing
if [[ -f "./thing/createThing.py" ]]; then
    python ./thing/createThing.py
    echo "Thing created with success!"
else
    echo "createThing.py not found!"
    exit 1
fi

# Turn on GTW code on reboot
cron_command="@reboot sleep 100 && /home/admin/pgadmin4/bin/python /home/admin/Desktop/GTW_installer/main >> /var/log/GTW_logs 2>&1 &"
(sudo crontab -l ; echo "$cron_command") | sudo crontab -
echo "Configuration for reboot done!"

echo "Setup complete!"

# Reboot GTW
timeVariable = 10
while [ $timeVariable > 0 ]
do
echo "GTW will reboot in $timeVariable seconds to apply changes and start communication..."
sleep 1
timeVariable = $timeVariable - 1
done
sudo shutdown -r now
