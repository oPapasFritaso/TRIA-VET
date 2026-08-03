% ==========================================
% ACTIVIDAD 1
% ==========================================

padecimiento_especie(infeccion_respiratoria, perro).
padecimiento_especie(infeccion_respiratoria, gato).

padecimiento_especie(gastroenteritis, perro).
padecimiento_especie(gastroenteritis, gato).

padecimiento_especie(dermatitis_alergica, perro).
padecimiento_especie(dermatitis_alergica, gato).

padecimiento_especie(osteoartritis, perro).
padecimiento_especie(osteoartritis, gato).

padecimiento_especie(diabetes_mellitus, perro).
padecimiento_especie(diabetes_mellitus, gato).

padecimiento_especie(lipidosis_hepatica, gato).

padecimiento_especie(parvovirosis, perro).
padecimiento_especie(moquillo, perro).

padecimiento_especie(panleucopenia, gato).
padecimiento_especie(leucemia_felina, gato).

padecimiento_especie(insuficiencia_renal, perro).
padecimiento_especie(insuficiencia_renal, gato).

padecimiento_especie(intoxicacion_farmacologica, perro).
padecimiento_especie(intoxicacion_farmacologica, gato).

% ==========================================
% ACTIVIDAD 2
% ==========================================
signo_padecimiento(infeccion_respiratoria, tos).
signo_padecimiento(infeccion_respiratoria, fiebre).
signo_padecimiento(infeccion_respiratoria, secrecion_nasal).
signo_padecimiento(infeccion_respiratoria, estornudos).

signo_padecimiento(gastroenteritis, vomito).
signo_padecimiento(gastroenteritis, diarrea).
signo_padecimiento(gastroenteritis, letargo).
signo_padecimiento(gastroenteritis, dolor_abdominal).

signo_padecimiento(dermatitis_alergica, prurito).
signo_padecimiento(dermatitis_alergica, enrojecimiento_piel).
signo_padecimiento(dermatitis_alergica, perdida_de_pelo).
signo_padecimiento(dermatitis_alergica, costras).

signo_padecimiento(osteoartritis, cojera).
signo_padecimiento(osteoartritis, rigidez_al_caminar).
signo_padecimiento(osteoartritis, dificultad_para_levantarse).
signo_padecimiento(osteoartritis, dolor_articular).

signo_padecimiento(diabetes_mellitus, poliuria).
signo_padecimiento(diabetes_mellitus, polidipsia).
signo_padecimiento(diabetes_mellitus, polifagia).
signo_padecimiento(diabetes_mellitus, perdida_de_peso).

signo_padecimiento(lipidosis_hepatica, anorexia).
signo_padecimiento(lipidosis_hepatica, ictericia).
signo_padecimiento(lipidosis_hepatica, vomito).
signo_padecimiento(lipidosis_hepatica, perdida_de_peso_severa).

signo_padecimiento(parvovirosis, diarrea_sanguinolenta).
signo_padecimiento(parvovirosis, vomito_severo).
signo_padecimiento(parvovirosis, deshidratacion_rapida).
signo_padecimiento(parvovirosis, letargo_extremo).

signo_padecimiento(moquillo, secrecion_ocular_verdosa).
signo_padecimiento(moquillo, fiebre).
signo_padecimiento(moquillo, temblores_musculares).
signo_padecimiento(moquillo, endurecimiento_almohadillas).

signo_padecimiento(panleucopenia, fiebre_alta).
signo_padecimiento(panleucopenia, vomito).
signo_padecimiento(panleucopenia, diarrea).
signo_padecimiento(panleucopenia, depresion_profunda).

signo_padecimiento(leucemia_felina, perdida_de_peso).
signo_padecimiento(leucemia_felina, palidez_mucosas).
signo_padecimiento(leucemia_felina, gingivitis).
signo_padecimiento(leucemia_felina, infecciones_recurrentes).

signo_padecimiento(insuficiencia_renal, poliuria).
signo_padecimiento(insuficiencia_renal, polidipsia).
signo_padecimiento(insuficiencia_renal, vomito).
signo_padecimiento(insuficiencia_renal, mal_aliento).

signo_padecimiento(intoxicacion_farmacologica, vomito).
signo_padecimiento(intoxicacion_farmacologica, hipersalivacion).
signo_padecimiento(intoxicacion_farmacologica, convulsiones).
signo_padecimiento(intoxicacion_farmacologica, pupilas_dilatadas).

% ==========================================
% ACTIVIDAD 3
% ==========================================
:- dynamic paciente/2.
:- dynamic presenta/2.

registrar_paciente(Nombre, Especie) :-
    assertz(paciente(Nombre, Especie)).

