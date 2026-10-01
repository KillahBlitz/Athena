# Requisitos Funcionales

**Estado:** especificación documental; no acredita implementación ni resultados.

**Fuente:** document.md · especificación de requerimientos. Véase [[tesis/referencias#Fuentes, cobertura y decisiones pendientes|Fuentes y pendientes]].

Se conservan los identificadores y el contenido de los requisitos originales.

## RF 1 · Información en Pantalla de Inicio.

La plataforma deberá presentar, en su pantalla de inicio, información introductoria sobre el sistema: en qué consiste, cuál es el objetivo del servicio, cómo se utiliza la plataforma y cómo debe responderse el cuestionario de manera adecuada. Al presionar el botón "Comenzar", el sistema deberá redirigir al usuario a la pantalla de recopilación de datos personales.

**Relacionado:** [[tesis/implementacion#Plataforma web y navegación|Plataforma web y navegación]]

## RF 2.4 · Términos y Condiciones

La plataforma deberá mostrar una casilla de verificación con la etiqueta “He leído y acepto los términos y condiciones”, acompañada de un enlace para consultar su contenido. La casilla deberá estar desmarcada de forma predeterminada y su aceptación será obligatoria para continuar con el cuestionario.  Los términos y condiciones deberán indicar lo siguiente:   * La plataforma tiene una finalidad exclusivamente académica y no persigue fines de lucro. * Su uso constituye un recurso complementario para la orientación vocacional y no sustituye la asesoría de un profesional en esta área. * No se garantiza que los resultados sean totalmente precisos ni que determinen de manera definitiva la elección vocacional de la persona usuaria. * Los resultados deberán contrastarse con la opinión de un profesional de orientación vocacional antes de utilizarlos como base para tomar decisiones académicas o profesionales.

**Relacionado:** [[tesis/implementacion#Plataforma web y navegación|Plataforma web y navegación]]

## RF 2 · Cuestionario de Información Personal

La plataforma deberá mostrar un cuestionario con campos para capturar el nombre y el correo electrónico de la persona usuaria. El cuestionario deberá incluir un botón con la etiqueta “Siguiente” para avanzar a la siguiente etapa.

**Relacionado:** [[tesis/implementacion#Plataforma web y navegación|Plataforma web y navegación]]

## RF 3 · Cuestionario de Selección de Área

La plataforma deberá permitir que la persona usuaria seleccione el área de conocimiento en la que desea realizar la prueba de orientación vocacional. Únicamente podrá seleccionarse un área por aplicación de la prueba. La plataforma deberá mostrar el cuestionario correspondiente al área seleccionada. Deberá tener un botón para continuar con el cuestionario.

**Relacionado:** [[tesis/implementacion#Plataforma web y navegación|Plataforma web y navegación]]

## RF 4 · Cuestionario Selección de Habilidades

La plataforma deberá presentar un cuestionario con la pregunta “Antes de comenzar, ¿qué habilidades consideras que son tus fortalezas?”. El usuario podrá seleccionar múltiples habilidades y avanzar a la siguiente etapa del formulario mediante el botón “Siguiente”.

**Relacionado:** [[tesis/preparacion-de-la-informacion#ETL y catálogo del IPN|ETL y catálogo del IPN]]

## RF 5 · Cuestionario STAR

La plataforma deberá presentar un cuestionario compuesto por cuatro situaciones orientadas a identificar habilidades de la persona usuaria mediante sus experiencias previas. Las preguntas deberán adaptarse al área de conocimiento seleccionada y mostrarse en pantallas con una estructura uniforme.  Para cada situación, la plataforma deberá solicitar una respuesta organizada en los siguientes componentes del método STAR e indicar la distribución sugerida del tiempo de respuesta:   1. **Situación (10 %):** describir el contexto, el problema o el reto enfrentado. 2. **Tarea (10 %):** explicar el objetivo que se buscaba alcanzar o la responsabilidad asumida. 3. **Acción (60 %):** detallar las acciones realizadas personalmente para atender la situación, incluyendo las decisiones tomadas y los pasos seguidos. 4. **Resultado (20 %):** describir el desenlace, los logros y los aprendizajes obtenidos, incluyendo datos o cifras cuando corresponda.   Las situaciones podrán referirse a experiencias escolares, personales o laborales. Los porcentajes deberán presentarse como una guía para desarrollar la respuesta.  **Preguntas base para adaptar por área**   1. Describe una ocasión en la que tuviste un conflicto con un compañero de estudio, de trabajo o con un cliente. ¿Cuál fue tu responsabilidad, qué acciones realizaste para atenderlo y cuál fue el resultado? 2. Cuéntanos sobre una ocasión en la que trabajaste con alguien cuya personalidad o forma de trabajar era diferente de la tuya. ¿Qué debían lograr, cómo contribuiste a la colaboración y qué resultado obtuvieron? 3. Describe una situación en la que tu equipo no estuvo de acuerdo con tu punto de vista. ¿Qué objetivo buscaban, cómo abordaste el desacuerdo y cuál fue el desenlace? 4. Relata una ocasión en la que enfrentaste un problema inesperado durante una actividad o proyecto. ¿Qué debías resolver, qué pasos seguiste y qué lograste?   La plataforma deberá permitir completar los componentes de cada situación y avanzar a la siguiente mediante el botón “Siguiente” y “Volver” en caso de que desee corregir el cuestionario anterior. En la cuarta situación, deberá mostrar el botón “Continuar” para avanzar a la siguiente etapa del formulario.

**Relacionado:** [[tesis/implementacion#Cuestionario STAR|Cuestionario STAR]]

## RF 6.2 · Pantalla de Error

En caso de que no exista una coincidencia con cierto asertividad, la plataforma mostrara la pantalla de error indicando que la evaluación no se contestó de manera adecuada y no fue posible encontrar una coincidencia con las habilidades descritas en el cuestionario, explicándole al usuario que vuelva a intentarlo o intente en otra área.

### Conflicto por resolver

La atribución de este resultado a una contestación inadecuada contradice RNF 6.1 y RNF 5.1. Se conserva el requisito para trazabilidad; debe conciliarse antes de implementar el mensaje. Véase [[tesis/requisitos-no-funcionales#RNF 6.1 · Interacción con resultados|RNF 6.1]] y [[tesis/requisitos-no-funcionales#RNF 5.1 · Restricciones de entradas de texto en cuestionario STAR|RNF 5.1]].

**Relacionado:** [[tesis/clasificacion-supervisada#Afinidad y construcción de recomendaciones|Afinidad y construcción de recomendaciones]]

## RF 6 · Resultados

La plataforma deberá mostrar las tres carreras con mayor porcentaje de coincidencia con el perfil identificado, ordenadas de mayor a menor. Para cada carrera se deberá presentar:   * Nombre de la carrera. * Posición dentro de los resultados: 1, 2 o 3. * Porcentaje de coincidencia. * Escuelas que ofertan la carrera.   Cuando no se obtengan resultados, la plataforma deberá mostrar la pantalla definida en el requerimiento de ausencia de resultados.  Se deberá incluir un botón “Descargar reporte” que abra el diálogo de impresión del navegador, equivalente a la acción de «Cmd + P», desde el cual la persona usuaria podrá guardar el reporte como PDF.

**Relacionado:** [[tesis/clasificacion-supervisada#Afinidad y construcción de recomendaciones|Afinidad y construcción de recomendaciones]]

## Enlaces

- [[tesis/requisitos-no-funcionales|Requisitos No Funcionales]]
- [[tesis/requisitos-implementacion|Requisitos de Implementación]]
- [[tesis/requisitos-interfaz|Requisitos de Interfaz]]
- [[index-tesis|Volver al índice de tesis]]
