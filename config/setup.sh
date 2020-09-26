#!/bin/bash -e

sudo -n true
test $? -eq 0 || exit "Need sudo priveledge to run script"


echo "** Change directory **"
cd ..

echo "** Update system **"
apt-get update

echo "** Installing python3 and pip **"
apt-get install python3-pip python3-dev

echo "** Install supervisor **"
sudo apt install supervisor

echo "** Create a virtual envirement and activate it **"
python3 -m venv venv
source venv/bin/activate

echo "** Install gunicorn into virtual envirement **"
pip3 install gunicorn

echo "** Install flask into virtual envirement **"
pip3 install flask 

echo "** Install flask-cors **"
pip3 install -U flask-cors

echo "** Install flask-jwt-extended **"
pip3 install flask-jwt-extended

echo "** Install requests **"
pip3 install requests

echo "************ INPUT VALUES **************"
while :; do
    read -r -p 'Write password to encode/decode JWT token: ' key
    export SECRET_KEY="${key}"
    read -r -p 'Write which port the server should use [5054]: ' port
    if [[ $port =~ ^-?[0-9]+$ ]]
    then
        sed -i.bak -E "s/([0-9]+.[0-9]+.[0-9]+.[0-9]+:)[0-9]+/\1${port}/g" ../boot.sh
    else
        echo 'This is not an valid port number. Please write an integer'
    fi
    echo "Checking Firewall"
    which udw status verbose | grep Status:
    if [ $? == 'Status: active' ]
    then
        ufw allow $port
    fi
    read -r -p 'Are you sure of this setup. Type "yes" to continue: '
    [[ "${REPLY}" == 'yes' ]] && break
done

echo "Adding new user 'smarthomenode'"
adduser smarthomenode
adduser smarthomenode sudo 

echo "Adding rights to user on the folder"
folderfile=$(eval "readlink -f boot.sh")
folder=$(eval "dirname -- ${folderfile}")
folderconfig="${folder}/config/smarthome_node.conf"

echo "Change permission on folder"
#chown -R smarthomenode:smarthomenode "${folder}"

echo "Modify conf file"
#sed -i -E "s/(directory=).+/\1${folder}/g" ./smarthome_node.conf
#sed -i -E "s/(command=).+/\1${folderfile}/g" ./smarthome_node.conf
echo "directory=${folder}" >> ./config/smarthome_node.conf
echo "command=${folderfile}" >> ./config/smarthome_node.conf

echo "Create symlink for supervisor"
ln -s "${folderconfig}" /etc/supervisor/conf.d/smarthome_node.conf

echo "Reread configfile in supervisor"
supervisorctl reread
supervisorctl update
supervisorctl avail
supervisorctl restart  

cd config