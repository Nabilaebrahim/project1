from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import pool
import redis
import os
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DB_HOST = os.getenv('DB_HOST', 'db-service')
DB_NAME = os.getenv('DB_NAME', 'mydb')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASS = os.getenv('DB_PASS', 'password')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis-service')


try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    logger.info("PostgreSQL connection pool created successfully")
except Exception as e:
    logger.error(f"Error creating DB pool: {e}")

# Connect to Redis
cache = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

@app.route('/check-user', methods=['POST'])
def check_user():
    data = request.get_json()
    if not data or 'username' not in data or 'phone' not in data:
        return jsonify({"error": "Missing username or phone"}), 400

    username = data.get('username')
    phone = data.get('phone')

    try:
        # 1. Check Redis Cache
        cached_user = cache.get(username)
        if cached_user == phone:
            return jsonify({"message": "Welcome back! (From Cache)"}), 200

        # 2. Check Database using the pool
        conn = db_pool.getconn()
        with conn.cursor() as cur:
            
            cur.execute("SELECT phone FROM users WHERE username = %s", (username,))
            result = cur.fetchone()

            if result:
                cache.set(username, phone)
                return jsonify({"message": "Welcome back! (From DB)"}), 200
            else:
                # 3. Register New User
                cur.execute("INSERT INTO users (username, phone) VALUES (%s, %s)", (username, phone))
                conn.commit()
                cache.set(username, phone)
                return jsonify({"message": "User registered successfully!"}), 201

    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        
        if conn:
            db_pool.putconn(conn)

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5000)