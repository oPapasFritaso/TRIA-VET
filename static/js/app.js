/* =========================================================
   VARIABLES GLOBALES
========================================================= */
const form = document.getElementById("form-analisis");
const especie = document.getElementById("especie");
const raza = document.getElementById("raza");
const foto = document.getElementById("foto");
const preview = document.getElementById("preview");
const placeholder = document.getElementById("upload-placeholder");
const boton = document.getElementById("btn-analizar");
const mensajes = document.getElementById("mensajes");
const btnReconocer = document.getElementById("btn-reconocer");
const visionResultado = document.getElementById("vision-resultado");

const navEnfermedad = document.getElementById("nav-enfermedad");
const navDesparasitante = document.getElementById("nav-desparasitante");
const seccionSintomasFarmacos = document.getElementById("seccion-sintomas-farmacos");
const inputModo = document.getElementById("modo");
const txtBtnAnalizar = document.getElementById("txt-btn-analizar");
const formTitle = document.getElementById("form-title");
const formDesc = document.getElementById("form-desc");


/* =========================================================
   NAVEGACIÓN POR PESTAÑAS (Enfermedad / Desparasitante)
========================================================= */
navEnfermedad.addEventListener("click", (e) => {
    e.preventDefault();
    navEnfermedad.classList.add("active");
    navDesparasitante.classList.remove("active");
    seccionSintomasFarmacos.classList.remove("hidden");
    inputModo.value = "enfermedad";
    txtBtnAnalizar.textContent = "Procesar Triaje";
    formTitle.textContent = "Análisis de Triaje 🐾";
    formDesc.textContent = "Clasificación preliminar para perros y gatos mediante evaluación de síntomas.";
});

navDesparasitante.addEventListener("click", (e) => {
    e.preventDefault();
    navDesparasitante.classList.add("active");
    navEnfermedad.classList.remove("active");
    seccionSintomasFarmacos.classList.add("hidden");
    inputModo.value = "desparasitante";
    txtBtnAnalizar.textContent = "Calcular Dosis";
    formTitle.textContent = "Cálculo de Desparasitante 🐾";
    formDesc.textContent = "Obtén la dosis preventiva recomendada según el peso de la mascota.";
    document.getElementById("medicamento").value = "ninguno";
});


/* =========================================================
   FUNCIÓN PARA LEER RESPUESTAS DEL SERVIDOR
========================================================= */
async function obtenerJsonSeguro(respuesta) {
    const contenido = await respuesta.text();
    try {
        return JSON.parse(contenido);
    } catch (error) {
        console.error("El servidor devolvió una respuesta no JSON:");
        console.error(contenido);
        throw new Error(
            "El servidor produjo un error interno. Revisa la terminal donde ejecutaste python app.py."
        );
    }
}


/* =========================================================
   CARGAR RAZAS SEGÚN LA ESPECIE
========================================================= */
especie.addEventListener("change", () => {
    const opciones = window.RAZAS[especie.value] || [];
    raza.innerHTML = `<option value="">Selecciona una raza</option>`;
    
    opciones.forEach(([valor, etiqueta]) => {
        const option = document.createElement("option");
        option.value = valor;
        option.textContent = etiqueta;
        raza.appendChild(option);
    });
});


/* =========================================================
   VISTA PREVIA DE LA FOTOGRAFÍA
========================================================= */
foto.addEventListener("change", () => {
    const archivo = foto.files[0];
    visionResultado.textContent = "";

    if (!archivo) {
        preview.style.display = "none";
        placeholder.style.display = "grid";
        preview.src = "";
        return;
    }

    const tiposPermitidos = ["image/jpeg", "image/png", "image/webp"];

    if (!tiposPermitidos.includes(archivo.type)) {
        mensajes.textContent = "La fotografía debe ser JPG, PNG o WEBP.";
        foto.value = "";
        preview.style.display = "none";
        placeholder.style.display = "grid";
        return;
    }

    const limite = 5 * 1024 * 1024;
    if (archivo.size > limite) {
        mensajes.textContent = "La fotografía no debe superar los 5 MB.";
        foto.value = "";
        preview.style.display = "none";
        placeholder.style.display = "grid";
        return;
    }

    mensajes.textContent = "";
    preview.src = URL.createObjectURL(archivo);
    preview.style.display = "block";
    placeholder.style.display = "none";
});


