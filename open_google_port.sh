export LC_ALL=C
router=$(ip r | grep default | cut -d " " -f 3)
gateway=$(upnpc -l | grep "desc: http://$router:[0-9]*/rootDesc.xml" | cut -d " " -f 3)
ip=$(upnpc -l | grep "Local LAN ip address" | cut -d: -f2)

external=8080
port=8080
upnpc -u  $gateway -d $external TCP
upnpc -u  $gateway -e "Web mapping Google OAuth" -a $ip $port $external TCP 