from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Setup database dummy
def init_db():
    conn = sqlite3.connect('banking.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS loans (
        customer_id TEXT,
        status TEXT
    )''')
    cursor.execute("INSERT INTO loans VALUES ('12345', 'Approved')")
    cursor.execute("INSERT INTO loans VALUES ('67890', 'Rejected')")
    conn.commit()
    conn.close()

@app.route('/loan-status', methods=['GET'])
def loan_status():
    customer_id = request.args.get('customer_id')
    conn = sqlite3.connect('banking.db')
    cursor = conn.cursor()

    # ❌ Vulnerable code (SQL Injection)
    query = f"SELECT status FROM loans WHERE customer_id = '{customer_id}'"
    cursor.execute(query)
    result = cursor.fetchall()

    if result:
        return jsonify({"loan_status": [row[0] for row in result]})
    else:
        return jsonify({"loan_status": "Not Found"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
