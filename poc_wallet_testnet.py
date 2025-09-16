import hashlib
import time
from mnemonic import Mnemonic

# -----------------------------
# CONFIGURAZIONE WALLET FINTIZIO
# -----------------------------
# Inserisci il timestamp simulato del wallet (es. creazione passata)
timestamp_str = "2021-08-14 13:22:05"  # puoi cambiare a qualsiasi data passata
timestamp = int(time.mktime(time.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")))

# -----------------------------
# SIMULAZIONE RNG VULNERABILE
# -----------------------------
# Simula l'RNG debole basato sul timestamp (solo per testnet!)
seed_input = str(timestamp).encode('utf-8')
entropy = hashlib.sha256(seed_input).digest()[:16]  # 128 bit come nell'esempio

# -----------------------------
# GENERAZIONE MNEMONIC
# -----------------------------
mnemo = Mnemonic("english")
mnemonic_words = mnemo.to_mnemonic(entropy)

print("=== PoC Wallet Fittizio ===")
print("Timestamp wallet simulato:", timestamp_str)
print("Entropy (hex):", entropy.hex())
print("Mnemonic ricostruito:", mnemonic_words)

# -----------------------------
# SIMULAZIONE IMPORT IN TESTNET WALLET
# -----------------------------
print("\nPer testare in Trust Wallet Testnet o emulator:")
print("1. Apri Trust Wallet in modalità testnet/emulatore")
print("2. Vai su 'Import Wallet' e inserisci il mnemonic sopra")
print("3. Avrai accesso al wallet fittizio con fondi zero")
