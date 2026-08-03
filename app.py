import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from config import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH, UPLOAD_DIR
from services.firebase_service import FirebaseService
from services.prolog_service import MotorProlog
from vision.reconocedor_raza import ReconocedorRaza

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)

SINTOMAS = {
    "Respiratorios": [
        ("tos", "Tos"), ("fiebre", "Fiebre"),
        ("secrecion_nasal", "Secreción nasal"), ("dificultad_respirar", "Dificultad para respirar"),
    ],
    "Digestivos": [
        ("vomito", "Vómito"), ("diarrea", "Diarrea"),
        ("diarrea_con_sangre", "Diarrea con sangre"), ("perdida_apetito", "Pérdida de apetito"),
        ("deshidratacion", "Deshidratación"),
    ],
    "Oídos y piel": [
        ("rasca_orejas", "Se rasca las orejas"), ("sacude_cabeza", "Sacude la cabeza"),
        ("secrecion_oido", "Secreción en el oído"), ("comezon", "Comezón"),
        ("enrojecimiento_piel", "Enrojecimiento de piel"), ("perdida_pelo", "Pérdida de pelo"),
    ],
    "Ojos": [
        ("ojos_rojos", "Ojos rojos"), ("secrecion_ocular", "Secreción ocular"),
        ("lagrimeo", "Lagrimeo"),
    ],
    "Urinarios": [
        ("orina_frecuente", "Orina frecuente"), ("dolor_orinar", "Dolor al orinar"),
        ("dificultad_orinar", "Dificultad para orinar"),
    ],
    "Neurológicos y urgentes": [
        ("temblores", "Temblores"), ("convulsiones", "Convulsiones"),
        ("desmayo", "Desmayo"), ("sangrado_abundante", "Sangrado abundante"),
        ("salivacion_excesiva", "Salivación excesiva"), ("debilidad", "Debilidad"),
    ],
}

RAZAS = {
    "perro": [
        ("husky_siberiano", "Husky siberiano"), ("pastor_aleman", "Pastor alemán"),
        ("labrador", "Labrador"), ("golden_retriever", "Golden retriever"),
        ("pug", "Pug"), ("chihuahua", "Chihuahua"),
        ("beagle", "Beagle"), ("mestizo", "Mestizo / Otra"),
    ],
    "gato": [
        ("persa", "Persa"), ("siames", "Siamés"),
        ("gato_domestico", "Gato doméstico"), ("mestizo", "Mestizo / Otra"),
    ],
}

MEDICAMENTOS = [
    ("ninguno", "Ninguno"), ("paracetamol", "Paracetamol"),
    ("aspirina", "Aspirina"), ("ibuprofeno", "Ibuprofeno"),
    ("naproxeno", "Naproxeno"), ("diclofenaco", "Diclofenaco"),
]

motor = MotorProlog()
firebase_service = FirebaseService()
reconocedor = ReconocedorRaza()

def extension_permitida(nombre: str) -> bool:
    return "." in nombre and nombre.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def guardar_archivo(archivo):
    extension = archivo.filename.rsplit(".", 1)[1].lower()
    nombre = secure_filename(f"{uuid.uuid4().hex}.{extension}")
    ruta = UPLOAD_DIR / nombre
    archivo.save(ruta)
    return ruta, nombre

# ==========================================
# RUTAS DE LA APLICACIÓN
# ==========================================

@app.get("/")
def inicio():
    return render_template(
        "index.html",
        sintomas=SINTOMAS,
        razas=RAZAS,
        medicamentos=MEDICAMENTOS,
        prolog_disponible=motor.disponible,
        firebase_disponible=firebase_service.disponible,
        vision_disponible=reconocedor.disponible,
    )

@app.post("/reconocer-raza")
def reconocer_raza():
    archivo = request.files.get("foto")
    if not archivo or not archivo.filename:
        return jsonify({"ok": False, "error": "Selecciona una fotografía."}), 400
    if not extension_permitida(archivo.filename):
        return jsonify({"ok": False, "error": "Formato de imagen no permitido."}), 400

    ruta, nombre = guardar_archivo(archivo)
    try:
        resultado = reconocedor.reconocer(ruta)
        resultado["imagen_local"] = f"/static/uploads/{nombre}"
        return jsonify({"ok": True, "resultado": resultado})
    except Exception as error:
        return jsonify({"ok": False, "error": str(error)}), 500

