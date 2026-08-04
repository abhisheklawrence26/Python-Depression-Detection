import cv2
import time
import base64
import numpy as np
from deepface import DeepFace

# Face cascade classifier setup
faceCascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)


def decode_image(image_input):
    """
    Decodes base64 string or raw bytes into OpenCV BGR frame.
    """
    if isinstance(image_input, str):
        if "," in image_input:
            image_input = image_input.split(",")[1]
        image_bytes = base64.b64decode(image_input)
    else:
        image_bytes = image_input

    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return frame


def analyze_frame(frame):
    """
    Analyzes a single OpenCV image frame for faces and emotions.
    Returns dict with bounding box, emotion probabilities, and dominant emotion.
    """
    if frame is None:
        raise ValueError("Invalid frame image data")

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(100, 100)
    )

    if len(faces) == 0:
        analysis_input = frame
        bbox = None
    else:
        x, y, w, h = faces[0]
        analysis_input = frame[y:y+h, x:x+w]
        bbox = (int(x), int(y), int(w), int(h))

    results = DeepFace.analyze(
        analysis_input,
        actions=['emotion'],
        detector_backend='opencv',
        enforce_detection=False
    )

    if isinstance(results, list):
        result = results[0]
    else:
        result = results

    raw_emotions = result.get('emotion', {})
    dominant_emotion = result.get('dominant_emotion', 'neutral')

    emotion_dict = {}
    for emo, score in raw_emotions.items():
        emotion_dict[emo] = round(float(score), 2)

    happy_score = emotion_dict.get("happy", 0.0)
    sad_score = emotion_dict.get("sad", 0.0)
    neutral_score = emotion_dict.get("neutral", 0.0)

    return {
        "bbox": bbox,
        "emotions": emotion_dict,
        "dominant_emotion": dominant_emotion,
        "confidence": round(float(emotion_dict.get(dominant_emotion, 0)), 2),
        "happy": happy_score,
        "sad": sad_score,
        "neutral": neutral_score,
    }


def calculate_emotion_percentages(emotion_count):
    """
    Calculates percentage for each emotion given an emotion_count dict.
    """
    total = sum(emotion_count.values())
    emotion_percentage = {}

    for emotion, count in emotion_count.items():
        if total > 0:
            percentage = (count / total) * 100
        else:
            percentage = 0.0
        emotion_percentage[emotion] = round(percentage, 2)

    dominant_emotion = max(emotion_percentage, key=emotion_percentage.get) if emotion_percentage else "neutral"

    return emotion_percentage, dominant_emotion


def run_standalone_cam():
    """
    Standalone function to run webcam emotion detection directly.
    """
    webcam = cv2.VideoCapture(0)
    if not webcam.isOpened():
        print("Could not open webcam")
        return

    emotion_count = {
        "happy": 0, "sad": 0, "neutral": 0, "angry": 0,
        "fear": 0, "surprise": 0, "disgust": 0
    }

    start_time = time.time()
    print("Starting webcam emotion analysis for 60 seconds...")

    while True:
        ret, frame = webcam.read()
        if not ret:
            print("Could not read frame")
            break

        try:
            analysis = analyze_frame(frame)
            bbox = analysis.get("bbox")
            dominant = analysis.get("dominant_emotion")
            confidence = analysis.get("confidence")

            if dominant in emotion_count:
                emotion_count[dominant] += 1

            if bbox:
                x, y, w, h = bbox
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            text = f"{dominant} ({confidence:.2f}%)"
            cv2.putText(frame, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        except Exception as e:
            print("Frame error:", e)

        remaining = max(0, 60 - int(time.time() - start_time))
        cv2.putText(frame, f"Time Left: {remaining}s", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.imshow("Emotion Detection", frame)

        if time.time() - start_time >= 60 or (cv2.waitKey(1) & 0xFF == ord('q')):
            break

    webcam.release()
    cv2.destroyAllWindows()

    emotion_percentage, dominant_emotion = calculate_emotion_percentages(emotion_count)

    print("\nEmotion Percentage:")
    for emo, pct in emotion_percentage.items():
        print(f"{emo} : {pct} %")

    print("\nFinal Emotion:", dominant_emotion)

    try:
        import requests
        response = requests.post(
            "http://127.0.0.1:8000/save-face-result/",
            json={
                "happy": emotion_percentage.get("happy", 0),
                "sad": emotion_percentage.get("sad", 0),
                "neutral": emotion_percentage.get("neutral", 0),
                "dominant_emotion": dominant_emotion
            }
        )
        print("Response status:", response.status_code)
    except Exception as e:
        print("Failed to post to Django server:", e)


if __name__ == "__main__":
    run_standalone_cam()