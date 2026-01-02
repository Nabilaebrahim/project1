from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import pool
import redis
import os
import logging

# Configure logging for professional monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Environment Variables
DB_HOST = os.getenv('DB_HOST', 'db-service')
DB_NAME = os.getenv('DB_NAME', 'mydb')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASS = os.getenv('DB_PASS')  # Secrets should be handled by Env/Secrets
REDIS_HOST = os.getenv('REDIS_HOST', 'redis-service')

# Use Connection Pooling to prevent resource leaks
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10, host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
    )
    cache = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")

@app.route('/check-user', methods=['POST'])
def check_user():
    data = request.get_json()
    
    # Input Validation
    if not data or 'username' not in data or 'phone' not in data:
        return jsonify({"error": "Invalid input data"}), 400

    username = data.get('username')
    phone = data.get('phone')

    conn = None
    try:
        # 1. Check Redis Cache
        cached_phone = cache.get(username)
        if cached_phone == phone:
            return jsonify({"message": "Welcome back! (From Cache)"}), 200

        # 2. Check Database with safe resource handling
        conn = db_pool.getconn()
        with conn.cursor() as cur:
            cur.execute("SELECT phone FROM users WHERE username = %s", (username,))
            result = cur.fetchone()

            if result:
                cache.set(username, phone, ex=3600)
                return jsonify({"message": "Welcome back! (From DB)"}), 200
            else:
                # 3. Register New User
                cur.execute("INSERT INTO users (username, phone) VALUES (%s, %s)", (username, phone))
                conn.commit()
                cache.set(username, phone, ex=3600)
                return jsonify({"message": "User registered successfully!"}), 201
                
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Service temporarily unavailable"}), 500
    finally:
        # Return connection to pool to prevent memory leaks
        if conn:
            db_pool.putconn(conn)

if __name__ == '__main__':
    # Running on localhost with debug disabled for SonarQube compliance
    app.run(host='127.0.0.1', port=5000, debug=False)