#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# scan_full_auto.py
#
# Esecuzione:
#   python scan_full_auto.py
#
# Cosa fa:
#  - Autoinstalla le dipendenze (web3, reportlab, eth_utils) se mancano.
#  - Usa RPC pubblici predefiniti (Ethereum + Arbitrum One).
#  - Scansiona una lista integrata di indirizzi noti (token/pool comuni).
#  - Genera report PDF e HTML per ciascun indirizzo.
#  - Crea uno ZIP con tutti i PDF.
#  - Genera un file email .eml pronto (to: bounty@hackenproof.com) con corpo e allegato zip.
#
# Opzionale: invio SMTP automatico (disattivato di default). Per abilitarlo,
#           imposta USE_SMTP=True e compila SMTP_* qui sotto.

import sys, subprocess, importlib, os, zipfile, mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

# ========== Config base (puoi lasciarla così) ==========
OUT_DIR = "reports_auto"
ZIP_NAME = "bundle_reports.pdf.zip"
EMAIL_TO = ["bounty@hackenproof.com"]
EMAIL_CC = ["support@hacken.io"]  # puoi lasciare vuoto []
AUTHOR_NAME = "Massimo (Security Researcher)"
AUTHOR_EMAIL = "you@example.com"  # metti il tuo se vuoi nel testo email

# SMTP (disattivo di default: USE_SMTP=False)
USE_SMTP = False
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "you@gmail.com"
SMTP_PASS = "APP_PASSWORD"
EMAIL_FROM = SMTP_USER  # mittente; se lasci vuoto userà SMTP_USER

# RPC pubblici (senza chiave). Se vuoi, puoi sostituire con Alchemy/Infura.
RPCS = {
    "Ethereum-Mainnet": "https://mainnet.infura.io/v3/2c2a861558e74f48a14992b8059c3f27",  # Infura personalizzato
    "Arbitrum-One":     "https://arb1.arbitrum.io/rpc",   # ufficiale
}
# Lista integrata di indirizzi noti (verificati ampiamente in community)
ADDRESS_BOOK = {
    "Ethereum-Mainnet": [
        # WETH (WETH9), USDC
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
    ],
    "Arbitrum-One": [
        # Token principali
        "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",  # WETH
        "0xAf88d065E77c8cC2239327C5EDb3A432268e5831",  # USDC (nativo)
        "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",  # USDC.e (bridged)
        "0x2f2a2543B76A4166549F7aAB2e75Bef0aefC5B0f",  # WBTC
        "0x912CE59144191C1204E64559FE8253a0e49E6548",  # ARB
        # (Facoltativo: puoi aggiungere pool Uniswap v3 ben note)
        # "0xC31e54C7A869B9fcbECC14363cf510D1C41Fa443",  # UNI V3 WETH/USDC.e 0.05%
        # "0x17c14D2C404D167802B16C450d3c99F88F2C4F4d",  # UNI V3 WETH/USDC 0.3%
    ],
}

# ========== Autoinstall dipendenze ==========
def ensure(pkg: str):
    try:
        return importlib.import_module(pkg)
    except ImportError:
        print(f"📦 Installo {pkg} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-input", pkg])
        return importlib.import_module(pkg)

web3 = ensure("web3")
reportlab = ensure("reportlab")
eth_utils = ensure("eth_utils")

from web3 import Web3
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

import smtplib, ssl
from email.message import EmailMessage

# ========== Euristiche scanning ==========
EIP1967_IMPLEMENTATION_SLOT = int("0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc", 16)
EIP1967_ADMIN_SLOT          = int("0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103", 16)

SIG_OWNER          = "0x8da5cb5b"  # owner()
SIG_IMPLEMENTATION = "0x5c60da1b"  # implementation()
SIG_ADMIN          = "0xf851a440"  # admin()
SIG_PAUSED         = "0x5c975abb"  # paused()
SIG_UPGRADE_TO     = "0x3659cfe6"  # upgradeTo(address)

def is_eip1167_minimal_proxy(bytecode_hex: str) -> bool:
    bc = bytecode_hex.lower().removeprefix("0x")
    return ("363d3d373d3d3d363d73" in bc and "5af43d" in bc and bc.endswith("5bf3"))

def contains_opcode(bytecode_hex: str, opcode_hex: str) -> bool:
    return opcode_hex.lower().removeprefix("0x") in bytecode_hex.lower().removeprefix("0x")

