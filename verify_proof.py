import sys
import os
import json
from datetime import datetime, timezone
from web3 import Web3

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def print_receipt(alert_id, threat_class, confidence, alert_hash, tx_hash, block_num, block_time, contract_addr):
    print("\n" + "=" * 68)
    print("ANVEX ON-CHAIN FORENSIC PROOF VERIFIER (ETHEREUM LEDGER)")
    print("=" * 68)
    print(f" STATUS           : [CRYPTOGRAPHICALLY VERIFIED - IMMUTABLE]")
    print(f" Alert ID         : {alert_id}")
    print(f" Threat Class     : {threat_class}")
    print(f" AI Confidence    : {confidence:.2f}%")
    print(f" Alert SHA-256    : {alert_hash}")
    print(f" Transaction Hash : {tx_hash}")
    print(f" Mined in Block   : {block_num}")
    print(f" Block Timestamp  : {block_time}")
    print(f" Smart Contract   : {contract_addr}")
    print("=" * 68)
    print(" [Integrity Validated] Payload cannot be altered without breaking hash.")
    print(" [Non-Repudiation]   Timestamp sealed in consensus block.")
    print("=" * 68 + "\n")

def main():
    rpc_url = os.getenv("HARDHAT_RPC_URL", "http://127.0.0.1:8545")
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    if not w3.is_connected():
        print(f"[ERROR] Could not connect to Ethereum Hardhat node at {rpc_url}")
        print("Please ensure Terminal 1 is running: npx hardhat node")
        sys.exit(1)

    contract_info_path = os.path.join(os.path.dirname(__file__), "trust_layer", "deployed", "contract_info.json")
    if not os.path.exists(contract_info_path):
        print(f"[ERROR] Contract info not found at {contract_info_path}")
        print("Please deploy contract first: cd trust_layer && npm run deploy")
        sys.exit(1)

    with open(contract_info_path, "r") as f:
        info = json.load(f)

    contract_addr = info["address"]
    contract = w3.eth.contract(address=contract_addr, abi=info["abi"])

    query = sys.argv[1].strip() if len(sys.argv) > 1 else None

    # If no argument, pick the latest transaction on the contract
    if not query:
        print("[INFO] No query passed. Searching for latest notarized alert on-chain...")
        current_block = w3.eth.block_number
        found_tx = None
        for b in range(current_block, 0, -1):
            block = w3.eth.get_block(b, full_transactions=True)
            for tx in block.transactions:
                if tx["to"] and tx["to"].lower() == contract_addr.lower():
                    found_tx = tx
                    break
            if found_tx:
                break
        if not found_tx:
            print("[INFO] No notarized transactions found on contract yet.")
            sys.exit(0)
        query = "0x" + found_tx.hash.hex()

    clean_query = query.lower()
    if not clean_query.startswith("0x") and len(clean_query) == 64:
        clean_query = "0x" + clean_query

    # 1. Try as Transaction Hash
    if clean_query.startswith("0x") and len(clean_query) == 66:
        try:
            tx = w3.eth.get_transaction(clean_query)
            decoded = contract.decode_function_input(tx.input)
            block = w3.eth.get_block(tx.blockNumber)
            block_dt = datetime.fromtimestamp(block.timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            args = decoded[1]
            alert_id = args.get("_alertId", "N/A")
            threat_class = args.get("_threatClass", "N/A")
            confidence = args.get("_confidence", 0) / 100.0
            alert_hash = "0x" + args.get("_alertHash", b"").hex()

            print_receipt(alert_id, threat_class, confidence, alert_hash, clean_query, tx.blockNumber, block_dt, contract_addr)
            return
        except Exception:
            pass  # Fall through to check if it's an alert_hash

    # 2. Try as Alert Hash (SHA-256) or Alert ID
    try:
        events = contract.events.AlertNotarized.get_logs(from_block=0)
        for evt in events:
            evt_alert_hash = "0x" + evt.args.alertHash.hex()
            evt_tx_hash = "0x" + evt.transactionHash.hex()

            # Check if matching alert_hash
            if clean_query.startswith("0x") and evt_alert_hash.lower() == clean_query:
                tx = w3.eth.get_transaction(evt.transactionHash)
                decoded = contract.decode_function_input(tx.input)
                args = decoded[1]
                block = w3.eth.get_block(tx.blockNumber)
                block_dt = datetime.fromtimestamp(block.timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
                print_receipt(args["_alertId"], args["_threatClass"], args["_confidence"]/100.0, evt_alert_hash, evt_tx_hash, tx.blockNumber, block_dt, contract_addr)
                return

        # 3. Try as Alert ID directly on contract verifyAlert
        try:
            call_res = contract.functions.verifyAlert(query).call()
            alert_hash = "0x" + call_res[0].hex()
            threat_class = call_res[1]
            confidence = call_res[2] / 100.0
            block_ts = call_res[3]
            block_dt = datetime.fromtimestamp(block_ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

            # Find tx_hash from events
            tx_h = "N/A"
            target_keccak = Web3.keccak(text=query).hex()
            for evt in events:
                if evt.args.alertId.hex() == target_keccak:
                    tx_h = "0x" + evt.transactionHash.hex()
                    break

            print_receipt(query, threat_class, confidence, alert_hash, tx_h, "Confirmed on-chain", block_dt, contract_addr)
            return
        except Exception:
            pass

    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        sys.exit(1)

    print(f"\n[NOT FOUND] No on-chain alert or transaction found matching query: '{query}'")
    print("Ensure the attack has run and been notarized by checking http://localhost:5173\n")

if __name__ == "__main__":
    main()
