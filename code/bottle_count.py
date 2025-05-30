from ultralytics import YOLO
import cv2
import datetime
import os
import time
import requests

model = YOLO("yolov8s.pt")
TARGET_CLASS = 39
CONF_THRESHOLD = 0.5

save_dir = "bottle_logs"
os.makedirs(save_dir, exist_ok=True)

print("🕓 병 인식 루프 시작 (10분마다 1회)")

while True:
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{now}] ▶ 병 인식 중...")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 카메라 열기 실패")
        time.sleep(600)
        continue

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ 이미지 캡처 실패")
        time.sleep(600)
        continue

    results = model(frame)[0]
    bottle_count = 0

    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        if cls_id != TARGET_CLASS or conf < CONF_THRESHOLD:
            continue

        bottle_count += 1
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label = f"bottle {conf:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("Bottle Detection", frame)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{save_dir}/bottles_{timestamp}_count{bottle_count}.jpg"
    cv2.imwrite(filename, frame)

    print(f"📦 병 개수: {bottle_count}")
    print(f"📁 저장됨: {filename}")

    # 서버 전송
    url = "http://10.10.14.7:5000/upload"
    files = {'file': open(filename, 'rb')}
    data = {'count': bottle_count, 'timestamp': now}

    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("✅ 서버 전송 성공")
        else:
            print(f"❌ 서버 전송 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 서버 전송 예외 발생: {e}")
    finally:
        files['file'].close()

    time.sleep(600)
