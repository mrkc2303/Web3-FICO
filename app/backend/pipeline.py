import requests
import json
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from scipy.stats import entropy

# ============== CONFIG ==============
ETHERSCAN_API_KEY = "7A32HIJRFBSUJQK8S6WD3E2XCDS6XBW9JZ"  # Replace with your key
# MODEL_PATH = "trust_score_model.pkl"
# SCALER_PATH = "trust_score_scaler.pkl"

# ============== LOAD MODEL ==========
# model = joblib.load(MODEL_PATH)
# scaler = joblib.load(SCALER_PATH)

# ============== API FETCH ===========
def get_transactions(wallet_address, tx_limit=10000):
    url = "https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet_address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        if result["status"] == "1":
            return result["result"][:tx_limit]
        else:
            return []
    except:
        return []
    
def get_wallet_balance(wallet_address):
    url = "https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "balance",
        "address": wallet_address,
        "tag": "latest",
        "apikey": ETHERSCAN_API_KEY
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        if result["status"] == "1":
            balance_wei = int(result["result"])
            return balance_wei  # convert to ETH
        else:
            return 0
    except:
        return 0


# ============== FEATURE ENGINEERING =============
def extract_transaction_features(transactions):
    if not transactions:
        return {key: 0 for key in [
            "total_transactions", "self_transfer_ratio", "circular_txn_count", "circular_txn_ratio",
            "avg_txn_value_eth", "txn_spike_score", "value_std_dev", "avg_gas_used", "avg_gas_price",
            "active_days", "wallet_age_days", "unique_counterparties", "failed_txn_ratio",
            "eth_inflow_outflow_ratio", "erc20_txn_count", "nft_txn_count", "first_txn_time_of_day",
            "erc20_token_diversity", "tx_direction_ratio", "contract_interaction_ratio",
            "value_entropy", "tx_burst_count", "average_txn_interval", "new_token_interaction_count",
            "token_approval_count", "sbt_poap_event_count", "approved_token_list"
        ]}

    txn_values, gas_used_list, gas_price_list, time_stamps = [], [], [], []
    from_addresses, to_addresses, counterparties = set(), set(), set()
    approved_tokens = set()
    erc20_token_contracts, new_token_contracts, circular_pairs = set(), set(), {}
    inflow = outflow = failed_txns = self_transfers = circular_count = contract_interactions = erc20_count = nft_count = approval_count = sbt_count = 0
    intervals = []
    prev_time = None

    for tx in transactions:
        from_addr = tx.get('from', '').lower()
        to_addr = tx.get('to', '').lower()
        value = int(tx.get('value', 0))
        gas = int(tx.get('gasUsed', 0))
        gas_price = int(tx.get('gasPrice', 0))
        timestamp = int(tx.get('timeStamp', 0))
        is_error = tx.get('isError', "0") == "1"
        input_data = tx.get('input', '')
        contract_address = tx.get('contractAddress', '')
        method_id = tx.get('methodId', '').lower()

        txn_values.append(value / 1e18)
        gas_used_list.append(gas)
        gas_price_list.append(gas_price)
        time_stamps.append(timestamp)
        from_addresses.add(from_addr)
        to_addresses.add(to_addr)
        counterparties.update([from_addr, to_addr])

        if from_addr == to_addr:
            self_transfers += 1

        if (to_addr, from_addr) in circular_pairs:
            circular_count += 1
        else:
            circular_pairs[(from_addr, to_addr)] = True

        inflow += value if to_addr else 0
        outflow += value if from_addr else 0
        failed_txns += int(is_error)

        if input_data.startswith("0xa9059cbb"):
            erc20_count += 1
            erc20_token_contracts.add(to_addr)
        elif input_data.startswith("0x23b872dd"):
            nft_count += 1
        if input_data.startswith("0x095ea7b3"):
            approval_count += 1
            approved_tokens.add(to_addr)
        if input_data.startswith("0x40c10f19") or input_data.startswith("0xb88d4fde"):
            sbt_count += 1
        if contract_address:
            contract_interactions += 1
        if method_id:
            new_token_contracts.add(to_addr)
        if prev_time:
            intervals.append(timestamp - prev_time)
        prev_time = timestamp

    total_txns = len(transactions)
    wallet_age = (datetime.utcnow() - datetime.utcfromtimestamp(min(time_stamps))).days if time_stamps else 0
    days_active = len(set(datetime.utcfromtimestamp(ts).date() for ts in time_stamps))
    txn_spike_score = max(pd.Series(time_stamps).value_counts()) if time_stamps else 0
    time_of_day = datetime.utcfromtimestamp(min(time_stamps)).hour if time_stamps else 0
    avg_interval = np.mean(intervals) if intervals else 0
    value_entropy = entropy(pd.Series(txn_values).value_counts(normalize=True))

    return {
        "total_transactions": total_txns,
        "self_transfer_ratio": self_transfers / total_txns,
        "circular_txn_count": circular_count,
        "circular_txn_ratio": circular_count / total_txns,
        "avg_txn_value_eth": np.mean(txn_values),
        "txn_spike_score": txn_spike_score,
        "value_std_dev": np.std(txn_values),
        "avg_gas_used": np.mean(gas_used_list),
        "avg_gas_price": np.mean(gas_price_list),
        "active_days": days_active,
        "wallet_age_days": wallet_age,
        "unique_counterparties": len(counterparties),
        "failed_txn_ratio": failed_txns / total_txns,
        "eth_inflow_outflow_ratio": inflow / (outflow + 1),
        "erc20_txn_count": erc20_count,
        "nft_txn_count": nft_count,
        "first_txn_time_of_day": time_of_day,
        "erc20_token_diversity": len(erc20_token_contracts),
        "tx_direction_ratio": len(to_addresses) / (len(from_addresses) + 1),
        "contract_interaction_ratio": contract_interactions / total_txns,
        "value_entropy": value_entropy,
        "tx_burst_count": txn_spike_score,
        "average_txn_interval": avg_interval,
        "new_token_interaction_count": len(new_token_contracts),
        "token_approval_count": approval_count,
        "sbt_poap_event_count": sbt_count,
        "approved_token_list": list(approved_tokens)
    }

