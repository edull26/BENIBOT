import speech_recognition as sr
import pyttsx3
import firebase_admin
from firebase_admin import credentials, db
import time

# ==== Inicializar Firebase ====
try:
    cred = credentials.Certificate("C:/Users/leong/OneDrive/Documentos/BENIVOZ/benibot26-firebase-adminsdk-fbsvc-72d2d50f15.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://benibot26-default-rtdb.firebaseio.com/'
    })
    print("🔥 Conectado a Firebase correctamente")
except Exception as e:
    print(f"❌ Error al conectar a Firebase: {e}")

# ==== Configuración de voz ====
name = "benito"
listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def talk(text):
    """Función para que el robot hable."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Función para escuchar y reconocer comandos."""
    with sr.Microphone() as source:
        print("🎙 Escuchando...")
        listener.adjust_for_ambient_noise(source)
        try:
            audio = listener.listen(source, timeout=5)
            rec = listener.recognize_google(audio, language="es").lower()
            print(f"✅ Comando detectado: {rec}")
            return rec
        except sr.WaitTimeoutError:
            print("⌛ No se detectó audio, esperando nuevamente...")
            return ""
        except sr.UnknownValueError:
            print("❌ No te entendí, intenta de nuevo")
            return ""
        except Exception as e:
            print(f"❌ Error en escucha: {e}")
            return ""

def send_command_to_firebase(command):
    """Función para actualizar a True y luego regresar a False."""
    try:
        ref = db.reference(f'/Acciones/{command}')
        ref.set(True)
        print(f"🔥 {command} actualizado a True en Firebase")
        talk(f"Ejecutando {command}")
        time.sleep(5)
        ref.set(False)
        print(f"🔁 {command} reseteado a False en Firebase")
    except Exception as e:
        print(f"❌ Error al escribir en Firebase: {e}")

def give_advice(emotion):
    """Función para ofrecer consejos según el estado de ánimo."""
    advice = {
        "triste": "No pasa nada, permítete sentir todo lo que necesites, pero sigue adelante.",
        "estresado": "Respira profundo, organiza tus ideas y prioriza lo importante.",
        "ansioso": "Intenta enfocarte en el momento presente, poco a poco sentirás mayor calma.",
        "enojado": "Cuenta hasta diez y piensa en algo que te haga sentir paz, puedes con esto.",
        "feliz": "Disfruta este momento, compártelo con quienes quieres." 
    }
    talk(advice.get(emotion, "No estoy seguro de qué decirte, pero recuerda que siempre puedes seguir adelante."))

def run_beni():
    """Bucle principal del robot."""
    while True:
        rec = listen()
        if name in rec:
            rec = rec.replace(name, '').strip()
            if "salúdame" in rec:
                print("✅ Enviando comando de saludo a Firebase")
                send_command_to_firebase('Saludo')
                talk("Hola, soy Beni bot, tu asistente médico personal, ¿En qué puedo ayudarte el día de hoy")
            elif "estoy triste" in rec:
                give_advice("triste")
            elif "estoy estresado" in rec:
                give_advice("estresado")
            elif "estoy ansioso" in rec:
                give_advice("ansioso")
            elif "estoy enojado" in rec:
                give_advice("enojado")
            elif "estoy feliz" in rec:
                give_advice("feliz")
            elif "dame gel" in rec:
                print("✅ Enviando comando para dispensar gel")
                send_command_to_firebase('Gel')
                talk("Claro, aqui hay un poco de gel para tí, recuerda siempre tener las manos limpias")

if __name__ == "__main__":
    run_beni()