def read_storage_at(w3: Web3, addr: str, slot_int: int) -> str:
    slot32 = slot_int.to_bytes(32, "big")
    try:
        return w3.eth.get_storage_at(addr, slot32).hex()
    except Exception:
        return "0x" + "00"*32

def try_staticcall(w3: Web3, to: str, data: str) -> str | None:
    try:
        res = w3.eth.call({"to": to, "data": data})
        return res.hex()
    except Exception:
        return None

def classify_severity(f: Dict[str, Any]) -> str:
    if f.get("has_selfdestruct") or f.get("anyone_admin"):
        return "CRITICAL"
    if f.get("eip1967_proxy") or f.get("is_minimal_proxy_eip1167") or f.get("upgrade_surface"):
        return "HIGH"
    if f.get("has_delegatecall"):
        return "MEDIUM"
    return "LOW"

def scan_contract(w3: Web3, address: str) -> Dict[str, Any]:
    addr = Web3.to_checksum_address(address)
    bytecode = w3.eth.get_code(addr).hex()
    byte_len = len(bytecode.removeprefix("0x")) // 2

    is_proxy_1167 = is_eip1167_minimal_proxy(bytecode)
    impl_slot = read_storage_at(w3, addr, EIP1967_IMPLEMENTATION_SLOT)
    adm_slot  = read_storage_at(w3, addr, EIP1967_ADMIN_SLOT)
    eip1967_proxy = (impl_slot != "0x" + "00"*32) or (adm_slot != "0x" + "00"*32)

    owner_raw          = try_staticcall(w3, addr, SIG_OWNER)
    implementation_raw = try_staticcall(w3, addr, SIG_IMPLEMENTATION)
    admin_raw          = try_staticcall(w3, addr, SIG_ADMIN)
    paused_raw         = try_staticcall(w3, addr, SIG_PAUSED)
    upgrade_to_raw     = try_staticcall(w3, addr, SIG_UPGRADE_TO)

    has_delegatecall = contains_opcode(bytecode, "0xf4")
    has_selfdestruct = contains_opcode(bytecode, "0xff")
    has_sstore       = contains_opcode(bytecode, "0x55")
    has_callcode     = contains_opcode(bytecode, "0xf2")

    findings = {
        "address": addr,
        "bytecode_size": byte_len,
        "is_minimal_proxy_eip1167": is_proxy_1167,
        "eip1967_proxy": eip1967_proxy,
        "eip1967.implementation_slot": impl_slot,
        "eip1967.admin_slot": adm_slot,
        "owner()": owner_raw,
        "implementation()": implementation_raw,
        "admin()": admin_raw,
        "paused()": paused_raw,
        "has_delegatecall": has_delegatecall,
        "has_selfdestruct": has_selfdestruct,
        "has_sstore": has_sstore,
        "has_callcode": has_callcode,
        "upgrade_surface": eip1967_proxy or (upgrade_to_raw is not None),
    }
    findings["severity"] = classify_severity(findings)
    return findings

# ========== Rendering report ==========
def to_table_data(findings: Dict[str, Any]) -> list[list[str]]:
    rows = [["Chiave", "Valore"]]
    for k, v in findings.items():
        if k in ("address", "severity"):
            continue
        rows.append([k, str(v)])
    return rows

