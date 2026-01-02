# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import psycopg2
# from psycopg2 import pool
# import redis
# import os
# import logging

# app = Flask(__name__)
# CORS(app)

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# DB_HOST = os.getenv('DB_HOST', 'db-service')
# DB_NAME = os.getenv('DB_NAME', 'mydb')
# DB_USER = os.getenv('DB_USER', 'user')
# DB_PASS = os.getenv('DB_PASS', 'password')
# REDIS_HOST = os.getenv('REDIS_HOST', 'redis-service')


# try:
#     db_pool = psycopg2.pool.SimpleConnectionPool(
#         1, 10,
#         host=DB_HOST,
#         database=DB_NAME,
#         user=DB_USER,
#         password=DB_PASS
#     )
#     logger.info("PostgreSQL connection pool created successfully")
# except Exception as e:
#     logger.error(f"Error creating DB pool: {e}")

# # Connect to Redis
# cache = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# @app.route('/check-user', methods=['POST'])
# def check_user():
#     data = request.get_json()
#     if not data or 'username' not in data or 'phone' not in data:
#         return jsonify({"error": "Missing username or phone"}), 400

#     username = data.get('username')
#     phone = data.get('phone')

#     try:
#         # 1. Check Redis Cache
#         cached_user = cache.get(username)
#         if cached_user == phone:
#             return jsonify({"message": "Welcome back! (From Cache)"}), 200

#         # 2. Check Database using the pool
#         conn = db_pool.getconn()
#         with conn.cursor() as cur:
            
#             cur.execute("SELECT phone FROM users WHERE username = %s", (username,))
#             result = cur.fetchone()

#             if result:
#                 cache.set(username, phone)
#                 return jsonify({"message": "Welcome back! (From DB)"}), 200
#             else:
#                 # 3. Register New User
#                 cur.execute("INSERT INTO users (username, phone) VALUES (%s, %s)", (username, phone))
#                 conn.commit()
#                 cache.set(username, phone)
#                 return jsonify({"message": "User registered successfully!"}), 201

#     except Exception as e:
#         logger.error(f"Database error: {e}")
#         return jsonify({"error": "Internal server error"}), 500
#     finally:
        
#         if conn:
#             db_pool.putconn(conn)

# if __name__ == '__main__':
    
#     app.run(host='0.0.0.0', port=5000)








from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import pool
import redis
import os
import logging

# Configure logging for better traceability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Environment variables with safe defaults
DB_HOST = os.getenv('DB_HOST', 'db-service')
DB_NAME = os.getenv('DB_NAME', 'mydb')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASS = os.getenv('DB_PASS', 'password')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis-service')

# Initialize Database Connection Pool
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    logger.info("Database connection pool initialized.")
except Exception as e:
    logger.error(f"Database connection error: {e}")

# Initialize Redis Cache
cache = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

@app.route('/check-user', methods=['POST'])
def check_user():
    data = request.get_json()
    
    # Input validation to prevent null pointer exceptions
    if not data or 'username' not in data or 'phone' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    username = data.get('username')
    phone = data.get('phone')

    conn = None
    try:
        # 1. Check Redis Cache
        cached_user = cache.get(username)
        if cached_user == phone:
            return jsonify({"message": "Success from cache"}), 200

        # 2. Database operation with Parameterized Query (Fixes SQL Injection)
        conn = db_pool.getconn()
        with conn.cursor() as cur:
            # Using %s prevents SQL injection vulnerabilities flagged by SonarQube
            cur.execute("SELECT phone FROM users WHERE username = %s", (username,))
            result = cur.fetchone()

            if result:
                cache.set(username, phone)
                return jsonify({"message": "Success from database"}), 200
            else:
                # 3. Securely register new user
                cur.execute("INSERT INTO users (username, phone) VALUES (%s, %s)", (username, phone))
                conn.commit()
                cache.set(username, phone)
                return jsonify({"message": "User created successfully"}), 201

    except Exception as e:
        logger.error(f"Application error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        # Ensure connection is returned to the pool (Fixes Resource Leak)
        if conn:
            db_pool.putconn(conn)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)