# ============== SCORING PIPELINE ==============
def score_wallet(wallet_address, model, scaler):
    transactions = get_transactions(wallet_address)

    # if len(transactions) < 5:
    #     return {
    #         "wallet": wallet_address,
    #         "score": 50.0,
    #         "label": "Neutral (Fallback: Low activity)"
    #     }
    
    balance = get_wallet_balance(wallet_address)
    no_of_trx = len(transactions)

    feature_dict = extract_transaction_features(transactions)
    feature_dict["Balance"] = balance
    feature_dict["noOfTrx.1"] = no_of_trx

    feature_df = pd.DataFrame([feature_dict])
    feature_df = feature_df.drop(columns=["approved_token_list"], errors="ignore")
    feature_df = feature_df.fillna(0)

    # 🧠 Align with model expectations (both names and order)
    required_features = model.feature_names_in_
    for col in required_features:
        if col not in feature_df.columns:
            feature_df[col] = 0
    feature_df = feature_df[required_features]

    numeric_cols = ['Balance', 'noOfTrx.1', 'avg_txn_value_eth', 'value_std_dev']
    # value_std_dev add this later
    feature_df[numeric_cols] = scaler.transform(feature_df[numeric_cols])

    # ✅ Predict
    score = model.predict(feature_df)[0] * 100
    score = np.clip(score, 0, 100).round(2)


    if score >= 70:
        label = "Safe"
    elif score >= 40:
        label = "Neutral"
    else:
        label = "Unsafe"

    def generate_risk_flags(row):
        flags = []
        if row['wallet_age_days'] < 3 and row['total_transactions'] < 5:
            flags.append("New Wallet - Low History")
        if row['circular_txn_ratio'] > 0.3:
            flags.append("Circular Transfers Detected")
        if row['token_approval_count'] > 0 and row['contract_interaction_ratio'] > 0.5:
            flags.append("Suspicious Contract Approvals")
        return flags or ["No critical flags"]

    flags = generate_risk_flags(feature_df.iloc[0])


    return {
        "wallet": wallet_address,
        "score": score,
        "label": label,
        "flags": flags
    }

# ============== USAGE EXAMPLE ==============

# wallet_to_test = "0x29E225D888cF11C5E67613BfFD30Bcf071EB3D4A"
# result = score_wallet(wallet_to_test)
# print("\n🧠 WIRE Trust Score")
# print(f"Wallet: {result['wallet']}")
# print(f"Score: {result['score']} / 100")
# print(f"Label: {result['label']}")
# print(f"Flags: {result['flags']}")