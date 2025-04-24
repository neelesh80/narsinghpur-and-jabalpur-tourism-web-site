from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import os
import jwt
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, static_folder='Jabalpur & Narsinghpur Tourism fronend design')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'tourisam and traveling website'  # Change this to a secure secret key
app.config['SMTP_SERVER'] = 'smtp.gmail.com'
app.config['SMTP_PORT'] = 587
app.config['SMTP_USERNAME'] = 'ayushsonisoni49@gmail.com'  # Change this to your email
app.config['SMTP_PASSWORD'] = 'fbsauogawlmgopxn'  # Change this to your app password

# Database initialization
def init_db():
    conn = sqlite3.connect('tourism.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_verified BOOLEAN DEFAULT 0,
            otp TEXT,
            otp_expiry TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create bookings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            destination TEXT NOT NULL,
            date TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create testimonials table
    c.execute('''
        CREATE TABLE IF NOT EXISTS testimonials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create contact messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Booking endpoint
@app.route('/api/book', methods=['POST'])
def book_trip():
    data = request.json
    
    if not all(key in data for key in ['service', 'destination', 'date', 'name', 'email']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = sqlite3.connect('tourism.db')
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO bookings (service, destination, date, name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['service'], data['destination'], data['date'], data['name'], data['email']))
        
        conn.commit()
        return jsonify({'message': 'Booking successful'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Testimonial endpoint
@app.route('/api/testimonial', methods=['POST'])
def add_testimonial():
    data = request.json
    
    if not all(key in data for key in ['name', 'email', 'message']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = sqlite3.connect('tourism.db')
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO testimonials (name, email, message)
            VALUES (?, ?, ?)
        ''', (data['name'], data['email'], data['message']))
        
        conn.commit()
        return jsonify({'message': 'Testimonial added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Contact form endpoint
@app.route('/api/contact', methods=['POST'])
def submit_contact():
    data = request.json
    
    if not all(key in data for key in ['name', 'email', 'message']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = sqlite3.connect('tourism.db')
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO contact_messages (name, email, message)
            VALUES (?, ?, ?)
        ''', (data['name'], data['email'], data['message']))
        
        conn.commit()
        return jsonify({'message': 'Message sent successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_confirmation_email(email, token):
    otp = generate_otp()
    msg = MIMEMultipart()
    msg['From'] = app.config['SMTP_USERNAME']
    msg['To'] = email
    msg['Subject'] = 'Email Verification OTP'
    
    body = f'Your OTP for email verification is: {otp}\n\nThis OTP will expire in 10 minutes.'
    msg.attach(MIMEText(body, 'plain'))
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
            server.starttls()
            server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
            server.send_message(msg)
            server.quit()
            
            # Store OTP in database with expiration
            conn = sqlite3.connect('tourism.db')
            c = conn.cursor()
            c.execute('UPDATE users SET otp = ?, otp_expiry = ? WHERE email = ?',
                     (otp, datetime.utcnow() + timedelta(minutes=10), email))
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f'Error sending email (attempt {retry_count + 1}): {str(e)}')
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(2)  # Wait 2 seconds before retrying
    
    return False

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    
    if not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = sqlite3.connect('tourism.db')
    c = conn.cursor()
    
    try:
        # Check if user already exists
        c.execute('SELECT * FROM users WHERE email = ?', (data['email'],))
        if c.fetchone() is not None:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Hash password
        hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Insert new user
        c.execute('''
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        ''', (data['username'], data['email'], hashed.decode('utf-8')))
        
        conn.commit()
        
        # Generate confirmation token
        token = jwt.encode(
            {'email': data['email'], 'exp': datetime.utcnow() + timedelta(hours=24)},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        # Send confirmation email
        if send_confirmation_email(data['email'], token):
            return jsonify({'message': 'Signup successful. Please check your email for confirmation.'}), 201
        else:
            return jsonify({'error': 'Failed to send confirmation email'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    
    if not all(key in data for key in ['email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = sqlite3.connect('tourism.db')
    c = conn.cursor()
    
    try:
        c.execute('SELECT * FROM users WHERE email = ?', (data['email'],))
        user = c.fetchone()
        
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user[3].encode('utf-8')):
            return jsonify({'error': 'Invalid password'}), 401
        
        if not user[4]:  # Check if email is verified
            return jsonify({'error': 'Please verify your email first'}), 401
        
        # Generate access token
        token = jwt.encode(
            {'user_id': user[0], 'exp': datetime.utcnow() + timedelta(days=1)},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'username': user[1]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    
    if not all(key in data for key in ['email', 'otp']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = sqlite3.connect('tourism.db')
    c = conn.cursor()
    
    try:
        c.execute('SELECT otp, otp_expiry FROM users WHERE email = ?', (data['email'],))
        user = c.fetchone()
        
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        
        stored_otp, otp_expiry = user
        
        if stored_otp != data['otp']:
            return jsonify({'error': 'Invalid OTP'}), 400
        
        if datetime.utcnow() > datetime.fromisoformat(otp_expiry):
            return jsonify({'error': 'OTP has expired'}), 400
        
        c.execute('UPDATE users SET is_verified = 1, otp = NULL, otp_expiry = NULL WHERE email = ?', (data['email'],))
        conn.commit()
        
        return jsonify({'message': 'Email verified successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)