AUTHORS:
--------
Hector Garcia Huerta hectorgh@gmail.com  
Raul Rodrigo Segura raurodse@gmail.com  
What do i need for starting?
-------------------------
* Make file key in folder /etc/n4d/ containing a master secret key. This file is only readable and writable by root user. On Linux you can execute :

        cat /dev/urandom| tr -dc '0-9a-zA-Z' |{ head -c 50;echo ""; } > /etc/n4d/key  
        chmod 400 /etc/n4d/key  
        chown root:root /etc/n4d/key

* You need create digital certificate, because n4d uses ssl communication. You must create key which you will sign certificates and a certificate. These move to folder /etc/n4d/cert.
Previously you has created folder /etc/n4d/cert. You can use openssl for create this digital certificate.

        mkdir /etc/n4d/cert/
        openssl genrsa -out /etc/n4d/cert/n4dkey.pem 2048
        yes '' | openssl req -new -key /etc/n4d/cert/n4dkey.pem -out /etc/n4d/cert/n4d.csr
        openssl x509 -req -days 600 -in /etc/n4d/cert/n4d.csr -signkey /etc/n4d/cert/n4dkey.pem -out /etc/n4d/cert/n4dcert.pem

For installing
--------------

	./setup.py install --install-data=/


