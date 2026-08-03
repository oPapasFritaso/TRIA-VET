from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

try:
    from tensorflow.keras.applications.mobilenet_v2 import (
        MobileNetV2,
        decode_predictions,
        preprocess_input,
    )
except Exception:
    MobileNetV2 = None
    decode_predictions = None
    preprocess_input = None


MAPEO_RAZAS = {
    "siberian_husky": "husky_siberiano",
    "german_shepherd": "pastor_aleman",
    "labrador_retriever": "labrador",
    "golden_retriever": "golden_retriever",
    "pug": "pug",
    "chihuahua": "chihuahua",
    "beagle": "beagle",
    "persian_cat": "persa",
    "siamese_cat": "siames",
    "egyptian_cat": "gato_domestico",
    "tabby": "gato_domestico",
    "tiger_cat": "gato_domestico",
}

ETIQUETAS_GATO = {
    "tabby", "tiger_cat", "persian_cat", "siamese_cat", "egyptian_cat",
}

# ImageNet incluye muchas razas de perro consecutivas; además se contemplan
# etiquetas frecuentes que MobileNetV2 devuelve para perros.
PISTAS_PERRO = {
    "dog", "terrier", "retriever", "shepherd", "spaniel", "hound",
    "poodle", "mastiff", "collie", "husky", "malamute", "pug",
    "chihuahua", "beagle", "boxer", "dalmatian", "schnauzer",
}


class ReconocedorRaza:
    """
    Estimación académica de especie y raza usando MobileNetV2 preentrenada
    con ImageNet. No sustituye un modelo veterinario entrenado específicamente.
    """

    def __init__(self) -> None:
        self.modelo = None
        self.disponible = MobileNetV2 is not None
        self.mensaje = (
            "MobileNetV2 disponible" if self.disponible
            else "TensorFlow no está instalado"
        )

    def _cargar_modelo(self) -> None:
        if not self.disponible:
            raise RuntimeError(self.mensaje)
        if self.modelo is None:
            self.modelo = MobileNetV2(weights="imagenet")

    @staticmethod
    def _normalizar_etiqueta(etiqueta: str) -> str:
        return etiqueta.strip().lower().replace(" ", "_")

    def reconocer(self, ruta_imagen: str | Path) -> dict[str, Any]:
        self._cargar_modelo()

        imagen = Image.open(ruta_imagen).convert("RGB").resize((224, 224))
        arreglo = np.asarray(imagen, dtype=np.float32)
        arreglo = np.expand_dims(arreglo, axis=0)
        arreglo = preprocess_input(arreglo)

        prediccion = self.modelo.predict(arreglo, verbose=0)
        resultados = decode_predictions(prediccion, top=5)[0]

        candidatos = []
        especie = "desconocida"
        raza = "no_identificada"
        confianza = 0.0

        for _, etiqueta_original, probabilidad in resultados:
            etiqueta = self._normalizar_etiqueta(etiqueta_original)
            candidatos.append({
                "etiqueta": etiqueta,
                "confianza": round(float(probabilidad) * 100, 2),
            })

            if etiqueta in ETIQUETAS_GATO and confianza == 0.0:
                especie = "gato"
                raza = MAPEO_RAZAS.get(etiqueta, "gato_domestico")
                confianza = float(probabilidad) * 100
                continue

            if any(pista in etiqueta for pista in PISTAS_PERRO) and confianza == 0.0:
                especie = "perro"
                raza = MAPEO_RAZAS.get(etiqueta, etiqueta)
                confianza = float(probabilidad) * 100

        return {
            "especie": especie,
            "raza": raza,
            "confianza": round(confianza, 2),
            "candidatos": candidatos,
            "modelo": "MobileNetV2-ImageNet",
        }
