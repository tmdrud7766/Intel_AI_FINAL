from flask import Flask, request
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "uploaded_bottles"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "❌ 파일이 없습니다", 400

    file = request.files['file']
    count = request.form.get('count', 'unknown')
    timestamp = request.form.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    filename = f"bottle_{timestamp.replace(':', '').replace(' ', '_')}_count{count}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    print(f"📥 수신 완료: {filename}")
    print(f"🧮 병 개수: {count}, ⏰ 시간: {timestamp}")
    
    return "✅ 업로드 성공", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