def make_pdf(out_path: str, chain: str, rpc_name: str, f: Dict[str, Any]) -> None:
    doc = SimpleDocTemplate(out_path, pagesize=A4)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", fontSize=9, leading=11))
    elems = []
    meta_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    title = f"Report di Sicurezza – {chain} – {f['address']}"
    elems.append(Paragraph(title, styles["Title"]))
    elems.append(Paragraph(f"Data: {meta_date} • RPC: {rpc_name}", styles["Normal"]))
    elems.append(Spacer(1, 10))

    sev = f.get("severity", "LOW")
    color_map = {"CRITICAL": colors.red, "HIGH": colors.orange, "MEDIUM": colors.darkgoldenrod, "LOW": colors.green}
    elems.append(Paragraph("Executive Summary", styles["Heading2"]))
    elems.append(Paragraph(
        f"Classificazione complessiva: <b><font color='{color_map.get(sev, colors.black)}'>{sev}</font></b>.",
        styles["Normal"]
    ))
    bullets = []
    if f.get("eip1967_proxy"): bullets.append("Proxy EIP-1967 (slot implementation/admin impostati).")
    if f.get("is_minimal_proxy_eip1167"): bullets.append("Pattern minimal proxy EIP-1167 nel bytecode.")
    if f.get("has_delegatecall"): bullets.append("Opcode DELEGATECALL presente → possibili rischi di delega.")
    if f.get("has_selfdestruct"): bullets.append("Opcode SELFDESTRUCT presente → rischio distruzione contratto.")
    if f.get("upgrade_surface"): bullets.append("Superficie di upgrade rilevata (proxy/upgradeTo).")
    if not bullets: bullets.append("Nessun pattern ad alto rischio rilevato dalle euristiche.")
    for b in bullets: elems.append(Paragraph(f"- {b}", styles["Normal"]))
    elems.append(Spacer(1, 10))

    elems.append(Paragraph("Dettagli (grezzi)", styles["Heading2"]))
    data = to_table_data(findings=f)
    table = Table(data, colWidths=[190, 330])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f3f4f6")),
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#e5e7eb")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#fafafa")]),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))
    elems.append(table)
    elems.append(Spacer(1, 10))

    elems.append(Paragraph("Raccomandazioni", styles["Heading2"]))
    recs = []
    if f.get("eip1967_proxy") or f.get("is_minimal_proxy_eip1167"):
        recs.append("Verificare admin multisig; limitare l’upgrade path (UUPS/Transparent).")
    if f.get("has_delegatecall"):
        recs.append("Confinare DELEGATECALL ad implementazioni fidate; allowlist e pause-guard.")
    if f.get("has_selfdestruct"):
        recs.append("Rimuovere/disabilitare SELFDESTRUCT o isolarlo con timelock/owner.")
    if not recs:
        recs.append("Nessun pattern ad alto rischio. Suggerito audit full-scope della logica di business.")
    for r in recs: elems.append(Paragraph(f"- {r}", styles["Normal"]))

    elems.append(Spacer(1, 16))
    elems.append(Paragraph(
        "Nota: Controlli euristici via RPC; non sostituiscono un audit completo.",
        styles["Small"]
    ))
    doc.build(elems)

def make_html(out_path: str, chain: str, rpc_name: str, f: Dict[str, Any]) -> None:
    meta_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    sev = f.get("severity","LOW")
    html = f"""<!doctype html><html lang="it"><meta charset="utf-8"><title>Report {f['address']}</title>
<style>body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial;padding:24px;line-height:1.45;color:#111}}
h1{{font-size:24px}} h2{{margin-top:18px;border-bottom:1px solid #eee;padding-bottom:6px}}
table{{border-collapse:collapse;width:100%}} th,td{{border:1px solid #e5e7eb;padding:6px 8px}} th{{background:#f3f4f6}}</style>
<h1>Report di Sicurezza – {chain} – {f['address']}</h1>
<p>Data: {meta_date} • RPC: {rpc_name}</p>
<h2>Executive Summary</h2>
<p>Classificazione: <b>{sev}</b></p>
<h2>Dettagli (grezzi)</h2>
<table><tr><th>Chiave</th><th>Valore</th></tr>
"""
    for k,v in f.items():
        if k in ("address","severity"): continue
        html += f"<tr><td>{k}</td><td>{v}</td></tr>\n"
    html += "</table>\n<h2>Raccomandazioni</h2><ul>"
    if f.get("eip1967_proxy") or f.get("is_minimal_proxy_eip1167"):
        html += "<li>Verificare admin multisig; limitare upgrade path (UUPS/Transparent).</li>"
    if f.get("has_delegatecall"):
        html += "<li>Limitare DELEGATECALL a implementazioni fidate; allowlist e pause-guard.</li>"
    if f.get("has_selfdestruct"):
        html += "<li>Rimuovere/disabilitare SELFDESTRUCT o proteggerlo con timelock.</li>"
    if not (f.get("eip1967_proxy") or f.get("is_minimal_proxy_eip1167") or f.get("has_delegatecall") or f.get("has_selfdestruct")):
        html += "<li>Nessun pattern ad alto rischio; considerare audit full-scope.</li>"
    html += "</ul><p style='color:#666;font-size:12px'>Analisi euristica via RPC – non sostituisce un audit completo.</p></html>"
    Path(out_path).write_text(html, encoding="utf-8")

# ========== Email (draft .eml o invio SMTP) ==========
def create_email_draft_eml(path: str, to: List[str], cc: List[str], subject: str, body: str, attachments: List[str]):
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM or "noreply@example.com"
    msg["To"] = ", ".join(to)
    if cc:
        msg["Cc"] = ", ".join(cc)
    msg["Subject"] = subject
    msg.set_content(body)

    for f in attachments:
        p = Path(f)
        if not p.exists():
            continue
        ctype, _ = mimetypes.guess_type(str(p))
        if ctype is None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(p, "rb") as fh:
            msg.add_attachment(fh.read(), maintype=maintype, subtype=subtype, filename=p.name)

    # Salva come .eml
    Path(path).write_bytes(bytes(msg))
    print(f"✉️  Bozza email .eml creata: {path}")

