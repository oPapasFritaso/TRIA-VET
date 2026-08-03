import re
import uuid
from pathlib import Path

try:
    from pyswip import Prolog
except Exception:
    Prolog = None

from config import BASE_DIR


class MotorProlog:
    def __init__(self) -> None:
        self.disponible = False
        self.prolog = None
        if Prolog is None:
            return
        try:
            self.prolog = Prolog()
            ruta = str(BASE_DIR / "base_conocimiento.pl").replace("\\", "/")
            self.prolog.consult(ruta)
            self.disponible = True
        except Exception as error:
            print(f"No fue posible iniciar Prolog: {error}")

    @staticmethod
    def atom(texto: str) -> str:
        limpio = re.sub(r"[^a-zA-Z0-9_]", "_", texto.strip().lower())
        return limpio or "mascota"

    def analizar(self, nombre, especie, sintomas, raza=None, medicamento="ninguno"):
        if not self.disponible:
            return {
                "diagnosticos": [],
                "triaje": "bajo",
                "perfil_raza": None,
                "advertencia": "Prolog no está disponible.",
                "motor": "No disponible",
            }

        animal = self.atom(f"{nombre}_{uuid.uuid4().hex[:8]}")
        especie_atom = self.atom(especie)

        try:
            list(self.prolog.query(f"registrar_paciente({animal}, {especie_atom})"))
            for sintoma in sintomas:
                list(self.prolog.query(
                    f"registrar_sintoma({animal}, {self.atom(sintoma)})"
                ))

            diagnosticos = []
            consulta = f"posible_diagnostico({animal}, D, P), recomendacion(D, R)"
            for resultado in self.prolog.query(consulta):
                diagnosticos.append({
                    "diagnostico": str(resultado["D"]),
                    "porcentaje": round(float(resultado["P"]), 1),
                    "recomendacion": str(resultado["R"]),
                })
            diagnosticos.sort(key=lambda item: item["porcentaje"], reverse=True)

            triajes = list(self.prolog.query(f"triaje({animal}, N)"))
            triaje = str(triajes[0]["N"]) if triajes else "bajo"

            perfil = None
            if raza and raza not in {"mestizo", "no_identificada"}:
                perfiles = list(self.prolog.query(
                    f"perfil_raza({self.atom(raza)}, C, R, S)"
                ))
                if perfiles:
                    perfil = {
                        "caracteristicas": str(perfiles[0]["C"]),
                        "recomendacion": str(perfiles[0]["R"]),
                        "salud": str(perfiles[0]["S"]),
                    }

            advertencia = None
            if medicamento and medicamento != "ninguno":
                advertencias = list(self.prolog.query(
                    f"advertencia_farmacologica({animal}, {self.atom(medicamento)}, A)"
                ))
                if advertencias:
                    advertencia = str(advertencias[0]["A"])

            return {
                "diagnosticos": diagnosticos[:3],
                "triaje": triaje,
                "perfil_raza": perfil,
                "advertencia": advertencia,
                "motor": "Prolog",
            }
        finally:
            try:
                list(self.prolog.query(f"limpiar_paciente({animal})"))
            except Exception:
                pass
