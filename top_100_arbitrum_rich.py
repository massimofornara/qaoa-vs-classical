
import requests
import time

ARBISCAN_API_KEY ="YX9RCZVHW4BZKSZITPF32G6P2KH3S68AH7"  # Inserisci la tua API key
BASE_URL = 'https://api.arbiscan.io/api'

def get_contracts_from_richlist(limit=100):
    url = f'https://arbiscan.io/accounts?ps=100'
    print("⚠️  Arbiscan non fornisce direttamente via API la 'richlist', ma possiamo combinarla con il metodo getAccountBalance")

    # Arbiscan non ha una "richlist API" ufficiale, quindi andrebbero scrappate le prime 100 addresses da Arbiscan UI
    # In alternativa, puoi usare DeBank API o Dune Analytics.

    raise NotImplementedError("Per la richlist completa serve scraping o utilizzo di DeBank/Dune APIs")

def get_contract_balance(address):
    url = f'{BASE_URL}?module=account&action=balance&address={address}&tag=latest&apikey={ARBISCAN_API_KEY}'
    response = requests.get(url)
    data = response.json()
    if data["status"] == "1":
        return int(data["result"]) / 1e18
    else:
        return None

def get_contract_type(address):
    url = f'{BASE_URL}?module=contract&action=getcontractcreation&contractaddresses={address}&apikey={ARBISCAN_API_KEY}'
    response = requests.get(url)
    data = response.json()
    if data['status'] == '1':
        return "Contract"
    return "Wallet"

def get_rich_contracts_from_custom_list(addresses):
    results = []
    for addr in addresses:
        print(f"⏳ Fetching: {addr}")
        balance = get_contract_balance(addr)
        ctype = get_contract_type(addr)
        if ctype == "Contract":
            results.append({
                "address": addr,
                "balance": balance
            })
        time.sleep(0.2)  # Rate limiting
    return sorted(results, key=lambda x: x["balance"], reverse=True)

# Esempio di lista top address (hardcoded — aggiorna da Arbiscan manualmente)
top_addresses = [
    "0x489ee077994b6658eafa855c308275ead8097c4a",  # GMX Vault
    "0xba12222222228d8ba445958a75a0704d566bf2c8",  # Balancer
    "0x5979d7b546e38e414f7e9822514be443a4800529",  # Lido wstETH
    # ... Aggiungine fino a 100
]

# Esecuzione
rich_contracts = get_rich_contracts_from_custom_list(top_addresses)
for idx, c in enumerate(rich_contracts):
    print(f"{idx+1:03d}. {c['address']} - {c['balance']} ETH")
