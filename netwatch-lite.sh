#!/bin/bash

echo ""
echo "📡 [NETWATCH] Scansione della rete locale"

# Ottieni l'IP Wi-Fi del dispositivo
MY_IP=$(ip a | grep wlan0 | grep inet | awk '{print $2}' | cut -d'/' -f1)

if [ -z "$MY_IP" ]; then
  echo "❌ Errore: IP non rilevato. Sei connesso al Wi-Fi?"
  exit 1
fi

SUBNET=$(echo "$MY_IP" | cut -d'.' -f1-3)
RANGE="$SUBNET.0/24"

echo "🌐 Range di scansione: $RANGE"

echo "🔎 Avvio scansione nmap..."
nmap -sn "$RANGE" -oG netwatch_scan.log > /dev/null 2>&1

if [ ! -s netwatch_scan.log ]; then
  echo "⚠️ Nessun dispositivo trovato o scansione fallita."
  exit 1
fi

cat netwatch_scan.log | grep Up | awk '{print "🟢 Host attivo: " $2}' > netwatch_results.txt
cat netwatch_results.txt

# Salva baseline iniziale e confronta
if [ ! -f netwatch_baseline.txt ]; then
  cp netwatch_results.txt netwatch_baseline.txt
  echo "✅ Baseline salvata."
else
  echo "📁 Confronto con baseline precedente:"
  diff netwatch_baseline.txt netwatch_results.txt > netwatch_diff.txt
  if [ -s netwatch_diff.txt ]; then
    echo "🚨 Differenze trovate (nuovi o rimossi):"
    cat netwatch_diff.txt
  else
    echo "✅ Nessun cambiamento rilevato. Rete stabile."
  fi
fi
