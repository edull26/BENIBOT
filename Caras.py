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

def draw_face(expression, blink=False, pulse=None, spo2=None):
    h, w = 480, 640
    center = (w // 2, h // 2)
    face_radius = 150

    # 1) Fondo: degradado radial (blanco → verde-menta)
    Y, X = np.ogrid[:h, :w]
    dist = np.sqrt((X - center[0])**2 + (Y - center[1])**2)
    maxd = np.sqrt(center[0]**2 + center[1]**2)
    norm = np.clip(dist / maxd, 0, 1)[:, :, None]
    inner = np.array([255, 255, 255], dtype=np.float32)
    outer = np.array([200, 240, 230], dtype=np.float32)  # verde-menta suave
    bg = (inner * (1 - norm) + outer * norm).astype(np.uint8)

    face = bg.copy()

    # 2) Sombra bajo la cara
    shadow_color = np.array([50, 50, 50], dtype=np.uint8)
    alpha = 0.2
    # dibujo máscara de sombra
    mask = ( (X - (center[0]+10))**2 + (Y - (center[1]+10))**2 ) <= face_radius**2
    face[mask] = (alpha * shadow_color + (1 - alpha) * face[mask]).astype(np.uint8)

    # 3) Cara principal
    cv2.circle(face, center, face_radius, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    # 4) Halo turquesa
    halo_color = (180, 240, 255)
    cv2.circle(face, center, face_radius + 5, halo_color, 3, lineType=cv2.LINE_AA)

    # 5) Antena
    antena_top = (center[0], center[1] - face_radius - 20)
    cv2.line(face, antena_top, (center[0], center[1] - face_radius), halo_color, 2, lineType=cv2.LINE_AA)
    cv2.circle(face, antena_top, 8, halo_color, -1, lineType=cv2.LINE_AA)

    # 6) Ojos
    eye_color = (30, 30, 30)
    shine_color = (255, 255, 255)
    # posiciones
    left_eye = (center[0] - 50, center[1] - 40)
    right_eye = (center[0] + 50, center[1] - 40)

    if blink:
        # párpado curvo
        cv2.ellipse(face, left_eye, (25,8), 0, 0, 180, eye_color, 4, lineType=cv2.LINE_AA)
        cv2.ellipse(face, right_eye, (25,8), 0, 0, 180, eye_color, 4, lineType=cv2.LINE_AA)
    else:
        # iris
        cv2.ellipse(face, left_eye, (25,15), 0, 0, 360, eye_color, -1, lineType=cv2.LINE_AA)
        cv2.ellipse(face, right_eye, (25,15), 0, 0, 360, eye_color, -1, lineType=cv2.LINE_AA)
        # brillo
        cv2.circle(face, (left_eye[0] - 5, left_eye[1] - 5), 5, shine_color, -1, lineType=cv2.LINE_AA)
        cv2.circle(face, (right_eye[0] - 5, right_eye[1] - 5), 5, shine_color, -1, lineType=cv2.LINE_AA)

    # 7) Boca/cejas según expresión
    if expression == "happy":
        cv2.ellipse(face, (center[0], center[1] + 60), (60, 30), 0, 0, 180, eye_color, 4, lineType=cv2.LINE_AA)
    elif expression == "sad":
        cv2.ellipse(face, (center[0], center[1] + 80), (60, 30), 0, 0, -180, eye_color, 4, lineType=cv2.LINE_AA)
    elif expression == "angry":
        # cejas
        cv2.line(face, (center[0]-70, center[1]-80), (center[0]-30, center[1]-60), eye_color, 4, lineType=cv2.LINE_AA)
        cv2.line(face, (center[0]+30, center[1]-60), (center[0]+70, center[1]-80), eye_color, 4, lineType=cv2.LINE_AA)
        # boca tensa
        cv2.line(face, (center[0]-50, center[1]+80), (center[0]+50, center[1]+80), eye_color, 4, lineType=cv2.LINE_AA)
    elif expression == "neutral":
        cv2.line(face, (center[0]-50, center[1]+80), (center[0]+50, center[1]+80), eye_color, 3, lineType=cv2.LINE_AA)
    elif expression == "gel":
        # boca en rojo suave
        cv2.ellipse(face, (center[0], center[1] + 60), (60, 30), 0, 0, 180, (180, 50, 50), 4, lineType=cv2.LINE_AA)
        cv2.putText(face, "💧", (center[0]-20, center[1]-80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (180, 50, 50), 2, lineType=cv2.LINE_AA)

    # 8) Textos de signos vitales (gris oscuro)
    if pulse is not None and spo2 is not None:
        txt_color = (50, 50, 50)
        cv2.putText(face, f"Pulso: {pulse} lpm", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, txt_color, 2, lineType=cv2.LINE_AA)
        cv2.putText(face, f"SpO2: {spo2}%", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, txt_color, 2, lineType=cv2.LINE_AA)

    return face

def show_expression(expression, duration=3, pulse=None, spo2=None):
    start = time.time()
    while time.time() - start < duration:
        face = draw_face(expression, pulse=pulse, spo2=spo2)
        cv2.imshow("BeniBot", face)
        if cv2.waitKey(100) & 0xFF == 27:
            break

def main_loop():
    cv2.namedWindow("BeniBot", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("BeniBot", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    blink = False
    last_blink_time = time.time()

    while True:
        actions = db.reference("/Acciones").get() or {}
        pulso = db.reference("/Signos/Pulso").get() or 0
        spo2  = db.reference("/Signos/SpO2").get() or 0

        if actions.get("Saludo"):
            show_expression("happy", duration=3, pulse=pulso, spo2=spo2)
            db.reference("/Acciones/Saludo").set(False)
        elif actions.get("Gel"):
            show_expression("gel", duration=3, pulse=pulso, spo2=spo2)
            db.reference("/Acciones/Gel").set(False)
        elif actions.get("Triste"):
            show_expression("sad", duration=3, pulse=pulso, spo2=spo2)
            db.reference("/Acciones/Triste").set(False)
        elif actions.get("Enojado"):
            show_expression("angry", duration=3, pulse=pulso, spo2=spo2)
            db.reference("/Acciones/Enojado").set(False)
        elif actions.get("Pastilla"):
            show_expression("neutral", duration=3, pulse=pulso, spo2=spo2)
            db.reference("/Acciones/Pastilla").set(False)
        elif actions.get("Signos"):
            show_expression("neutral", duration=5, pulse=pulso, spo2=spo2)
            db.reference("/Acciones/Signos").set(False)
        else:
            now = time.time()
            if now - last_blink_time > 2.5:
                blink = True
                blink_start = now
            if blink and now - blink_start > 0.15:
                blink = False
                last_blink_time = now

            face = draw_face("neutral", blink, pulse=pulso, spo2=spo2)
            cv2.imshow("BeniBot", face)

        if cv2.waitKey(30) & 0xFF == 27:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main_loop()
