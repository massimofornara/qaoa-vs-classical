#!/bin/bash

echo "[🔍] Scansione rete locale in corso..."
# Rileva il tuo IP locale e subnet
IP=$(ip addr show wlan0 | grep 'inet ' | awk '{print $2}')
SUBNET=$(echo $IP | cut -d"/" -f2)
GATEWAY=$(ip route | grep default | awk '{print $3}')
RANGE=$(echo $IP | cut -d"/" -f1 | cut -d"." -f1-3).0/24

echo "[ℹ️] Subnet: $RANGE"

# Lancia scansione Nmap sulla rete
nmap -sn $RANGE -oG - | awk '/Up$/{print $2}' > live_hosts.txt

echo "[📁] Host attivi rilevati:"
cat live_hosts.txt

# Rileva MAC e IP dei dispositivi live
echo "[🧠] MAC address e identificazione dispositivi:"
for IP in $(cat live_hosts.txt); do
    MAC=$(arp -n $IP | grep -o -E "([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}")
    echo "$IP - $MAC" >> devices.log
    echo "[✔️] $IP - $MAC"
done

# Salva il file per confronto successivo
if [ ! -f baseline.log ]; then
    cp devices.log baseline.log
    echo "[✅] Prima scansione salvata. Tutto ok."
else
    echo "[⚠️] Confronto con scansione precedente..."
    diff baseline.log devices.log > diff.log
    if [ -s diff.log ]; then
        echo "[🚨] ATTENZIONE: nuovi dispositivi trovati o modifiche:"
        cat diff.log
        echo "[🔔] Possibile intrusione o nuovo accesso non autorizzato."
    else
        echo "[🟢] Nessuna differenza rilevata. Nessun accesso sospetto."
    fi
fi
