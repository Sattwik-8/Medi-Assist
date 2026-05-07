import os
import sqlite3
import smtplib
import uuid
import pandas as pd
from datetime import datetime
from email.mime.text       import MIMEText
from email.mime.multipart  import MIMEMultipart
from functools import wraps

from flask import Flask, render_template, request, jsonify, redirect, send_from_directory, session, url_for
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

# ── Load .env ─────────────────────────────────────────────────────────────────
load_dotenv()

# ── App modules ───────────────────────────────────────────────────────────────
from app.data  import helper, severity_map as _sev_ref
from app.model import get_top3_predictions, severity_map as model_sev, symptoms_dict
from app.nlp   import extract_symptoms_from_text
from app.chat  import build_chat_response
from app.i18n  import SUPPORTED_LANGS
from app.safety import confidence_note, detect_emergency, emergency_message

# ── Wire severity_map into model (avoids circular import) ─────────────────────
import app.model as _model_mod
import app.data  as _data_mod
_model_mod.severity_map = _data_mod.severity_map

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

DB_PATH = os.path.join(app.root_path, 'medi_assist.db')
ALLOWED_UPLOADS = {'png', 'jpg', 'jpeg', 'webp', 'pdf'}


@app.after_request
def add_local_preview_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                disease TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                original_name TEXT NOT NULL,
                stored_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login', next=request.path))
        return view(*args, **kwargs)
    return wrapped


def allowed_upload(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_UPLOADS


init_db()


# ── Helper: send email via Gmail SMTP ─────────────────────────────────────────
def send_contact_email(name: str, email: str, subject: str, message: str) -> bool:
    """Send contact form submission to configured inbox. Returns True on success."""
    gmail_user     = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
    recipient      = os.environ.get('CONTACT_RECIPIENT') or 'sattwik.hit@gmail.com'

    if not gmail_user or not gmail_password:
        return False

    gmail_user = gmail_user.strip()
    gmail_password = gmail_password.replace(' ', '').strip()
    recipient = recipient.strip()

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"[Medi-Assist Contact] {subject}"
    msg['From']    = gmail_user
    msg['To']      = recipient

    body = f"""
New contact form submission from Medi-Assist:

Name    : {name}
Email   : {email}
Subject : {subject}

Message :
{message}
"""
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, recipient, msg.as_string())
        return True
    except Exception as e:
        print(f"SMTP error: {e}")
        return False


