import os, json, uuid, shutil, subprocess
from datetime import date, timedelta
from flask import Flask, request, jsonify, render_template, send_from_directory
import urllib.request
import urllib.error

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'server-data')
BOOKS_DIR = os.path.join(DATA_DIR, 'books')

def data_file(name):
    return os.path.join(DATA_DIR, name)

DEFAULTS = {
    'homework.json': [],
    'tests.json': [],
    'streak.json': {"streak": 0, "lastCheckin": ""},
    'books.json': []
}

def read_data(name):
    path = data_file(name)
    if not os.path.exists(path):
        write_data(name, DEFAULTS[name])
        return DEFAULTS[name]
    with open(path) as f:
        return json.load(f)

def write_data(name, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(data_file(name), 'w') as f:
        json.dump(data, f, indent=2)

# --- Homework ---
@app.get('/api/homework')
def get_homework():
    return jsonify(read_data('homework.json'))

@app.post('/api/homework')
def add_homework():
    body = request.json
    items = read_data('homework.json')
    item = {'id': str(uuid.uuid4()), 'subject': body['subject'],
            'description': body['description'], 'dueDate': body['dueDate'],
            'done': False, 'createdAt': str(date.today())}
    items.append(item)
    write_data('homework.json', items)
    return jsonify(item), 201

@app.route('/api/homework/<id>', methods=['PATCH'])
def toggle_homework(id):
    items = read_data('homework.json')
    for item in items:
        if item['id'] == id:
            item['done'] = not item['done']
            write_data('homework.json', items)
            return jsonify(item)
    return jsonify({'error': 'not found'}), 404

@app.route('/api/homework/<id>', methods=['DELETE'])
def delete_homework(id):
    items = [i for i in read_data('homework.json') if i['id'] != id]
    write_data('homework.json', items)
    return jsonify({'ok': True})

# --- Tests ---
@app.get('/api/tests')
def get_tests():
    return jsonify(read_data('tests.json'))

@app.post('/api/tests')
def add_test():
    body = request.json
    tests = read_data('tests.json')
    test = {'id': str(uuid.uuid4()), 'subject': body['subject'],
            'topic': body['topic'], 'testDate': body['testDate'],
            'createdAt': str(date.today())}
    tests.append(test)
    write_data('tests.json', tests)
    return jsonify(test), 201

@app.route('/api/tests/<id>', methods=['DELETE'])
def delete_test(id):
    tests = [t for t in read_data('tests.json') if t['id'] != id]
    write_data('tests.json', tests)
    return jsonify({'ok': True})

# --- Streak ---
@app.get('/api/streak')
def get_streak():
    return jsonify(read_data('streak.json'))

@app.post('/api/streak/checkin')
def checkin():
    s = read_data('streak.json')
    today = str(date.today())
    if s.get('lastCheckin') != today:
        s['streak'] = s.get('streak', 0) + 1
        s['lastCheckin'] = today
        write_data('streak.json', s)
    return jsonify(s)

# --- Books ---
@app.get('/api/books')
def get_books():
    return jsonify(read_data('books.json'))

@app.route('/api/books/<id>', methods=['DELETE'])
def delete_book(id):
    books = read_data('books.json')
    book = next((b for b in books if b['id'] == id), None)
    if book and book.get('textFile') and os.path.exists(book['textFile']):
        os.remove(book['textFile'])
    books = [b for b in books if b['id'] != id]
    write_data('books.json', books)
    return jsonify({'ok': True})

@app.post('/api/books/upload')
def upload_book():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    f = request.files['file']
    subject = request.form.get('subject', 'Maths')
    if not f.filename.lower().endswith('.pdf'):
        return jsonify({'success': False, 'error': 'Please upload a PDF file'}), 400
    f.seek(0, 2)
    size = f.tell()
    f.seek(0)
    if size > 50 * 1024 * 1024:
        return jsonify({'success': False, 'error': 'File too large. Maximum size is 50MB'}), 400
    ts = str(int(__import__('time').time()))
    pdf_path = f'/tmp/upload_{ts}.pdf'
    txt_path = os.path.join(BOOKS_DIR, f'{subject}-{ts}.txt')
    os.makedirs(BOOKS_DIR, exist_ok=True)
    f.save(pdf_path)
    if not shutil.which('pdftotext'):
        subprocess.run(['apt-get', 'install', '-y', 'poppler-utils'], capture_output=True)
    subprocess.run(['pdftotext', pdf_path, txt_path], capture_output=True)
    pages = 0
    try:
        r = subprocess.run(['pdfinfo', pdf_path], capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if 'Pages:' in line:
                pages = int(line.split(':')[1].strip())
    except Exception:
        pass
    title = f.filename.replace('.pdf', '')
    book = {'id': str(uuid.uuid4()), 'subject': subject, 'title': title,
            'pages': pages, 'uploadDate': str(date.today()), 'textFile': txt_path}
    books = read_data('books.json')
    books.append(book)
    write_data('books.json', books)
    try:
        os.remove(pdf_path)
    except Exception:
        pass
    return jsonify({'success': True, 'id': book['id'], 'title': title,
                    'pages': pages, 'message': f'Textbook uploaded! {pages} pages ready for study.'})

# --- Chat ---
@app.post('/api/chat')
def chat():
    try:
        body = request.json
        messages = body.get('messages', [])
        subject = body.get('subject', 'Maths')
        topic = body.get('topic', '')
        textbook_context = ''
        books = read_data('books.json')
        book = next((b for b in books if b['subject'] == subject and os.path.exists(b.get('textFile',''))), None)
        if book:
            with open(book['textFile']) as tf:
                text = tf.read()
            idx = text.lower().find(topic.lower())
            if idx >= 0:
                start = max(0, idx - 500)
                end = min(len(text), idx + 1500)
                textbook_context = f'\n\nRelevant content from Simise\'s actual textbook:\n{text[start:end]}\n\nUse this to make your guidance more relevant, but still do not give direct answers.'
        system_prompt = f"""You are Simise's friendly study buddy. Simise is a Grade 8 South African student (CAPS curriculum) struggling with Maths and Afrikaans.
Rules:
1. NEVER give direct answers to homework or test questions
2. Ask guiding questions to help Simise think it through himself
3. Break problems into smaller steps - one step at a time
4. Celebrate warmly when he gets it right ("Yes! You've got it! 🎉")
5. Give hints that nudge without giving away answers
6. Keep language simple and encouraging - he's 13/14 years old
7. If he asks "just tell me the answer", say "I know it's tempting, but you'll remember it SO much better if you work it out. Let's try together..."
8. For Maths: work through the method step by step
9. For Afrikaans: focus on language structures and vocabulary in context
10. Always end with a question or next step to keep Simise engaged
11. Use South African context in examples (rand, braai, cricket, rugby)
12. Keep responses SHORT - max 3-4 sentences. Simise is a teenager.
Currently helping with: {subject} - {topic}{textbook_context}"""
        payload = json.dumps({
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": system_prompt}] + messages
        }).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read())
        reply = result["choices"][0]["message"]["content"]
        return jsonify({"reply": reply, "error": None})
    except Exception as e:
        return jsonify({"reply": None, "error": "AI service not configured. Please add OpenAI credentials in Settings > Integrations."})

@app.get('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)



@app.post('/api/report/send')
def send_weekly_report():
    try:
        import json as _json
        hw = read_data('homework.json')
        tests = read_data('tests.json')
        streak_data = read_data('streak.json')
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_start_str = str(week_start)
        today_str = str(today)
        this_week_hw = [h for h in hw if h.get('dueDate','') >= week_start_str]
        done = sum(1 for h in this_week_hw if h.get('done'))
        overdue = sum(1 for h in this_week_hw if not h.get('done') and h.get('dueDate','') < today_str)
        pending = sum(1 for h in this_week_hw if not h.get('done') and h.get('dueDate','') >= today_str)
        streak = streak_data.get('streak', 0) if isinstance(streak_data, dict) else 0
        upcoming = sorted([t for t in tests if t.get('date','') >= today_str], key=lambda x: x.get('date',''))[:5]
        tests_rows = ''.join(
            f"<tr><td style='padding:6px 12px;'>{t.get('subject','')}</td>"
            f"<td style='padding:6px 12px;'>{t.get('topic','')}</td>"
            f"<td style='padding:6px 12px;'>{t.get('date','')}</td></tr>"
            for t in upcoming
        ) or "<tr><td colspan='3' style='padding:6px 12px;color:#718096;'>No upcoming tests</td></tr>"
        streak_msg = ('<p style="color:#7ED321;">Great consistency this week! 🌟</p>' if streak >= 5
                      else '<p style="color:#F5A623;">Keep encouraging Simise to check in daily!</p>' if streak > 0
                      else '<p style="color:#E74C3C;">No streak yet — try to check in daily!</p>')
        html_body = f"""<div style="font-family:sans-serif;max-width:480px;margin:0 auto;background:#F0F4F8;padding:24px;border-radius:12px;">
  <h2 style="color:#4A90D9;margin-bottom:4px;">📚 Simise's Weekly Study Report</h2>
  <p style="color:#718096;margin-top:0;">Week of {week_start.strftime('%d %B %Y')}</p>
  <div style="background:#fff;border-radius:10px;padding:16px;margin-bottom:16px;">
    <h3 style="margin-top:0;">📌 Homework This Week</h3>
    <p>✅ Completed: <strong>{done}</strong> &nbsp; ❌ Overdue: <strong>{overdue}</strong> &nbsp; ⏳ Pending: <strong>{pending}</strong></p>
  </div>
  <div style="background:#fff;border-radius:10px;padding:16px;margin-bottom:16px;">
    <h3 style="margin-top:0;">🔥 Study Streak: {streak} day{"s" if streak!=1 else ""}</h3>
    {streak_msg}
  </div>
  <div style="background:#fff;border-radius:10px;padding:16px;margin-bottom:16px;">
    <h3 style="margin-top:0;">📅 Upcoming Tests</h3>
    <table style="width:100%;border-collapse:collapse;">
      <tr style="background:#F7FAFC;">
        <th style="padding:6px 12px;text-align:left;">Subject</th>
        <th style="padding:6px 12px;text-align:left;">Topic</th>
        <th style="padding:6px 12px;text-align:left;">Date</th>
      </tr>
      {tests_rows}
    </table>
  </div>
  <p style="color:#A0AEC0;font-size:.8rem;text-align:center;">Sent automatically by Simise's Study Buddy 📖</p>
</div>"""
        payload = _json.dumps({
            "personalizations": [{"to": [{"email": "taluxury@gmail.com"}]}],
            "from": {"email": "noreply@studybuddy.app", "name": "Simise's Study Buddy"},
            "subject": f"📚 Simise's Weekly Study Report — {week_start.strftime('%d %b %Y')}",
            "content": [{"type": "text/html", "value": html_body}]
        }).encode()
        req = urllib.request.Request(
            'https://api.sendgrid.com/v3/mail/send',
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req) as resp:
            return jsonify({'ok': True, 'status': resp.status}), 200
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return jsonify({'error': f'Email service error: {e.code} {body}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.get('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
