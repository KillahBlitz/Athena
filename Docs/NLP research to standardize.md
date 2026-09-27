# nlp_research_to_standardize

## 1. resumen_ejecutivo_y_contexto_del_proyecto_athena

el proyecto **athena** (*sistema inteligente basado en aprendizaje automático para la recomendación vocacional de carreras del instituto politécnico nacional en la ciudad de méxico*) tiene como meta reducir la deserción escolar orientando a los aspirantes de educación media superior mediante el análisis de sus competencias reales frente a la oferta del ipn.

### flujo_general_del_sistema
1. **captura_de_datos:** el aspirante selecciona su área de conocimiento (por ejemplo, ingeniería y ciencias físico-matemáticas) y contesta preguntas abiertas organizadas bajo la metodología **star** (*situación*, *tarea*, *acción*, *resultado*).
2. **extraccion_y_normalizacion_nlp:** el módulo de procesamiento de lenguaje natural interpreta las narrativas de texto libre para identificar evidencias de habilidades y homologarlas directamente contra el catálogo oficial (`habilidad`, `criterio`, `carrera_habilidad`).
3. **puntuacion_de_evidencia:** se calcula numéricamente el grado de cumplimiento de cada habilidad (`cumplimiento_criterio` entre 0.0 y 1.0) y se almacena en la tabla `usuario_habilidad`.
4. **clasificador_supervisado:** el modelo clasificador toma el vector estructurado de habilidades evaluadas y predice la afinidad del aspirante respecto a las carreras del área seleccionada, devolviendo las 3 mejores opciones (**top 3**) con su porcentaje de coincidencia.

el reto central consiste en convertir texto informal y cualitativo en registros discretos y normalizados compatibles con la base de datos relacional, sin sufrir alucinaciones de texto libre ni latencias prolongadas.

---

## 2. modelos_system_one_jev_y_laya

frente a los modelos generativos autoregresivos tradicionales (*system two* como gpt o gemini, que decodifican texto palabra por palabra con tiempos de respuesta elevados y salidas difíciles de gobernar), han surgido los **modelos de decisión system one**:

* **naturaleza_no_autoregresiva:** no generan prosa libre; reciben un contexto estructurado y un conjunto definido de opciones o escalas, emitiendo decisiones tipadas en milisegundos (~30 a 80 ms).
* **primitivas_de_decision:**
  * `choice`: selecciona una o varias opciones discretas dentro de una lista cerrada (homologación contra el catálogo de habilidades).
  * `score`: calibra una intensidad o nivel de desempeño en una escala continua u ordinal (determinación de `cumplimiento_criterio` entre 0.0 y 1.0).
  * `bernoulli` / `noul`: decisión booleana con probabilidad calibrada ($p \in [0.0, 1.0]$) sobre si una evidencia está presente o no.
* **calibracion_probabilistica (rlcd):** sus probabilidades reflejan certidumbre estadística real, permitiendo establecer umbrales matemáticos para descartar respuestas ambiguas o insuficientes.

### comparativa_tecnica

| parametro | jev (typesafe ai) | laya (convai innovations) | llm generativo tradicional |
| :--- | :--- | :--- | :--- |
| **tipo_modelo** | propietario / cloud api | open-source (apache 2.0) | fundacional autoregresivo |
| **despliegue** | api en la nube | contenedor local / docker | api cloud externa |
| **latencia_promedio** | ~50 a 100 ms | < 30 a 50 ms (gpu / cpu) | 1,500 a 4,000 ms |
| **formato_salida** | tipos nativos (primitivas) | tipos nativos (primitivas) | json generado por texto |
| **calibracion_score** | alta (vía rlcd) | alta (vía rlcd) | baja (sobreconfianza) |
| **riesgo_alucinacion** | nulo (conjunto cerrado) | nulo (conjunto cerrado) | latente en texto libre |

---

## 3. como_ayudan_en_la_homologacion_y_clasificacion

