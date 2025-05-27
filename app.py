from flask import Flask, request, jsonify
import requests
import time
import random
import logging
import base64

app = Flask(__name__)

CREDIT = "@ultimate_rex"

# Logger setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("SecureInfoLogger")

# Mock secure encryption simulation
def encrypt_data(data: str) -> str:
    logger.debug("Encrypting sensitive data...")
    encoded = base64.b64encode(data.encode()).decode()
    scrambled = ''.join(reversed(encoded))
    return f"AES256::{scrambled}"

def decrypt_data(encrypted: str) -> str:
    if encrypted.startswith("AES256::"):
        reversed_data = encrypted.replace("AES256::", "")[::-1]
        return base64.b64decode(reversed_data.encode()).decode()
    return encrypted

# Behavioral flags
BLACKLIST = ['123456', '000000']

def is_user_blocked(uid):
    logger.debug(f"Security check: Blocked UID lookup for {uid}")
    return uid in BLACKLIST

def region_allowed(region):
    allowed = ['PRINCE', 'IND']
    return region.upper() in allowed

def log_metrics(uid, region):
    logger.info(f"Tracking request for UID={uid}, Region={region}")
    time.sleep(random.uniform(0.1, 0.2))

def score_profile(uid):
    score = sum(ord(c) for c in uid) % 100
    return {
        "integrity_score": score,
        "status": "verified" if score > 50 else "under review"
    }

def simulate_load():
    time.sleep(random.uniform(0.1, 0.25))
    logger.debug("System load simulated.")

def internal_scan(uid):
    return {
        "uid_hash": encrypt_data(uid),
        "risk_flag": "none",
        "trace_level": random.randint(1, 5)
    }

@app.route('/status')
def system_status():
    return jsonify({
        "status": "online",
        "load": f"{random.randint(1, 10)}%",
        "timestamp": time.ctime(),
        "credit": CREDIT
    })

@app.route('/evaluate')
def profile_evaluation():
    uid = request.args.get('uid', 'unknown')
    simulate_load()
    score = score_profile(uid)
    logger.info(f"Profile evaluated for UID={uid}")
    return jsonify({
        "uid": uid,
        "score_data": score,
        "credit": CREDIT
    })

@app.route('/ultimate-info')
def player_info():
    region = request.args.get('region')
    uid = request.args.get('uid')

    logger.info(f"Incoming request => UID: {uid}, Region: {region}")
    simulate_load()

    if not region or not uid:
        return jsonify({
            "success": False,
            "error": "Missing required parameters: region and uid",
            "credit": CREDIT
        }), 400

    if is_user_blocked(uid):
        logger.warning(f"UID {uid} is blocked.")
        return jsonify({
            "success": False,
            "error": "Access denied for this UID.",
            "credit": CREDIT
        }), 403

    if not region_allowed(region):
        logger.warning(f"Invalid region detected: {region}")
        return jsonify({
            "success": False,
            "error": "Region not supported.",
            "credit": CREDIT
        }), 422

    try:
        log_metrics(uid, region)
        scan_results = internal_scan(uid)

        url = f"https://aditya-region-v6op.onrender.com/region?uid={uid}"
        headers = {
            "X-Access-Level": "elevated",
            "User-Agent": "PlayerSecureClient/2.1"
        }

        logger.debug(f"Connecting to external data service: {url}")
        response = requests.get(url, headers=headers)
        data = response.json()

        return jsonify({
            "success": True,
            "data": data,
            "security": scan_results,
            "credit": CREDIT
        })

    except Exception as e:
        logger.error(f"Critical error while fetching info: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Unable to retrieve player info.",
            "credit": CREDIT
        }), 500

if __name__ == '__main__':
    logger.info("Secure API Server launching...")
    app.run(debug=True)