registrar_sintoma(Nombre, Sintoma) :-
    assertz(presenta(Nombre, Sintoma)).

limpiar_paciente(Nombre) :-
    retractall(paciente(Nombre, _)),
    retractall(presenta(Nombre, _)).

% ==========================================
% ACTIVIDAD 6
% ==========================================
% atención veterinaria inmediata.
signo_alerta(convulsiones).
signo_alerta(diarrea_sanguinolenta).
signo_alerta(vomito_severo).
signo_alerta(deshidratacion_rapida).
signo_alerta(letargo_extremo).
signo_alerta(depresion_profunda).
signo_alerta(pupilas_dilatadas).

% revisión médica, paciente está estable.
signo_precaucion(vomito).
signo_precaucion(diarrea).
signo_precaucion(fiebre).
signo_precaucion(fiebre_alta).
signo_precaucion(letargo).
signo_precaucion(anorexia).
signo_precaucion(ictericia).

% presenta al menos un signo de alerta.
triaje(Animal, alto) :-
    presenta(Animal, Signo),
    signo_alerta(Signo),
    !.

% presenta un signo de precaución, pero se valida que no tenga ningún signo de alerta.
triaje(Animal, medio) :-
    presenta(Animal, Signo),
    \+ (presenta(Animal, SignoAlerta), signo_alerta(SignoAlerta)),
    signo_precaucion(Signo),
    !.

% no hay signos de alerta ni de precaución.
triaje(Animal, bajo) :-
    \+ (presenta(Animal, SignoAlerta), signo_alerta(SignoAlerta)),
    \+ (presenta(Animal, SignoPrecaucion), signo_precaucion(SignoPrecaucion)).

% ==========================================
% ACTIVIDAD 9
% ==========================================
analizar(Animal, Diagnostico, Porcentaje, Triaje, Recomendacion) :-
    posible_diagnostico(Animal, Diagnostico, Porcentaje),
    triaje(Animal, Triaje),
    recomendacion(Diagnostico, Recomendacion).

% ==========================================
% ACTIVIDAD 4
% ==========================================
diagnostico(Animal, infeccion_respiratoria) :-
    paciente(Animal, Especie),
    padecimiento_especie(infeccion_respiratoria, Especie),
    presenta(Animal, tos),
    presenta(Animal, fiebre),
    presenta(Animal, secrecion_nasal),
    presenta(Animal, estornudos).

diagnostico(Animal, gastroenteritis) :-
    paciente(Animal, Especie),
    padecimiento_especie(gastroenteritis, Especie),
    presenta(Animal, vomito),
    presenta(Animal, diarrea),
    presenta(Animal, letargo),
    presenta(Animal, dolor_abdominal).

diagnostico(Animal, dermatitis_alergica) :-
    paciente(Animal, Especie),
    padecimiento_especie(dermatitis_alergica, Especie),
    presenta(Animal, prurito),
    presenta(Animal, enrojecimiento_piel),
    presenta(Animal, perdida_de_pelo),
    presenta(Animal, costras).

diagnostico(Animal, osteoartritis) :-
    paciente(Animal, Especie),
    padecimiento_especie(osteoartritis, Especie),
    presenta(Animal, cojera),
    presenta(Animal, rigidez_al_caminar),
    presenta(Animal, dificultad_para_levantarse),
    presenta(Animal, dolor_articular).

diagnostico(Animal, diabetes_mellitus) :-
    paciente(Animal, Especie),
    padecimiento_especie(diabetes_mellitus, Especie),
    presenta(Animal, poliuria),
    presenta(Animal, polidipsia),
    presenta(Animal, polifagia),
    presenta(Animal, perdida_de_peso).

diagnostico(Animal, lipidosis_hepatica) :-
    paciente(Animal, Especie),
    padecimiento_especie(lipidosis_hepatica, Especie),
    presenta(Animal, anorexia),
    presenta(Animal, ictericia),
    presenta(Animal, vomito),
    presenta(Animal, perdida_de_peso_severa).

diagnostico(Animal, parvovirosis) :-
    paciente(Animal, Especie),
    padecimiento_especie(parvovirosis, Especie),
    presenta(Animal, diarrea_sanguinolenta),
    presenta(Animal, vomito_severo),
    presenta(Animal, deshidratacion_rapida),
    presenta(Animal, letargo_extremo).

diagnostico(Animal, moquillo) :-
    paciente(Animal, Especie),
    padecimiento_especie(moquillo, Especie),
    presenta(Animal, secrecion_ocular_verdosa),
    presenta(Animal, fiebre),
    presenta(Animal, temblores_musculares),
    presenta(Animal, endurecimiento_almohadillas).