1. **anclaje_estricto_a_la_base_de_datos:**  
   el extractor presenta al modelo únicamente las descripciones de habilidades recuperadas de la tabla `habilidad`. el modelo no puede emitir nombres inventados, garantizando integridad referencial con `id_habilidad`.
2. **asignacion_directa_de_cumplimiento:**  
   mediante la primitiva `score`, la evidencia demostrada en la *acción* y el *resultado* de la respuesta star se mapea numéricamente a `cumplimiento_criterio`, listo para inserción en `usuario_habilidad`.
3. **deteccion_de_respuestas_insuficientes:**  
   si ninguna habilidad candidata supera el umbral de certeza probabilística, el sistema detecta de inmediato que la respuesta carece de detalle suficiente (cumpliendo el requerimiento funcional de validación de contenido star).
4. **alimentacion_limpia_al_clasificador:**  
   al recibir un vector normalizado de habilidades con puntajes reales entre 0.0 y 1.0, el clasificador opera sobre atributos limpios, consistentes y sin ruido textual.

---

## 4. arquitectura_del_flujo_nlp

```
[respuesta star del estudiante]
            │
            ▼
[recuperacion rag / embedding]
  -> filtra habilidades candidatas por id_area en postgresql
            │
            ▼
[homologador system one (laya o jev)]
  -> choice / bernoulli: verifica presencia de cada habilidad
  -> score: calibra cumplimiento_criterio [0.0 - 1.0]
            │
            ▼
[insercion estructurada en usuario_habilidad]
            │
            ▼
[clasificador supervisado]
  -> inferencia de compatibilidad y ranking top 3 de carreras
```

---

## 5. ejemplos_practicos_de_implementacion

a continuación se presentan ejemplos funcionales en python que ilustran la integración de ambas herramientas en el backend del proyecto.

### 5.1 ejemplo_practico_con_jev_api

este ejemplo ilustra cómo consumir la api de **jev** para evaluar si una respuesta star evidencia una habilidad específica y obtener su puntaje normalizado:

```python
import os
import requests
from typing import Dict, Any, Optional

# configuracion_del_cliente_jev
JEV_API_KEY = os.getenv("JEV_API_KEY", "tu_api_key_aqui")
JEV_ENDPOINT = "https://api.typesafe.ai/v1/decision"

def evaluar_habilidad_con_jev(
    texto_star: str,
    id_habilidad: int,
    nombre_habilidad: str,
    criterios_evaluacion: list[str]
) -> Dict[str, Any]:
    """
    evalua una habilidad del catalogo frente a la narrativa star
    utilizando las primitivas choice y score de jev.
    """
    encabezados = {
        "Authorization": f"Bearer {JEV_API_KEY}",
        "Content-Type": "application/json"
    }

    # payload estructurado con el contexto y la regla de evaluacion
    cuerpo_peticion = {
        "context": {
            "narrativa_star": texto_star,
            "habilidad_objetivo": {
                "id": id_habilidad,
                "nombre": nombre_habilidad,
                "criterios": criterios_evaluacion
            }
        },
        "query": f"¿el estudiante demuestra activamente la competencia '{nombre_habilidad}'?",
        "decisions": {
            # primitiva bernoulli para deteccion booleana con probabilidad
            "evidencia_detectada": {
                "type": "bernoulli",
                "threshold": 0.65
            },
            # primitiva score para obtener cumplimiento en rango [0.0, 1.0]
            "cumplimiento_criterio": {
                "type": "score",
                "min": 0.0,
                "max": 1.0,
                "calibration": "rlcd"
            }
        }
    }

    respuesta = requests.post(JEV_ENDPOINT, json=cuerpo_peticion, headers=encabezados, timeout=5)
    respuesta.raise_for_status()
    resultado = respuesta.json()

    # extraccion de resultados tipados
    evidencia = resultado["decisions"]["evidencia_detectada"]["value"]
    probabilidad = resultado["decisions"]["evidencia_detectada"]["probability"]
    cumplimiento = resultado["decisions"]["cumplimiento_criterio"]["value"]

    return {
        "id_habilidad": id_habilidad,
        "nombre_habilidad": nombre_habilidad,
        "es_valida": evidencia and probabilidad >= 0.70,
        "probabilidad_certeza": round(probabilidad, 4),
        "cumplimiento_criterio": round(cumplimiento, 2) if evidencia else 0.0
    }

# caso_de_prueba_jev
if __name__ == "__main__":
    respuesta_estudiante_star = (
        "situacion: en el proyecto final de física teníamos discrepancias sobre el circuito a armar. "
        "tarea: debíamos entregar el prototipo funcional en tres días y coordinar el trabajo en equipo. "
        "accion: organicé una sesión de lluvia de ideas, dividí las mediciones según fortalezas de cada uno "
        "y propuse una prueba modular para validar voltajes paso a paso. "
        "resultado: terminamos el circuito con 24 horas de anticipación y obtuvimos la calificación máxima."
    )

    habilidad_prueba = {
        "id_habilidad": 12,
        "nombre_habilidad": "resolución de problemas y trabajo en equipo",
        "criterios": [
            "propone soluciones estructuradas ante contingencias",
            "coordina actividades de forma colaborativa"
        ]
    }

    resultado_evaluacion = evaluar_habilidad_con_jev(
        texto_star=respuesta_estudiante_star,
        id_habilidad=habilidad_prueba["id_habilidad"],
        nombre_habilidad=habilidad_prueba["nombre_habilidad"],
        criterios_evaluacion=habilidad_prueba["criterios"]
    )

    print("resultado jev:", resultado_evaluacion)
```

