# vulnerable_app.py
from flask import Flask, request, jsonify
import os
import sqlite3
import pickle   # unsafe deserialization example
import yaml     # older PyYAML usage pattern
import subprocess

app = Flask(__name__)

# --- Intentional: hardcoded credential (sast should flag this) ---
DB_PASSWORD = "P@ssw0rd!_Hardcoded"   # <-- SENSITIVE: hardcoded secret

# Simple DB connect (for demo only)
def get_conn():
    # using a file-based sqlite for demo
    conn = sqlite3.connect('banking_demo.db')
    return conn

@app.route('/balance', methods=['GET'])
def get_balance():
    # Example of using a request param unsafely in a shell call (injection risk)
    account = request.args.get('account', '')
    # ❌ Vulnerable pattern: unsanitized user input passed to shell with shell=True
    cmd = "echo Checking account: " + account
    subprocess.call(cmd, shell=True)  # SAST should flag shell=True + concatenation

    # Return fake balance
    return jsonify({"account": account, "balance": 1000})

@app.route('/deserialize', methods=['POST'])
def deserialize_user():
    """
    Endpoint that accepts a pickled object (unsafe - for demo).
    A SAST tool should flag 'pickle.loads' usage on untrusted data.
    """
    raw = request.get_data()
    try:
        # ❌ Unsafe deserialization: untrusted pickle data
        obj = pickle.loads(raw)
        return jsonify({"status": "ok", "type": str(type(obj))})
    except Exception as e:
        return jsonify({"error": "failed to deserialize", "msg": str(e)}), 400

@app.route('/yaml-load', methods=['POST'])
def yaml_load():
    """
    Demonstrates unsafe yaml loading (older PyYAML patterns).
    """
    raw = request.get_data().decode('utf-8')
    try:
        # ❌ Unsafe: yaml.load without specifying SafeLoader (older usage)
        data = yaml.load(raw)   # SAST should flag yaml.load -> use safe_load instead
        return jsonify({"loaded_keys": list(data.keys())})
    except Exception as e:
        return jsonify({"error": "yaml error", "msg": str(e)}), 400

@app.route('/eval', methods=['POST'])
def do_eval():
    """
    Demonstrates dangerous eval() on user input (classic SAST issue).
    """
    body = request.json or {}
    expr = body.get('calc', '')
    # ❌ Dangerous: evaluating user-controlled expression
    try:
        result = eval(expr)   # SAST should flag eval
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": "bad expression", "msg": str(e)}), 400

if __name__ == '__main__':
    # init DB (demo only)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS accounts (account TEXT PRIMARY KEY, balance INTEGER)')
    cur.execute("INSERT OR IGNORE INTO accounts (account, balance) VALUES ('1111', 1000)")
    conn.commit()
    conn.close()
    app.run(host='0.0.0.0', port=5000)