diagnostico(Animal, panleucopenia) :-
    paciente(Animal, Especie),
    padecimiento_especie(panleucopenia, Especie),
    presenta(Animal, fiebre_alta),
    presenta(Animal, vomito),
    presenta(Animal, diarrea),
    presenta(Animal, depresion_profunda).

diagnostico(Animal, leucemia_felina) :-
    paciente(Animal, Especie),
    padecimiento_especie(leucemia_felina, Especie),
    presenta(Animal, perdida_de_peso),
    presenta(Animal, palidez_mucosas),
    presenta(Animal, gingivitis),
    presenta(Animal, infecciones_recurrentes).

diagnostico(Animal, insuficiencia_renal) :-
    paciente(Animal, Especie),
    padecimiento_especie(insuficiencia_renal, Especie),
    presenta(Animal, poliuria),
    presenta(Animal, polidipsia),
    presenta(Animal, vomito),
    presenta(Animal, mal_aliento).

diagnostico(Animal, intoxicacion_farmacologica) :-
    paciente(Animal, Especie),
    presenta(Animal, vomito),
    presenta(Animal, hipersalivacion),
    presenta(Animal, convulsiones),
    presenta(Animal, pupilas_dilatadas).

diagnostico_especie(Animal, Padecimiento) :-
    paciente(Animal, Especie),
    padecimiento_especie(Padecimiento, Especie),
    diagnostico(Animal, Padecimiento).

% ==========================================
% ACTIVIDAD 5
% ==========================================
% Contar signos de un padecimiento
cantidad_signos_padecimiento(Padecimiento, Cantidad) :-
    findall(
        Signo,
        signo_padecimiento(Padecimiento, Signo),
        Lista
    ),
    length(Lista, Cantidad).

% Contar signos coincidentes del paciente
cantidad_coincidencias(Animal, Padecimiento, Cantidad) :-
    findall(
        Signo,
        (
            signo_padecimiento(Padecimiento, Signo),
            presenta(Animal, Signo)
        ),
        Lista
    ),
    length(Lista, Cantidad).

% Calcular porcentaje
porcentaje_coincidencia(Animal, Padecimiento, Porcentaje) :-
    cantidad_signos_padecimiento(Padecimiento, Total),
    cantidad_coincidencias(Animal, Padecimiento, Coincidencias),
    Total > 0,
    Porcentaje is (Coincidencias * 100) / Total.

% Diagnóstico posible con 50 % o más
posible_diagnostico(Animal, Padecimiento, Porcentaje) :-
    paciente(Animal, Especie),
    padecimiento_especie(Padecimiento, Especie),
    porcentaje_coincidencia(Animal, Padecimiento, Porcentaje),
    Porcentaje >= 50.

% ==========================================
% ACTIVIDAD 7
% ==========================================
recomendacion(
    infeccion_respiratoria,
    'Aislar a la mascota de otros animales. Mantenerla en un lugar calido y sin corrientes de aire.'
).

recomendacion(
    gastroenteritis,
    'Retirar el alimento por 12-24 horas, pero mantener acceso a agua limpia para evitar deshidratacion. No administrar medicamentos de humanos. Acudir al veterinario si el vomito persiste.'
).

recomendacion(
    dermatitis_alergica,
    'Aplicar tratamiento antipulgas de uso veterinario. Evitar bañar en exceso a la mascota. Acudir al clinico para un tratamiento que controle la comezon y evite infecciones secundarias.'
).

recomendacion(
    osteoartritis,
    'Proporcionar una cama suave y evitar el ejercicio intenso o saltos. Es vital el control dietetico riguroso para mantener un peso adecuado y evitar agravamiento.'
).

recomendacion(
    diabetes_mellitus,
    'Requiere evaluacion veterinaria urgente para estabilizacion y posible terapia con insulina. Sera indispensable un manejo nutricional estricto y horarios de comida controlados.'
).

recomendacion(
    lipidosis_hepatica,
    'Emergencia medica. Los felinos no deben pasar mas de 48 horas sin comer. Acudir inmediatamente al veterinario; el pronostico mejora con soporte nutricional temprano (sonda).'
).

recomendacion(
    parvovirosis,
    'Altamente contagioso y letal. Aislar inmediatamente. Requiere hospitalizacion urgente para terapia de fluidos intravenosa y soporte medico. Desinfectar el area con cloro.'
).

recomendacion(
    moquillo,
    'Enfermedad viral grave. Aislar al paciente y acudir de inmediato a urgencias veterinarias. El tratamiento es de soporte intensivo.'
).

