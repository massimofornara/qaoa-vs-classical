nano crea_video_tiktok.sh
chmod +x crea_video_tiktok.sh
./crea_video_tiktok.sh
pkg update && pkg upgrade -y
pkg install imagemagick ffmpeg -y
./crea_video_tiktok.sh
termux-open tiktok_video/TikTok_CryptoBot_Template.mp4
sudo apt update && sudo apt install git python3 python3-pip curl wget -y
pip install shodan censys requests beautifulsoup4
nano openpayd-register-and-init.js
nano .env
node openpayd-register-and-init.js
npm install puppeteer
pkg update && pkg upgrade -y
pkg install nmap tsu curl git -y
cd ~
nano netwatch.sh
chmod +x netwatch.sh
./netwatch.sh
pkg install curl nmap iproute -y
pkg update && pkg install curl nmap inetutils -y
nano netwatch-lite.sh
chmod +x netwatch-lite.sh
./netwatch-lite.sh
# Apri Termux ed esegui:
am force-stop com.avg.android.vpn
am start -n com.avg.android.vpn/.ui.activity.MainActivity
nano poc_wallet_testnet.py
python poc_wallet_testnet.py
mkdir crypto_to_fiat_arb
cd crypto_to_fiat_arb
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows PowerShell
pip install --upgrade pip
pip install web3==6.20.1 eth-account==0.10.0 ccxt==4.4.34 python-dotenv==1.0.1
pkg update && pkg upgrade -y
pkg install -y rust clang make pkg-config libsqlite openssl
# Assicurati che $HOME/.cargo/bin sia nel PATH
echo 'source $HOME/.cargo/env' >> ~/.bashrc
source $HOME/.cargo/env
pip install --upgrade pip setuptools wheel
pip install web3==6.20.1 eth-account==0.10.0 ccxt==4.4.34 python-dotenv==1.0.1
cd crypto_to_fiat_arb
pkg update
pkg upgrade -y
pkg install -y rust clang make pkg-config libsqlite openssl
echo 'source $HOME/.cargo/env' >> ~/.bashrc
source $HOME/.cargo/env
nano .env
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install web3==6.20.1 eth-account==0.10.0 ccxt==4.4.34 python-dotenv==1.0.1
pkg update
pkg install -y python-cryptography libffi libffi-dev openssl
pkg install -y rust clang make pkg-config libffi libffi-dev openssl
echo 'source $HOME/.cargo/env' >> ~/.bashrc
source $HOME/.cargo/env
pip install --upgrade pip setuptools wheel setuptools-rust
pip install cryptography --no-binary=:all:
pip install web3==6.20.1 eth-account==0.10.0 ccxt==4.4.34 python-dotenv==1.0.1
python crypto_to_fiat_arb.py
# Entra nella cartella con crypto_to_fiat_arb.py e .env
cd crypto_to_fiat_arb
# Avvia un container Python con librerie già preinstallate
docker run --rm -it   -v $PWD:/app   -w /app   ghcr.io/summershrimp/python-defi:latest   python crypto_to_fiat_arb.py
pkg update && pkg upgrade
pkg install proot-distro git wget curl -y
proot-distro install ubuntu
proot-distro login ubuntu
proot-distro login ubuntu --user user
proot-distro login ubuntu
proot-distro login ubuntu --user massimo
# 5) Configura la build
tools/dev/v8gen.py x64.release
# 6) Forza l'uso del toolchain di sistema (niente clang/lld Google)
cat >> out.gn/x64.release/args.gn <<'EOF'
is_clang = false
use_sysroot = false
use_custom_libcxx = false
clang_use_chrome_plugins = false
use_lld = false
treat_warnings_as_errors = false
EOF

gn gen out.gn/x64.release
# 7) Compila SOLO d8 (limita i job per non saturare il telefono)
ninja -j2 -C out.gn/x64.release d8
# sei in Ubuntu proot come 'massimo'
cd ~/code/v8 || { echo "La cartella v8 non esiste"; exit 1; }
pkg update -y && pkg install -y python
nano scan_full_auto.py
python scan_full_auto.py