---

### 5.2 ejemplo_practico_con_laya (local / contenedor docker)

este ejemplo utiliza el paquete de inferencia local de **laya** (`laya-engine` o el runtime encoder de decisiones), idóneo para correr dentro de los microservicios sin dependencias externas:

```python
from typing import List, Dict, Any
# hipotetica importacion del sdk open source laya
from laya import DecisionEngine, DecisionPrimitive

# inicializacion del motor de decision local
motor_laya = DecisionEngine.load_model(
    model_name_or_path="convai/laya-decision-base-es",
    device="cpu"  # o "cuda" para aceleracion por tarjeta grafica
)

def homologar_habilidades_laya(
    narrativa_star: str,
    catalogo_habilidades_candidatas: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    evalua un conjunto de habilidades candidatas recuperadas de la base de datos
    contra la respuesta star del usuario de manera paralela y no autoregresiva.
    """
    habilidades_homologadas = []

    for item in catalogo_habilidades_candidatas:
        id_hab = item["id_habilidad"]
        nombre_hab = item["descripcion"]
        subcriterios = item.get("criterios", [])

        # contexto estructurado de entrada
        contexto = {
            "texto_usuario": narrativa_star,
            "definicion_habilidad": nombre_hab,
            "criterios": subcriterios
        }

        # ejecucion de la decision tipada en milisegundos
        decision = motor_laya.evaluate(
            context=contexto,
            decisions=[
                DecisionPrimitive.Bernoulli(
                    name="evidencia_demostrada",
                    prompt=f"¿el texto refleja que el estudiante posee y aplica '{nombre_hab}'?"
                ),
                DecisionPrimitive.Score(
                    name="grado_cumplimiento",
                    prompt="califica de 0.0 a 1.0 el nivel de competencia y resolucion alcanzado",
                    min_val=0.0,
                    max_val=1.0
                )
            ]
        )

        es_valida = decision["evidencia_demostrada"].as_bool(threshold=0.60)
        score_cumplimiento = decision["grado_cumplimiento"].as_float()

        if es_valida and score_cumplimiento > 0.20:
            habilidades_homologadas.append({
                "id_habilidad": id_hab,
                "cumplimiento_criterio": round(score_cumplimiento, 2),
                "confianza": round(decision["evidencia_demostrada"].probability, 3)
            })

    return habilidades_homologadas

# caso_de_prueba_laya
if __name__ == "__main__":
    texto_usuario = (
        "teníamos que programar un algoritmo para clasificar datos de laboratorio. "
        "analicé el conjunto de datos, corregí los valores nulos con python y ajusté "
        "los hiperparámetros para mejorar la precisión del modelo."
    )

    candidatos_bd = [
        {"id_habilidad": 4, "descripcion": "pensamiento analítico y resolución cuantitativa", "criterios": ["manejo de datos"]},
        {"id_habilidad": 9, "descripcion": "comunicación oral y expresión gráfica", "criterios": ["presentación de resultados"]},
        {"id_habilidad": 15, "descripcion": "habilidad lógico-matemática y algorítmica", "criterios": ["lógica computacional"]}
    ]

    habilidades_encontradas = homologar_habilidades_laya(texto_usuario, candidatos_bd)
    print("habilidades homologadas por laya:", habilidades_encontradas)
```

