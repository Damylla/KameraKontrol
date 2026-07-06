from flask import Flask, Response, jsonify, render_template
import cv2
from ultralytics import YOLO
import threading
import time

app = Flask(__name__)

print("Loading YOLO...")
model = YOLO("yolov8n.pt")

cap = None
current_frame = None
person_count = 0
is_running = False
frame_lock = threading.Lock()

def init_camera():
    global cap
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Camera not found!")
        return False
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("Atech USB webcam connected!")
    return True

def process_camera():
    global current_frame, person_count, is_running, cap
    print("Camera processing thread started...")
    
    while is_running:
        ret, frame = cap.read()
        if not ret:
            print("No frame received...")
            time.sleep(0.1)
            continue
        
        try:
            results = model(frame)
            person_count_local = 0
            for r in results[0].boxes:
                if int(r.cls[0]) == 0:
                    person_count_local += 1
            person_count = person_count_local
            
            annotated_frame = results[0].plot()
            cv2.putText(annotated_frame, f"Total: {person_count_local} people", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2, cv2.LINE_AA)
            
            with frame_lock:
                current_frame = annotated_frame
        except Exception as e:
            print(f"YOLO error: {e}")
            time.sleep(0.1)

def generate_frames():
    global current_frame
    while True:
        with frame_lock:
            if current_frame is not None:
                ret, buffer = cv2.imencode('.jpg', current_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                time.sleep(0.05)
                continue
        time.sleep(0.03)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/person_count')
def get_person_count():
    return jsonify({'count': person_count})

if __name__ == '__main__':
    if init_camera():
        is_running = True
        thread = threading.Thread(target=process_camera)
        thread.daemon = True
        thread.start()
        print("Camera thread started!")
    else:
        print("Camera could not be started!")
    
    print("Flask server starting...")
    app.run(debug=False, threaded=True, host='0.0.0.0', port=5000)