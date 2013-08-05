#!/bin/bash

SOURCE="./install-files/*"
DEST="/"
OPTION=$1
shift
if [ "$OPTION" = "--dest" ];then

	if [  "$1" != "" ];then
		DEST="$1"
	fi
fi

SERVER_FILE="$DEST""/usr/share/n4d/xmlrpc-server/server.py"
SERVER_BIN="$DEST""/usr/sbin/n4d-server"
CERTGEN_BIN="$DEST""/usr/share/n4d/certgen/n4d-certgen"
FILESECRET="$DEST""/etc/n4d/key"


check_netifaces()
{
	VAR=0
	echo -n "* Checking python-netifaces ... "
	
	python -c "import netifaces" 2>/dev/null || VAR=1
	if [ $VAR -eq 0 ];then
		echo  "OK"
	else
		echo "FAILED"
		echo -e "\tLibrary is not installed."
		exit 1
	fi
}

check_ppam()
{
	VAR=0
	echo -n "* Checking python-pam ... "
	
	python -c "import PAM" 2>/dev/null || VAR=1
	if [ $VAR -eq 0 ];then
		echo  "OK"
	else
		echo "FAILED"
		echo -e "\tLibrary is not installed."
		exit 1
	fi
}

check_openssl()
{
	VAR=0
	echo -n "* Checking openssl ... "
	
	openssl -h 2>/dev/null || VAR=1
	
	if [ $VAR -eq 0 ];then
		echo  "OK"
	else
		echo "FAILED"
		echo -e "\t/usr/bin/openssl is not installed."
		exit 1
	fi
	
}

copy_files()
{



	echo -n "* Copying files ... "
	mkdir -p $DEST
	cp -rf $SOURCE $DEST
	mkdir -p "$DEST"/usr/sbin
	if [ ! -e "$SERVER_BIN" ]; then
		ln -s "$SERVER_FILE" "$SERVER_BIN" 
	fi
		
	echo "OK"
}

generate_n4d_key()
{

	echo -n "* Generating n4d key ... "
	
	if [ ! -e "$FILESECRET" ]; then
		cat /dev/urandom 2>/dev/null | tr -dc '0-9a-zA-Z' 2>/dev/null |{ head -c 50;echo ""; } > $FILESECRET
		chmod 400 $FILESECRET
		chown root:root $FILESECRET		
	fi

	echo "OK"



}

generate_cert()
{
	echo -n "* Generating n4d certificate ... "
	$CERTGEN_BIN	"$DEST/etc/n4d/cert/"
	echo "OK"
}


echo -e "\n* N4D INSTALLATION *\n"

check_ppam
check_netifaces
check_openssl
copy_files
generate_n4d_key
generate_cert

echo ""
echo "* Installation finished"
echo -e "\t[Info] To run the n4d service, execute n4d-server with root privileges.\n"



