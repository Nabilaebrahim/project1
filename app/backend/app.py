from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import pool
import redis
import os
import logging
import atexit # إضافة عشان نقفل الـ pool صح

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv('DB_HOST', 'db-service')
DB_NAME = os.getenv('DB_NAME', 'mydb')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASS = os.getenv('DB_PASS') 
REDIS_HOST = os.getenv('REDIS_HOST', 'redis-service')

# إعداد الـ Pool كـ متغير Global عشان السونار يطمن لإدارة الموارد
db_pool = None

def init_db():
    global db_pool
    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10, host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
        )
        logger.info("Database pool initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")

init_db()

# إغلاق الـ pool عند قفل البرنامج (لحل مشكلة الـ Reliability في السونار)
@atexit.register
def close_db_pool():
    if db_pool:
        db_pool.closeall()
        logger.info("Database pool closed")

@app.route('/check-user', methods=['POST'])
def check_user():
    data = request.get_json()
    if not data or 'username' not in data or 'phone' not in data:
        return jsonify({"error": "Invalid input data"}), 400

    username = data.get('username')
    phone = data.get('phone')

    conn = None
    try:
        # استخدام Redis بـ Timeout عشان السونار ميعتبرهاش ثغرة أداء
        cache = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True, socket_timeout=5)
        
        cached_phone = cache.get(username)
        if cached_phone == phone:
            return jsonify({"message": "Welcome back! (From Cache)"}), 200

        if not db_pool:
            return jsonify({"error": "Database not initialized"}), 500

        conn = db_pool.getconn()
        with conn.cursor() as cur:
            cur.execute("SELECT phone FROM users WHERE username = %s", (username,))
            result = cur.fetchone()

            if result:
                cache.set(username, phone, ex=3600)
                return jsonify({"message": "Welcome back! (From DB)"}), 200
            
            cur.execute("INSERT INTO users (username, phone) VALUES (%s, %s)", (username, phone))
            conn.commit()
            cache.set(username, phone, ex=3600)
            return jsonify({"message": "User registered successfully!"}), 201
                
    except Exception as e:
        logger.error(f"Service error: {e}")
        return jsonify({"error": "Service unavailable"}), 500
    finally:
        if conn:
            db_pool.putconn(conn)

if __name__ == '__main__':
    # تأكدي إن مفيش أي باسوورد مكتوب هنا حتى في الكومنتس
    app.run(host='127.0.0.1', port=5000, debug=False)