def send_email_smtp(to: List[str], cc: List[str], subject: str, body: str, attachments: List[str]):
    email_from = EMAIL_FROM or SMTP_USER
    msg = EmailMessage()
    msg["From"] = email_from
    msg["To"] = ", ".join(to)
    if cc:
        msg["Cc"] = ", ".join(cc)
    msg["Subject"] = subject
    msg.set_content(body)

    for f in attachments:
        p = Path(f)
        if not p.exists():
            continue
        ctype, _ = mimetypes.guess_type(str(p))
        if ctype is None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(p, "rb") as fh:
            msg.add_attachment(fh.read(), maintype=maintype, subtype=subtype, filename=p.name)

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
    print("📨 Email inviata via SMTP.")

# ========== Main ==========
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    produced_pdfs: List[str] = []

    for chain, rpc in RPCS.items():
        print(f"\n🌐 Scansione chain: {chain}  |  RPC: {rpc}")
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 30}))
        if not w3.is_connected():
            print(f"❌ Impossibile connettersi a {chain}. Salto.")
            continue
        rpc_name = rpc.split("://")[-1].split("/")[0]

        addrs = ADDRESS_BOOK.get(chain, [])
        if not addrs:
            print(f"ℹ️ Nessun indirizzo nella rubrica per {chain}.")
            continue

        for i, addr in enumerate(addrs, 1):
            try:
                f = scan_contract(w3, addr)
                pdf_path  = os.path.join(OUT_DIR, f"report_{chain}_{f['address']}.pdf".replace(":", "_"))
                html_path = os.path.join(OUT_DIR, f"report_{chain}_{f['address']}.html".replace(":", "_"))
                make_pdf(pdf_path, chain, rpc_name, f)
                make_html(html_path, chain, rpc_name, f)
                produced_pdfs.append(pdf_path)
                print(f"  [{i}/{len(addrs)}] ✅ {os.path.basename(pdf_path)} • severità={f['severity']}")
            except Exception as e:
                print(f"  [{i}/{len(addrs)}] ⚠️ Errore su {addr}: {e}")

    # ZIP di tutti i PDF
    zip_path = os.path.join(OUT_DIR, ZIP_NAME)
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for p in produced_pdfs:
                z.write(p, arcname=os.path.basename(p))
        print(f"\n📦 Creato ZIP: {zip_path}")
    except Exception as e:
        print(f"⚠️ ZIP fallito: {e}")
        zip_path = ""

    # Corpo email per Hacken
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    subject = "[Disclosure] On-chain security reports (heuristics) – Ethereum/Arbitrum"
    body = f"""Hello Hacken Team,

this is a responsible disclosure from {AUTHOR_NAME}.
Attached you will find on-chain heuristic reports (PDF, zipped) covering popular contracts on Ethereum and Arbitrum.
The reports include: proxy detection (EIP-1967 / EIP-1167), opcode red flags (DELEGATECALL/SELFDESTRUCT), raw slots and static-call probes.
Author: {AUTHOR_NAME} • Contact: {AUTHOR_EMAIL}
Date: {now}

Happy to proceed via HackenProof / NDA and provide additional technical evidence as needed.

Best regards,
{AUTHOR_NAME}
{AUTHOR_EMAIL}
"""

    # Crea bozza .eml sempre
    eml_path = os.path.join(OUT_DIR, "hacken_disclosure_draft.eml")
    attachments = [zip_path] if zip_path else produced_pdfs
    create_email_draft_eml(eml_path, EMAIL_TO, EMAIL_CC, subject, body, attachments)

    # Invio SMTP solo se USE_SMTP=True e ZIP presente
    if USE_SMTP and zip_path:
        try:
            send_email_smtp(EMAIL_TO, EMAIL_CC, subject, body, [zip_path])
        except Exception as e:
            print(f"⚠️ Invio SMTP fallito: {e}")

    print("\n✅ Finito.")
    print(f"Cartella report: {OUT_DIR}")
    print(f"- PDF/HTML multipli per contratto")
    print(f"- ZIP: {zip_path if zip_path else 'non creato'}")
    print(f"- Bozza email: {eml_path} (apribile da client email per invio)")

if __name__ == "__main__":
    main()
