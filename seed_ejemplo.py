"""Genera preguntas_ejemplo.csv con ~55 preguntas de muestra para la demo."""
import csv, random
from datetime import datetime, timedelta

random.seed(7)
temas = {
    "plan": ["¿Qué materias tiene el plan de estudios?", "¿Cuántos semestres dura la maestría?",
             "¿Cuántos créditos tiene el programa?", "¿Qué materias se llevan en el primer semestre?",
             "¿Hay materias optativas en el mapa curricular?", "¿Cuál es el mapa curricular?",
             "¿Cuántas materias se cursan por cuatrimestre?", "¿Hay materias de investigación en el plan de estudios?",
             "¿Cuándo se hace la tesis o proyecto final?", "¿Qué materias de innovación educativa incluye?"],
    "fechas": ["¿Cuándo inician las clases?", "¿Cuándo es la fecha de inscripción?",
               "¿Cuáles son las fechas del calendario 2026-2027?", "¿Cuándo terminan las clases del cuatrimestre?",
               "¿Cuándo son las vacaciones en el calendario?", "¿Hasta cuándo puedo inscribirme?",
               "¿Cuándo es el periodo de exámenes?", "¿Cuál es la fecha límite para entregar documentos?",
               "¿Cuándo empieza el siguiente ciclo escolar?", "¿Qué días no hay clases en el calendario?"],
    "validez": ["¿El programa tiene validez oficial?", "¿Está reconocido por la SEP?",
                "¿Cuál es el RVOE de la maestría?", "¿El título tiene validez en todo el país?",
                "¿Me dan cédula profesional al terminar?", "¿La universidad está acreditada oficialmente?",
                "¿Qué respaldo oficial tiene el posgrado?", "¿El grado sirve para trabajar en escuelas públicas?"],
    "requisitos": ["¿Qué requisitos necesito para ingresar?", "¿Qué documentos debo entregar para inscribirme?",
                   "¿Necesito título de licenciatura para entrar?", "¿Piden examen de admisión?",
                   "¿Hay requisito de promedio mínimo?", "¿Piden carta de motivos?",
                   "¿Necesito acreditar inglés para ingresar?", "¿Qué documentos piden en la convocatoria?"],
    "costos": ["¿Cuánto cuesta la colegiatura?", "¿Hay becas disponibles?", "¿Cuál es el costo de inscripción?",
               "¿Puedo pagar en parcialidades?", "¿Cuánto cuesta el programa completo?",
               "¿Hay descuento para egresados?", "¿Aceptan pago con tarjeta?"],
    "modalidad": ["¿Las clases son en línea o presenciales?", "¿Cuál es el horario de clases?",
                  "¿Las clases son entre semana o sábados?", "¿Puedo trabajar y estudiar al mismo tiempo?",
                  "¿Hay clases por las noches?"],
}
sin_respuesta = {"costos", "modalidad"}  # temas que el bot no encuentra en los PDFs

filas, t0 = [], datetime(2026, 10, 12, 9, 0)
usuarios = [f"u{random.randint(10**9, 10**10-1):x}"[:10] for _ in range(14)]
for tema, preguntas in temas.items():
    for p in preguntas:
        t0 += timedelta(minutes=random.randint(20, 400))
        resp = int(not (tema in sin_respuesta and random.random() < 0.8))
        filas.append([t0.isoformat(timespec="seconds"), random.choice(usuarios), p, "(ejemplo)", resp])
random.shuffle(filas)
filas.sort(key=lambda f: f[0])

with open("preguntas_ejemplo.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["fecha", "usuario", "pregunta", "respuesta", "respondida"])
    w.writerows(filas)
print(len(filas), "preguntas generadas")