@app.post("/analizar")
def analizar():
    nombre = request.form.get("nombre", "").strip()
    especie = request.form.get("especie", "").strip().lower()
    raza = request.form.get("raza", "").strip().lower()
    edad = request.form.get("edad", "").strip()
    peso_str = request.form.get("peso", "0").strip()
    sexo = request.form.get("sexo", "").strip().lower()
    actividad = request.form.get("actividad", "").strip().lower()
    medicamento = request.form.get("medicamento", "ninguno").strip().lower()
    sintomas = request.form.getlist("sintomas")
    
    modo = request.form.get("modo", "enfermedad").strip().lower()

    errores = []
    if not nombre:
        errores.append("Escribe el nombre de la mascota.")
    if especie not in {"perro", "gato"}:
        errores.append("Selecciona una especie.")
        
    if modo == "enfermedad" and not sintomas:
        errores.append("Selecciona al menos un síntoma.")
    
    try:
        peso = float(peso_str)
        if peso <= 0:
            errores.append("El peso debe ser mayor a 0.")
    except ValueError:
        errores.append("Ingresa un peso válido.")

    if errores:
        return jsonify({"ok": False, "errores": errores}), 400

    dosis_mg = round(peso * 5.0, 1)

    imagen_local = None
    imagen_url = None
    vision = None
    archivo = request.files.get("foto")

    if archivo and archivo.filename:
        if not extension_permitida(archivo.filename):
            return jsonify({"ok": False, "errores": ["Formato de imagen no permitido."]}), 400
        ruta, nombre_archivo = guardar_archivo(archivo)
        imagen_local = f"/static/uploads/{nombre_archivo}"
        try:
            vision = reconocedor.reconocer(ruta)
            if vision["especie"] in {"perro", "gato"}:
                especie = vision["especie"]
            if vision["raza"] != "no_identificada":
                raza = vision["raza"]
        except Exception as error:
            vision = {"error": str(error)}

        try:
            imagen_url = firebase_service.subir_imagen(ruta, nombre_archivo)
        except Exception as error:
            print(f"No se pudo subir imagen: {error}")

    resultado = motor.analizar(nombre, especie, sintomas, raza, medicamento)

    mascota = {
        "nombre": nombre, "especie": especie, "raza": raza,
        "raza_detectada": vision.get("raza") if vision and not vision.get("error") else None,
        "confianza_raza": vision.get("confianza") if vision and not vision.get("error") else None,
        "edad": int(edad) if edad.isdigit() else None, "peso": peso, "sexo": sexo,
        "actividad": actividad, "imagen_url": imagen_url,
    }
    mascota_id = firebase_service.guardar_o_actualizar_mascota(mascota)

    consulta = {
        "mascota_id": mascota_id, "nombre": nombre, "especie": especie,
        "raza": raza, "edad": mascota["edad"], "peso": peso, "dosis_desparasitante": dosis_mg,
        "sexo": sexo, "actividad": actividad, "sintomas": sintomas,
        "medicamento": medicamento, "diagnosticos": resultado["diagnosticos"],
        "triaje": resultado["triaje"], "perfil_raza": resultado["perfil_raza"],
        "advertencia": resultado["advertencia"], "imagen_url": imagen_url,
        "imagen_local": imagen_local, "vision_artificial": vision,
        "motor_inferencia": resultado["motor"],
        "modo": modo
    }
    consulta_id = firebase_service.guardar_consulta(consulta)
    consulta["consulta_id"] = consulta_id
    consulta["firebase_guardado"] = bool(consulta_id)
    
    return jsonify({"ok": True, "resultado": consulta})

@app.get("/api/historial")
def api_historial():
    return jsonify({"ok": True, "historial": firebase_service.obtener_historial()})

@app.errorhandler(413)
def archivo_grande(_):
    return jsonify({"ok": False, "errores": ["La fotografía supera 5 MB."]}), 413

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False, threaded=True)