/* =========================================================
   RECONOCIMIENTO DE ESPECIE Y RAZA
========================================================= */
btnReconocer.addEventListener("click", async () => {
    const archivo = foto.files[0];

    if (!archivo) {
        visionResultado.textContent = "Selecciona primero una fotografía.";
        return;
    }

    btnReconocer.disabled = true;
    btnReconocer.textContent = "Reconociendo...";
    visionResultado.textContent = "Procesando fotografía con MobileNetV2...";

    const datosFormulario = new FormData();
    datosFormulario.append("foto", archivo);

    try {
        const respuesta = await fetch("/reconocer-raza", {
            method: "POST",
            body: datosFormulario
        });

        const contenido = await obtenerJsonSeguro(respuesta);

        if (!respuesta.ok || !contenido.ok) {
            throw new Error(
                contenido.error || contenido.detalle || "No fue posible reconocer la imagen."
            );
        }

        const resultado = contenido.resultado;

        if (!resultado) {
            throw new Error("El servidor no devolvió el resultado de visión artificial.");
        }

        visionResultado.innerHTML = `
            <p><strong>Especie:</strong> ${textoBonito(resultado.especie)}</p>
            <p><strong>Raza estimada:</strong> ${textoBonito(resultado.raza)}</p>
            <p><strong>Confianza:</strong> ${resultado.confianza ?? 0} %</p>
            <p><strong>Modelo:</strong> ${resultado.modelo || "MobileNetV2"}</p>
        `;

        if (resultado.especie === "perro" || resultado.especie === "gato") {
            especie.value = resultado.especie;
            especie.dispatchEvent(new Event("change"));

            setTimeout(() => {
                const existe = [...raza.options].some(opcion => opcion.value === resultado.raza);
                if (existe) {
                    raza.value = resultado.raza;
                }
            }, 50);
        }
    } catch (error) {
        console.error(error);
        visionResultado.textContent = error.message || "Ocurrió un error al reconocer la fotografía.";
    } finally {
        btnReconocer.disabled = false;
        btnReconocer.textContent = "Reconocer especie y raza";
    }
});


/* =========================================================
   ENVIAR FORMULARIO PARA ANÁLISIS
========================================================= */
form.addEventListener("submit", async (event) => {
    event.preventDefault();
    mensajes.textContent = "";
    boton.disabled = true;
    txtBtnAnalizar.textContent = "Procesando...";

    try {
        const datosFormulario = new FormData(form);
        const sintomasSeleccionados = datosFormulario.getAll("sintomas");
        const modoSeleccionado = inputModo.value;

        if (!datosFormulario.get("nombre")?.trim()) {
            throw new Error("Escribe el nombre de la mascota.");
        }
        if (!datosFormulario.get("especie")) {
            throw new Error("Selecciona la especie.");
        }
        
        if (modoSeleccionado === "enfermedad" && sintomasSeleccionados.length === 0) {
            throw new Error("Selecciona al menos un síntoma.");
        }

        const respuesta = await fetch("/analizar", {
            method: "POST",
            body: datosFormulario
        });

        const datos = await obtenerJsonSeguro(respuesta);

        if (!respuesta.ok || !datos.ok) {
            let mensajeError = "No fue posible realizar el análisis.";
            if (Array.isArray(datos.errores) && datos.errores.length > 0) {
                mensajeError = datos.errores.join(" ");
            } else if (datos.error) {
                mensajeError = datos.error;
            } else if (datos.detalle) {
                mensajeError = datos.detalle;
            }
            throw new Error(mensajeError);
        }

        if (!datos.resultado) {
            throw new Error("El servidor no devolvió resultados.");
        }

        mostrarResultados(datos.resultado);

    } catch (error) {
        console.error(error);
        mensajes.textContent = error.message || "Ocurrió un error inesperado.";
    } finally {
        boton.disabled = false;
        txtBtnAnalizar.textContent = inputModo.value === "enfermedad" ? "Procesar Triaje" : "Calcular Dosis";
    }
});


/* =========================================================
   FORMATEAR TEXTO
========================================================= */
function textoBonito(texto) {
    return String(texto || "")
        .replaceAll("_", " ")
        .replace(/\b\w/g, letra => letra.toUpperCase());
}


/* =========================================================
   MOSTRAR RESULTADOS
========================================================= */
function mostrarResultados(resultado) {
    const resultsEmpty = document.getElementById("results-empty");
    const resultsContent = document.getElementById("results-content");

    resultsEmpty.classList.add("hidden");
    resultsContent.classList.remove("hidden");

    const tarjetaTriaje = document.getElementById("tarjeta-triaje");
    const tarjetaDiagnostico = document.getElementById("tarjeta-diagnostico");
    const tarjetaDosis = document.getElementById("tarjeta-dosis");
    const tarjetaFarmaco = document.getElementById("tarjeta-farmaco");

    if (resultado.modo === "desparasitante") {
        tarjetaTriaje.classList.add("hidden");
        tarjetaDiagnostico.classList.add("hidden");
        tarjetaFarmaco.classList.add("hidden");
        tarjetaDosis.classList.remove("hidden");
    } else {
        tarjetaTriaje.classList.remove("hidden");
        tarjetaDiagnostico.classList.remove("hidden");
        tarjetaFarmaco.classList.remove("hidden");
        tarjetaDosis.classList.add("hidden");
    }

    mostrarTriaje(resultado);
    mostrarDiagnosticos(resultado);
    mostrarDosis(resultado);
    mostrarPerfilRaza(resultado);
    mostrarAdvertencia(resultado);

    document.querySelector(".results-panel").scrollIntoView({ 
        behavior: "smooth", 
        block: "start" 
    });
}

