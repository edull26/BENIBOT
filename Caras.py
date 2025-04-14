import cv2
import numpy as np
import time
import firebase_admin
from firebase_admin import credentials, db

# ==== Inicializar Firebase ====
cred = credentials.Certificate("C:/Users/leong/OneDrive/Documentos/BENIVOZ/benibot26-firebase-adminsdk-fbsvc-3728821fe3.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://benibot26-default-rtdb.firebaseio.com/'
})

# ==== Función para dibujar caras ====
def draw_face(expression, blink=False):
    face = np.ones((360, 640, 3), dtype=np.uint8) * 255  # Pantalla horizontal

    # Cara base centrada
    cv2.circle(face, (320, 180), 150, (255, 255, 153), -1)

    # Ojos (ajustados a horizontal)
    if blink:
        cv2.line(face, (250, 150), (270, 150), (0, 0, 0), 4)
        cv2.line(face, (370, 150), (390, 150), (0, 0, 0), 4)
    else:
        cv2.circle(face, (260, 150), 15, (0, 0, 0), -1)
        cv2.circle(face, (380, 150), 15, (0, 0, 0), -1)

    # Boca y cejas según expresión
    if expression == "happy":
        cv2.ellipse(face, (320, 230), (50, 25), 0, 0, 180, (0, 0, 0), 4)
    elif expression == "sad":
        cv2.ellipse(face, (320, 250), (50, 25), 0, 0, -180, (0, 0, 0), 4)
    elif expression == "angry":
        cv2.line(face, (230, 130), (270, 145), (0, 0, 0), 4)
        cv2.line(face, (370, 145), (410, 130), (0, 0, 0), 4)
        cv2.line(face, (270, 240), (370, 240), (0, 0, 0), 4)
    elif expression == "neutral":
        cv2.line(face, (270, 240), (370, 240), (0, 0, 0), 3)
    elif expression == "gel":
        cv2.ellipse(face, (320, 230), (50, 25), 0, 0, 180, (255, 0, 0), 4)
        cv2.putText(face, "💧", (300, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 2)

    return face

# ==== Mostrar expresión por unos segundos ====
def show_expression(expression, duration=3):
    start = time.time()
    while time.time() - start < duration:
        face = draw_face(expression)
        cv2.imshow("BeniBot", face)
        if cv2.waitKey(100) & 0xFF == 27:
            break

# ==== Loop principal con parpadeo en "neutral" ====
def main_loop():
    cv2.namedWindow("BeniBot", cv2.WINDOW_AUTOSIZE)

    blink = False
    last_blink_time = time.time()
    blink_duration = 0.15
    blink_interval = 2.5

    while True:
        actions_ref = db.reference("/Acciones").get()

        if actions_ref.get("Saludo"):
            show_expression("happy")
            db.reference("/Acciones/Saludo").set(False)

        elif actions_ref.get("Gel"):
            show_expression("gel")
            db.reference("/Acciones/Gel").set(False)

        elif actions_ref.get("Triste"):
            show_expression("sad")
            db.reference("/Acciones/Triste").set(False)

        elif actions_ref.get("Enojado"):
            show_expression("angry")
            db.reference("/Acciones/Enojado").set(False)

        else:
            current_time = time.time()

            if not blink and current_time - last_blink_time > blink_interval:
                blink = True
                blink_start = current_time
            elif blink and current_time - blink_start > blink_duration:
                blink = False
                last_blink_time = current_time

            face = draw_face("neutral", blink)
            cv2.imshow("BeniBot", face)

        if cv2.waitKey(30) & 0xFF == 27:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main_loop()
