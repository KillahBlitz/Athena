# Requisitos No Funcionales

**Estado:** especificación documental; no acredita implementación ni resultados.

**Fuente:** document.md · especificación de requerimientos. Véase [[tesis/referencias#Fuentes, cobertura y decisiones pendientes|Fuentes y pendientes]].

Se conservan los identificadores y el contenido de los requisitos originales.

## RNF 2.1 · Restricciones del Campo de Nombre

El campo “Nombre” deberá admitir únicamente caracteres alfabéticos y tener una longitud mínima de 3 caracteres y máxima de 60 caracteres.

**Relacionado:** [[tesis/implementacion#Plataforma web y navegación|Plataforma web y navegación]]

## RNF 2.2 · Restricciones del campo email

El campo “Correo electrónico” deberá aceptar únicamente direcciones con un formato válido, compuesto por un nombre de usuario, el símbolo “@” y un dominio con su extensión, separados por un punto. Ejemplo: usuario@dominio.com.

**Relacionado:** [[tesis/implementacion#Plataforma web y navegación|Plataforma web y navegación]]

## RNF 2.3 · Uso de Datos Personales

Los datos recopilados mediante este cuestionario se utilizarán exclusivamente con fines estadísticos. Proporcionar esta información no constituirá un registro ni creará una cuenta en la plataforma.

**Relacionado:** [[tesis/implementacion#Plataforma web y navegación|Plataforma web y navegación]]

## RNF 3.1 · Selección de Área

La plataforma deberá limitar la selección a las siguientes tres áreas de conocimiento del Instituto Politécnico Nacional (IPN):   1. Ingeniería y Ciencias Físico Matemáticas. 2. Ciencias Médico Biológicas. 3. Ciencias Sociales y Administrativas.   No se permitirá ingresar áreas de forma manual ni seleccionar opciones distintas de las establecidas.

**Relacionado:** [[tesis/implementacion#Plataforma web y navegación|Plataforma web y navegación]]

## RNF 4.1 · Catálogo de Habilidades

El catálogo deberá integrarse con las habilidades recopiladas de los perfiles de ingreso de las carreras del Instituto Politécnico Nacional (IPN). El cuestionario deberá mostrar exclusivamente las habilidades correspondientes al área de conocimiento seleccionada previamente por el usuario.

**Relacionado:** [[tesis/preparacion-de-la-informacion#ETL y catálogo del IPN|ETL y catálogo del IPN]]

## RNF 4.2 · Selección de Habilidades

La persona usuaria deberá seleccionar al menos una habilidad para continuar con el formulario.

**Relacionado:** [[tesis/preparacion-de-la-informacion#ETL y catálogo del IPN|ETL y catálogo del IPN]]

## RNF 5.1 · Restricciones de entradas de texto en cuestionario STAR

La plataforma deberá solicitar respuestas claras y detalladas que describan el contexto de cada situación, la responsabilidad asumida, las acciones realizadas y los resultados obtenidos. Cada pregunta deberá incluir una indicación que invite a proporcionar ejemplos concretos y explicar la participación personal.  Las respuestas vacías, ajenas a la pregunta o que no aporten información sobre la experiencia descrita deberán considerarse insuficientes para identificar habilidades. La suficiencia de una respuesta deberá depender de su contenido y no únicamente de su extensión.  Cuando la información proporcionada en el cuestionario sea insuficiente para identificar habilidades y relacionarlas con los perfiles de las carreras del área seleccionada, la plataforma deberá informar que no es posible generar una recomendación con las respuestas recibidas, mediante el siguiente mensaje:  «Tus respuestas no contienen suficiente información para identificar tus habilidades y generar una recomendación de carreras en el área seleccionada. Describe con mayor detalle las situaciones, tus responsabilidades, las acciones que realizaste y los resultados que obtuviste».  La falta de información no deberá interpretarse ni comunicarse como ausencia de habilidades o incompatibilidad con las carreras del área.

**Relacionado:** [[tesis/implementacion#Cuestionario STAR|Cuestionario STAR]]

## RNF 6.1 · Interacción con resultados

Cuando ninguna carrera alcance el porcentaje mínimo de coincidencia establecido para generar una recomendación, la plataforma deberá mostrar una pantalla de ausencia de resultados.  El mensaje deberá explicar que las respuestas no permitieron identificar una coincidencia suficiente entre las habilidades descritas y las carreras del área seleccionada, sin atribuir necesariamente este resultado a una contestación incorrecta.  La pantalla deberá mostrar el siguiente mensaje:  “No encontramos una coincidencia suficiente para recomendarte una carrera en el área seleccionada. Puedes intentarlo nuevamente describiendo con mayor detalle tus experiencias, acciones y resultados, o realizar el cuestionario en otra área de conocimiento”.  La plataforma deberá ofrecer las opciones “Intentar nuevamente” y “Elegir otra área”.

**Relacionado:** [[tesis/clasificacion-supervisada#Afinidad y construcción de recomendaciones|Afinidad y construcción de recomendaciones]]

## Enlaces

- [[tesis/requisitos-funcionales|Requisitos Funcionales]]
- [[tesis/requisitos-implementacion|Requisitos de Implementación]]
- [[tesis/requisitos-interfaz|Requisitos de Interfaz]]
- [[index-tesis|Volver al índice de tesis]]
