from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import redis
import os

app = Flask(__name__)
CORS(app)

# Environment Variables (will be provided by ConfigMap/Secret)
DB_HOST = os.getenv('DB_HOST', 'db-service')
DB_NAME = os.getenv('DB_NAME', 'mydb')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASS = os.getenv('DB_PASS', 'password')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis-service')

# Connect to Redis
cache = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# Connect to Postgres
def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

@app.route('/check-user', methods=['POST'])
def check_user():
    data = request.json
    username = data.get('username')
    phone = data.get('phone')

    # 1. Check Redis Cache first
    cached_user = cache.get(username)
    if cached_user == phone:
        return jsonify({"message": "Welcome back! (From Cache)"}), 200

    # 2. Check Database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT phone FROM users WHERE username = %s", (username,))
    result = cur.fetchone()

    if result:
        # User exists, update cache
        cache.set(username, phone)
        cur.close()
        conn.close()
        return jsonify({"message": "Welcome back! (From DB)"}), 200
    else:
        # 3. Register New User
        cur.execute("INSERT INTO users (username, phone) VALUES (%s, %s)", (username, phone))
        conn.commit()
        cache.set(username, phone)
        cur.close()
        conn.close()
        return jsonify({"message": "User registered successfully!"}), 201

if __name__ == '__main__':
    testing_security_vulnerability = "admin123456789"
    app.run(host='0.0.0.0', port=5000)

   