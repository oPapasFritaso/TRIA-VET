import hashlib
import os
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import firebase_admin
from firebase_admin import credentials, firestore, storage


# =========================================================
# RUTAS Y CONFIGURACIÓN
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CREDENTIALS_FILE = (
    BASE_DIR
    / "prueba-77cee-firebase-adminsdk-fbsvc-d767780ebf.json"
)

# Es opcional para Firestore.
# Solo es necesario para subir fotografías a Firebase Storage.
STORAGE_BUCKET = os.getenv(
    "FIREBASE_STORAGE_BUCKET",
    ""
).strip()


class FirebaseService:
    """
    Servicio para trabajar con Cloud Firestore y,
    opcionalmente, Firebase Storage.
    """

    def __init__(self) -> None:
        self.db = None
        self.bucket = None
        self.disponible = False
        self.storage_disponible = False
        self.error: Optional[str] = None

        self.inicializar()

    # =====================================================
    # INICIALIZACIÓN
    # =====================================================

    def inicializar(self) -> None:
        print("=" * 60)
        print("INICIALIZANDO FIREBASE")
        print("Ruta de credenciales:")
        print(CREDENTIALS_FILE)

        try:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    "No se encontró el archivo de credenciales: "
                    f"{CREDENTIALS_FILE}"
                )

            opciones = {}

            if STORAGE_BUCKET:
                opciones["storageBucket"] = STORAGE_BUCKET

            if not firebase_admin._apps:
                credencial = credentials.Certificate(
                    str(CREDENTIALS_FILE)
                )

                firebase_admin.initialize_app(
                    credencial,
                    opciones
                )

            self.db = firestore.client()
            self.disponible = True
            self.error = None

            print("Firebase conectado correctamente.")
            print("Firestore disponible: True")

            self._inicializar_storage()

        except Exception as error:
            self.db = None
            self.bucket = None
            self.disponible = False
            self.storage_disponible = False
            self.error = str(error)

            print("ERROR AL INICIALIZAR FIREBASE")
            print("Tipo:", type(error).__name__)
            print("Detalle:", error)

        print("=" * 60)

    def _inicializar_storage(self) -> None:
        if not STORAGE_BUCKET:
            self.bucket = None
            self.storage_disponible = False

            print(
                "Firebase Storage no configurado. "
                "Firestore sí puede utilizarse."
            )
            return

        try:
            self.bucket = storage.bucket()
            self.storage_disponible = True

            print("Firebase Storage disponible: True")
            print("Bucket:", STORAGE_BUCKET)

        except Exception as error:
            self.bucket = None
            self.storage_disponible = False

            print("Firebase Storage no disponible.")
            print("Detalle:", error)

    # =====================================================
    # FUNCIONES AUXILIARES
    # =====================================================

    @staticmethod
    def _normalizar_texto(texto: Any) -> str:
        texto = str(texto or "").strip().lower()

        texto = unicodedata.normalize(
            "NFKD",
            texto
        )

        texto = "".join(
            caracter
            for caracter in texto
            if not unicodedata.combining(caracter)
        )

        return texto

    def _generar_id_mascota(
        self,
        nombre: str,
        especie: str
    ) -> str:
        """
        Genera un ID estable para evitar que la misma mascota
        se duplique en cada consulta.
        """

        clave = (
            f"{self._normalizar_texto(especie)}:"
            f"{self._normalizar_texto(nombre)}"
        )

        resumen = hashlib.sha256(
            clave.encode("utf-8")
        ).hexdigest()[:20]

        return f"mascota_{resumen}"

    def _verificar_firestore(self) -> bool:
        if self.disponible and self.db is not None:
            return True

        print("Firestore no está disponible.")

        if self.error:
            print("Detalle:", self.error)

        return False

    # =====================================================
    # FIREBASE STORAGE
    # =====================================================

    def subir_imagen(
        self,
        ruta_archivo: Path,
        nombre_archivo: str
    ) -> Optional[str]:
        """
        Sube la fotografía a Firebase Storage.

        Si Storage no está configurado, devuelve None sin
        impedir que la consulta se guarde en Firestore.
        """

        if not self.storage_disponible or self.bucket is None:
            print(
                "La imagen no se subió porque Firebase "
                "Storage no está configurado."
            )
            return None

        try:
            ruta_archivo = Path(ruta_archivo)

            if not ruta_archivo.exists():
                raise FileNotFoundError(
                    f"No existe la imagen: {ruta_archivo}"
                )

            destino = f"mascotas/{nombre_archivo}"

            blob = self.bucket.blob(destino)

            blob.upload_from_filename(
                str(ruta_archivo)
            )

            # Esta operación puede depender de la configuración
            # del bucket. Si falla, se conserva la ruta gs://.
            try:
                blob.make_public()
                imagen_url = blob.public_url
            except Exception:
                imagen_url = (
                    f"gs://{self.bucket.name}/{destino}"
                )

            print("Imagen subida correctamente:")
            print(imagen_url)

            return imagen_url

        except Exception as error:
            print("ERROR AL SUBIR LA IMAGEN")
            print("Tipo:", type(error).__name__)
            print("Detalle:", error)

            return None

    # =====================================================
    # COLECCIÓN MASCOTAS
    # =====================================================

    def guardar_o_actualizar_mascota(
        self,
        datos: dict[str, Any]
    ) -> Optional[str]:
        """
        Crea una mascota si no existe o actualiza su
        información si ya fue registrada.
        """

        if not self._verificar_firestore():
            return None

        try:
            nombre = str(
                datos.get("nombre", "")
            ).strip()

            especie = str(
                datos.get("especie", "")
            ).strip().lower()

            if not nombre:
                raise ValueError(
                    "El nombre de la mascota es obligatorio."
                )

            if especie not in {"perro", "gato"}:
                raise ValueError(
                    "La especie debe ser perro o gato."
                )

            mascota_id = self._generar_id_mascota(
                nombre,
                especie
            )

            referencia = (
                self.db
                .collection("mascotas")
                .document(mascota_id)
            )

            documento = referencia.get()
            ya_existe = documento.exists

            mascota = {
                "nombre": nombre,
                "nombre_normalizado":
                    self._normalizar_texto(nombre),
                "especie": especie,
                "raza": datos.get("raza"),
                "raza_detectada":
                    datos.get("raza_detectada"),
                "confianza_raza":
                    datos.get("confianza_raza"),
                "edad": datos.get("edad"),
                "sexo": datos.get("sexo"),
                "actividad": datos.get("actividad"),
                "imagen_url": datos.get("imagen_url"),
                "ultima_actualizacion":
                    firestore.SERVER_TIMESTAMP,
            }

            if not ya_existe:
                mascota["fecha_registro"] = (
                    firestore.SERVER_TIMESTAMP
                )

            referencia.set(
                mascota,
                merge=True
            )

            if ya_existe:
                print(
                    "Mascota actualizada correctamente:",
                    mascota_id
                )
            else:
                print(
                    "Mascota creada correctamente:",
                    mascota_id
                )

            return mascota_id

        except Exception as error:
            self.error = str(error)

            print(
                "ERROR AL GUARDAR O ACTUALIZAR MASCOTA"
            )
            print("Tipo:", type(error).__name__)
            print("Detalle:", error)

            return None

    # =====================================================
    # COLECCIÓN CONSULTAS
    # =====================================================

    def guardar_consulta(
        self,
        datos: dict[str, Any]
    ) -> Optional[str]:
        """
        Guarda una nueva consulta veterinaria.
        Cada análisis genera un documento independiente.
        """

        if not self._verificar_firestore():
            return None

        try:
            referencia = (
                self.db
                .collection("consultas_veterinarias")
                .document()
            )

            consulta = {
                "mascota_id":
                    datos.get("mascota_id"),
                "nombre":
                    datos.get("nombre"),
                "especie":
                    datos.get("especie"),
                "raza":
                    datos.get("raza"),
                "edad":
                    datos.get("edad"),
                "sexo":
                    datos.get("sexo"),
                "actividad":
                    datos.get("actividad"),
                "sintomas":
                    datos.get("sintomas", []),
                "medicamento":
                    datos.get("medicamento", "ninguno"),
                "diagnosticos":
                    datos.get("diagnosticos", []),
                "triaje":
                    datos.get("triaje", "bajo"),
                "perfil_raza":
                    datos.get("perfil_raza"),
                "advertencia":
                    datos.get("advertencia"),
                "imagen_url":
                    datos.get("imagen_url"),
                "imagen_local":
                    datos.get("imagen_local"),
                "vision_artificial":
                    datos.get("vision_artificial"),
                "motor_inferencia":
                    datos.get(
                        "motor_inferencia",
                        "Prolog"
                    ),
                "fecha":
                    firestore.SERVER_TIMESTAMP,
            }

            referencia.set(consulta)

            print(
                "Consulta guardada correctamente:",
                referencia.id
            )

            return referencia.id

        except Exception as error:
            self.error = str(error)

            print("ERROR AL GUARDAR LA CONSULTA")
            print("Tipo:", type(error).__name__)
            print("Detalle:", error)

            return None

    # =====================================================
    # HISTORIAL
    # =====================================================

    def obtener_historial(
        self,
        limite: int = 50
    ) -> list[dict[str, Any]]:
        """
        Recupera las consultas más recientes de Firestore.
        """

        if not self._verificar_firestore():
            return []

        try:
            limite = max(
                1,
                min(int(limite), 100)
            )

            documentos = (
                self.db
                .collection("consultas_veterinarias")
                .order_by(
                    "fecha",
                    direction=firestore.Query.DESCENDING
                )
                .limit(limite)
                .stream()
            )

            historial = []

            for documento in documentos:
                datos = documento.to_dict() or {}
                datos["consulta_id"] = documento.id

                fecha = datos.get("fecha")

                if isinstance(fecha, datetime):
                    datos["fecha"] = fecha.isoformat()

                historial.append(datos)

            return historial

        except Exception as error:
            self.error = str(error)

            print("ERROR AL OBTENER EL HISTORIAL")
            print("Tipo:", type(error).__name__)
            print("Detalle:", error)

            return []