function mostrarTriaje(resultado) {
    const nivel = resultado.triaje || "bajo";
    const triajeCard = document.getElementById("triaje-card");
    if(triajeCard) triajeCard.dataset.level = nivel;

    const triajeText = document.getElementById("triaje-text");
    if(triajeText) triajeText.textContent = textoBonito(nivel);

    const triajeBadge = document.getElementById("triaje-badge");
    if(triajeBadge) triajeBadge.textContent = `Nivel ${textoBonito(nivel)}`;
}

function mostrarDiagnosticos(resultado) {
    const contenedor = document.getElementById("diagnosticos");
    if(!contenedor) return;
    const diagnosticos = Array.isArray(resultado.diagnosticos) ? resultado.diagnosticos : [];

    if (diagnosticos.length === 0) {
        contenedor.innerHTML = `
            <p>No se encontró una coincidencia igual o superior al 50 %.</p>
            <p>Se recomienda una valoración veterinaria para obtener un diagnóstico.</p>
        `;
        return;
    }

    contenedor.innerHTML = diagnosticos.map(item => {
        const porcentaje = Number(item.porcentaje) || 0;
        return `
            <article class="diagnostico-item">
                <div class="diagnostico-head">
                    <span>${textoBonito(item.diagnostico)}</span>
                    <span>${porcentaje.toFixed(1)} %</span>
                </div>
                <div class="progress">
                    <span style="width: ${Math.min(porcentaje, 100)}%"></span>
                </div>
                <p>${item.recomendacion || "Consulta a un médico veterinario."}</p>
            </article>
        `;
    }).join("");
}

function mostrarPerfilRaza(resultado) {
    const perfil = document.getElementById("perfil-raza");
    if(!perfil) return;

    if (resultado.perfil_raza) {
        perfil.innerHTML = `
            <p><strong>Características:</strong> ${resultado.perfil_raza.caracteristicas || "No disponible"}</p>
            <p><strong>Recomendación:</strong> ${resultado.perfil_raza.recomendacion || "No disponible"}</p>
            <p><strong>Consejo de salud:</strong> ${resultado.perfil_raza.salud || "No disponible"}</p>
        `;
    } else {
        perfil.innerHTML = `<p>No hay un perfil específico registrado para la raza seleccionada.</p>`;
    }
}

function mostrarAdvertencia(resultado) {
    const advertencia = document.getElementById("advertencia");
    if(!advertencia) return;

    if (resultado.advertencia) {
        advertencia.innerHTML = `<p>${resultado.advertencia}</p>`;
    } else {
        advertencia.innerHTML = `<p>No se seleccionó un medicamento o no existe una advertencia registrada.</p>`;
    }
}

function mostrarDosis(resultado) {
    const contenedor = document.getElementById("dosis-desparasitante");
    if(!contenedor) return;
    
    const dosis = resultado.dosis_desparasitante || 0;
    const peso = resultado.peso || 0;
    
    const rer = Math.round(70 * Math.pow(peso, 0.75));

    contenedor.innerHTML = `
        <div style="margin-bottom: 12px;">
            <p style="color: #14744d; margin: 0 0 5px 0;"><strong>▶ Dosis Antiparasitaria</strong></p>
            <p style="color: #14744d; margin: 0;">
                Peso registrado: <strong>${peso} kg</strong> <br>
                Dosis sugerida (5 mg/kg): <span style="font-size: 1.2rem; font-weight: 800;">${dosis} mg</span>
            </p>
            <p style="font-size: 0.85rem; color: #2ea56f; margin-top: 4px;">
                *Ej. fenbendazol o pirantel. Verifique indicaciones de la formulación comercial.
            </p>
        </div>
        
        <hr style="border: 0; border-top: 1px dashed #bfead6; margin: 12px 0;">
        
        <div>
            <p style="color: #14744d; margin: 0 0 5px 0;"><strong>▶ Guía Nutricional General</strong></p>
            <p style="color: #14744d; margin: 0;">
                Requerimiento Calórico Base (RER): <strong>${rer} kcal/día</strong>
            </p>
            <p style="font-size: 0.85rem; color: #2ea56f; margin-top: 4px;">
                *Valor calórico de mantenimiento estimado. Ajuste las porciones diarias según la tabla nutricional del alimento o croquetas.
            </p>
        </div>
    `;
}