recomendacion(
    panleucopenia,
    'Alta mortalidad en gatos. Aislar al paciente. Requiere atencion veterinaria inmediata y hospitalizacion para manejo de fluidos y prevencion de sepsis.'
).

recomendacion(
    leucemia_felina,
    'Mantener al gato estrictamente en interiores para evitar contagios a otros. Ofrecer una dieta de alta calidad y acudir al veterinario para establecer un plan de control inmunologico.'
).

recomendacion(
    insuficiencia_renal,
    'Fomentar el consumo de agua. Acudir al veterinario para pruebas sanguineas. Requerira una dieta de prescripcion baja en fosforo y proteinas.'
).

recomendacion(
    intoxicacion_farmacologica,
    'Emergencia toxicolociga. NO inducir el vomito sin supervision medica ni administrar remedios caseros. Acudir inmediatamente a la clinica veterinaria con el empaque del farmaco o toxico ingerido.'
).

% ==========================================
% ACTIVIDAD 8
% ==========================================
medicamento_riesgoso(paracetamol, gato).
medicamento_riesgoso(paracetamol, perro).
medicamento_riesgoso(ibuprofeno, perro).
medicamento_riesgoso(ibuprofeno, gato).
medicamento_riesgoso(naproxeno, perro).
medicamento_riesgoso(naproxeno, gato).
medicamento_riesgoso(aspirina, gato).
medicamento_riesgoso(diclofenaco, perro).
medicamento_riesgoso(diclofenaco, gato).

advertencia_farmacologica(Animal, Medicamento, '¡ALERTA CRITICA! Este medicamento es ALTAMENTE TOXICO para la especie de su mascota. No lo administre, puede causar fallas organicas severas.') :-
    paciente(Animal, Especie),
    medicamento_riesgoso(Medicamento, Especie),
    !.

advertencia_farmacologica(Animal, Medicamento, 'El medicamento no esta registrado como toxicologico agudo en el sistema, pero NO se recomienda administrar medicamentos de humanos sin supervision.') :-
    paciente(Animal, Especie),
    \+ medicamento_riesgoso(Medicamento, Especie).

% ==========================================
% PERFIL Y CONSEJOS POR RAZA
% ==========================================
perfil_raza(
    husky_siberiano,
    'Alta energia, adaptado a climas frios y necesita ejercicio diario.',
    'Proporcionar ejercicio intenso, juegos y caminatas largas.',
    'Vigilar articulaciones, ojos y tolerancia al calor.'
).

perfil_raza(
    pastor_aleman,
    'Inteligente, activo, protector y de talla grande.',
    'Realizar ejercicio diario y actividades de estimulacion mental.',
    'Vigilar cadera, codos y problemas digestivos.'
).

perfil_raza(
    labrador,
    'Sociable, activo y con tendencia a ganar peso.',
    'Controlar porciones y mantener actividad fisica diaria.',
    'Vigilar obesidad, articulaciones y oidos.'
).

perfil_raza(
    golden_retriever,
    'Sociable, activo y de temperamento tranquilo.',
    'Mantener actividad fisica, cepillado frecuente y dieta equilibrada.',
    'Vigilar piel, articulaciones y peso corporal.'
).

perfil_raza(
    pug,
    'Perro pequeno, sociable y braquicefalo.',
    'Evitar ejercicio intenso y calor excesivo.',
    'Vigilar respiracion, ojos y control del peso.'
).

perfil_raza(
    chihuahua,
    'Perro pequeno, alerta y sensible al frio.',
    'Proporcionar actividad moderada y proteccion contra bajas temperaturas.',
    'Vigilar dentadura, rotula y niveles de glucosa.'
).

perfil_raza(
    beagle,
    'Activo, curioso y guiado por el olfato.',
    'Realizar paseos con correa y juegos de olfato.',
    'Vigilar peso, oidos y tendencia a escapar.'
).

perfil_raza(
    persa,
    'Gato tranquilo, de pelo largo y cara achatada.',
    'Cepillar diariamente y limpiar ojos con cuidado.',
    'Vigilar respiracion, ojos, piel y rinones.'
).

perfil_raza(
    siames,
    'Gato activo, comunicativo y social.',
    'Proporcionar juego, enriquecimiento ambiental y compania.',
    'Vigilar dentadura, respiracion y salud renal.'
).

perfil_raza(
    gato_domestico,
    'Gato adaptable con necesidades variables segun edad y actividad.',
    'Ofrecer juego diario, rascadores y alimentacion equilibrada.',
    'Realizar revisiones periodicas y vigilar peso y salud urinaria.'
).





















