import cv2
import easyocr
import ssl
import re
import time

ssl._create_default_https_context = ssl._create_unverified_context

# OCR
reader = easyocr.Reader(['en'], gpu=False)

cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

def extract_plate(text):
    text = text.upper()
    text = "".join(filter(str.isalnum, text))

    match = re.search(r'[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}', text)
    return match.group() if match else ""

last_text = ""
last_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (480, 320))

    current_time = time.time()

    if current_time - last_time > 1:
        results = reader.readtext(frame)

        for (bbox, text, prob) in results:
            plate = extract_plate(text)

            if plate != "":
                last_text = plate
                print("Detected Plate:", plate)

        last_time = current_time
    if last_text != "":
        cv2.putText(frame, last_text, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2)

    cv2.imshow("ANPR Demo", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()