---

### 5.3 integracion_con_el_clasificador_y_la_base_de_datos

una vez extraídas y homologadas las habilidades mediante jev o laya, se consolidan e insertan en `usuario_habilidad` para transferirlas al clasificador supervisado:

```python
import psycopg2
from psycopg2.extras import execute_values
from typing import List, Dict, Any

def persistir_habilidades_y_alimentar_clasificador(
    id_usuario: int,
    id_area: int,
    habilidades_evaluadas: List[Dict[str, Any]],
    conexion_bd
) -> List[tuple]:
    """
    inserta los registros homologados en usuario_habilidad y extrae
    el vector de atributos preparado para el modelo clasificador.
    """
    cursor = conexion_bd.cursor()

    # 1. preparacion de tuplas para insercion en usuario_habilidad
    datos_insercion = [
        (id_usuario, item["id_habilidad"], item["cumplimiento_criterio"])
        for item in habilidades_evaluadas
    ]

    consulta_insert = """
        INSERT INTO usuario_habilidad (id_usuario, id_habilidad, cumplimiento_criterio)
        VALUES %s
        ON CONFLICT DO NOTHING;
    """
    execute_values(cursor, consulta_insert, datos_insercion)
    conexion_bd.commit()

    # 2. consulta del vector consolidado para el clasificador de carreras
    consulta_vector_carreras = """
        SELECT 
            c.id_carrera,
            c.nombre_carrera,
            COUNT(ch.id_habilidad) AS total_habilidades_requeridas,
            COUNT(uh.id_habilidad) AS habilidades_coincidentes,
            COALESCE(SUM(uh.cumplimiento_criterio), 0.0) AS suma_cumplimiento
        FROM carrera c
        JOIN carrera_habilidad ch ON ch.id_carrera = c.id_carrera
        LEFT JOIN usuario_habilidad uh ON uh.id_habilidad = ch.id_habilidad 
                                      AND uh.id_usuario = %s
        WHERE c.id_area = %s
        GROUP BY c.id_carrera, c.nombre_carrera
        ORDER BY suma_cumplimiento DESC;
    """
    cursor.execute(consulta_vector_carreras, (id_usuario, id_area))
    filas_vector = cursor.fetchall()
    cursor.close()

    # estas filas alimentan directamente la matriz x_test del clasificador
    return filas_vector
```

---

## 6. recomendaciones_de_adopcion

1. **etapa_de_desarrollo_y_pruebas:** usar **jev** vía api para prototipar rápidamente las preguntas star y calibrar las escalas de evaluación sin requerir infraestructura adicional.
2. **etapa_productiva_en_gcp / docker:** empaquetar **laya** como microservicio independiente en python/fastapi. esto asegura:
   * latencias menores a 50 ms por respuesta.
   * total apego a la privacidad de datos personales de los estudiantes.
   * ausencia de costos recurrentes por llamadas externas.
