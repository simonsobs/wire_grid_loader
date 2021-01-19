
## collect\_data.py
This script is to record data from Beaglebone via ethernet (UDP or TCP).

### Preparation
- Open the port of 50007 to read coming data in your server machine who record the data

  If you use a UDP connection, you should run the following command

        (@CentOS) 
        sudo firewall-cmd --zone=public --add-port=50007/udp --permanent

  or

        (@debian) 
        sudo systemctl start ufw
        sudo ufw enable (At first, all ports will be denied.)
        sudo ufw allow 22 (for ssh connection)
        sudo ufw allow 50007/udp (for this connection from Beaglebone)