# ════════════════════════════════════════════════════════════
#  Routes
# ════════════════════════════════════════════════════════════

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('auth.html', mode='signup', error=None)

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    if not name or not email or len(password) < 6:
        return render_template('auth.html', mode='signup', error='Enter your name, email, and a password with at least 6 characters.')

    try:
        with get_db() as db:
            cursor = db.execute(
                "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (name, email, generate_password_hash(password), datetime.utcnow().isoformat())
            )
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return render_template('auth.html', mode='signup', error='An account already exists with this email.')

    session['user_id'] = user_id
    session['user_name'] = name
    session['user_email'] = email
    return redirect(url_for('chat'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth.html', mode='login', error=None)

    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if not user or not check_password_hash(user['password_hash'], password):
        return render_template('auth.html', mode='login', error='Invalid email or password.')

    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    return redirect(request.args.get('next') or url_for('chat'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', languages=SUPPORTED_LANGS, user=session)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/developer')
def developer():
    return render_template('developer.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')


@app.route('/symptoms')
def symptoms():
    readable = sorted(symptom.replace('_', ' ') for symptom in symptoms_dict.keys())
    return jsonify({'symptoms': readable})


# ── Predict API (form-based, returns full report) ─────────────────────────────
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data     = request.get_json(force=True)
        raw_symptoms = data.get('symptoms', [])
        emergency = detect_emergency(" ".join(str(item) for item in raw_symptoms))
        if emergency:
            return jsonify({
                'error': emergency_message('en'),
                'emergency': True,
            })

        symptoms = []
        for item in raw_symptoms:
            symptom = str(item).strip().lower().replace(' ', '_')
            if symptom in symptoms_dict:
                symptoms.append(symptom)
                continue

            extracted = extract_symptoms_from_text(str(item).replace('_', ' '))
            symptoms.extend(extracted)

        symptoms = list(dict.fromkeys(symptoms))

        if not symptoms:
            return jsonify({'error': 'No symptoms provided.'})

        top3, unrecognized = get_top3_predictions(symptoms)

        if not top3:
            return jsonify({'error': 'None of the symptoms were recognized.'})

        # Full details for primary disease
        primary      = top3[0]
        disease      = primary['disease']
        desc, pre, med, die, wrk = helper(disease)

        return jsonify({
            'disease':      disease,
            'confidence':   primary['confidence'],
            'severity':     primary['severity'],
            'confidence_note': confidence_note(primary['confidence']),
            'top3':         top3,
            'description':  desc,
            'precautions':  pre,
            'medication':   med,
            'diet':         die,
            'workout':      wrk,
            'unrecognized': unrecognized,
        })
    except Exception as e:
        print(f"PREDICT ERROR: {e}")
        return jsonify({'error': str(e)})


# ── Chat API ──────────────────────────────────────────────────────────────────
@app.route('/chat-message', methods=['POST'])
def chat_message():
    try:
        data         = request.get_json(force=True)
        message      = data.get('message', '').strip()
        last_disease = data.get('last_disease', None)
        lang         = data.get('lang', 'en')
        context      = data.get('context', [])

        if not message:
            return jsonify({
                'text': 'Please type something.',
                'type': 'error'
            })

        result = build_chat_response(
            message,
            last_disease,
            lang,
            context
        )

        return jsonify(result)

    except Exception as e:
        print(f"CHAT ERROR: {e}")

        return jsonify({
            'text': 'Something went wrong. Please try again.',
            'type': 'error'
        })
@app.route('/upload-prescription', methods=['POST'])
@login_required
def upload_prescription():
    file = request.files.get('file')
    note = request.form.get('note', '').strip()

    if not file or not file.filename:
        return jsonify({'success': False, 'error': 'Please choose a prescription or photo to upload.'}), 400

    if not allowed_upload(file.filename):
        return jsonify({'success': False, 'error': 'Allowed files: PNG, JPG, JPEG, WEBP, or PDF.'}), 400

    safe_name = secure_filename(file.filename)
    extension = safe_name.rsplit('.', 1)[1].lower()
    stored_name = f"{session['user_id']}_{uuid.uuid4().hex}.{extension}"
    user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(session['user_id']))
    os.makedirs(user_dir, exist_ok=True)
    file.save(os.path.join(user_dir, stored_name))

    with get_db() as db:
        cursor = db.execute(
            """
            INSERT INTO prescriptions (user_id, original_name, stored_name, file_type, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session['user_id'], safe_name, stored_name, extension, note, datetime.utcnow().isoformat())
        )
        upload_id = cursor.lastrowid

    return jsonify({
        'success': True,
        'upload': {
            'id': upload_id,
            'original_name': safe_name,
            'file_type': extension,
            'note': note,
            'created_at': datetime.utcnow().isoformat(),
        }
    })


@app.route('/prescription/<int:upload_id>')
@login_required
def prescription_file(upload_id):
    with get_db() as db:
        item = db.execute(
            "SELECT * FROM prescriptions WHERE id = ? AND user_id = ?",
            (upload_id, session['user_id'])
        ).fetchone()

    if not item:
        return redirect(url_for('chat'))

    return send_from_directory(
        os.path.join(app.config['UPLOAD_FOLDER'], str(session['user_id'])),
        item['stored_name'],
        as_attachment=False,
        download_name=item['original_name']
    )


# ── Contact form API ──────────────────────────────────────────────────────────
@app.route('/contact-submit', methods=['POST'])
def contact_submit():
    try:
        data    = request.get_json(force=True)
        name    = data.get('name', '').strip()
        email   = data.get('email', '').strip()
        subject = data.get('subject', 'General').strip()
        message = data.get('message', '').strip()

        if not name or not email or not message:
            return jsonify({'success': False, 'error': 'Missing required fields.'})

        success = send_contact_email(name, email, subject, message)

        if success:
            return jsonify({'success': True, 'message': 'Message sent successfully!'})

        print(f"[CONTACT FORM] From: {name} <{email}> | Subject: {subject}\n{message}")
        if os.environ.get('GMAIL_USER') and os.environ.get('GMAIL_APP_PASSWORD'):
            return jsonify({
                'success': False,
                'error': 'Email could not be sent. Please check the Gmail sender and app password.'
            })

        return jsonify({'success': True, 'message': 'Message received! We will get back to you.'})

    except Exception as e:
        print(f"CONTACT ERROR: {e}")
        return jsonify({'success': False, 'error': 'Something went wrong.'})


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'false') == 'true')
