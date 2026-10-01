# Requisitos de Interfaz

**Estado:** especificación documental; no acredita implementación ni resultados.

**Fuente:** document.md · especificación de requerimientos. Véase [[tesis/referencias#Fuentes, cobertura y decisiones pendientes|Fuentes y pendientes]].

Se conservan los identificadores y el contenido de los requisitos originales.

## RI 1.1 · Pantalla de Inicio.

La pantalla de inicio deberá contener, en el siguiente orden: (1) una frase principal, centrada, con el texto "Descubre tu camino profesional"; (2) un texto introductorio ubicado debajo de la frase principal; (3) una explicación del funcionamiento de la plataforma, ubicada debajo del texto introductorio, que describa cómo debe usarse el sistema; y (4) un botón de acción con la etiqueta "COMENZAR", ubicado al final de la pantalla.

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI 2.5 · Pantalla de Cuestionario de Información Personal

La plataforma deberá mostrar una pantalla titulada “Cuestionario de información personal”, con los siguientes elementos: **Campo Nombre, Campo Correo electrónico, Aviso sobre el uso de los datos, Acceso a los términos y condiciones, Casilla de aceptación, Botón Siguiente**  Los elementos deberán presentarse en un orden claro, con etiquetas visibles, textos legibles y una distribución adaptable a dispositivos móviles y computadoras. Los mensajes de validación deberán aparecer junto al elemento correspondiente y no depender únicamente del color para comunicar un error.

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI 3.2 · Pantalla de Selección de Área

La pantalla deberá presentar el título “Selecciona tu área de conocimiento” y, debajo, el texto “Elige el área de tu interés para realizar la prueba de orientación vocacional”.  En la sección central se mostrarán tres tarjetas de igual tamaño, con bordes redondeados y separación uniforme. Cada tarjeta incluirá un indicador circular de selección, un ícono representativo y el nombre del área. La tarjeta seleccionada se distinguirá mediante un borde resaltado, un fondo de color tenue y el indicador circular marcado.  En la parte inferior se ubicará un botón con la etiqueta Siguiente, destacado con el color principal de la plataforma.

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI 4.3 · Pantalla de Selección de Habilidades

La pantalla deberá mostrar la pregunta “Antes de comenzar, ¿qué habilidades consideras que son tus fortalezas?” centrada en la parte superior y con un tamaño de letra destacado.  Debajo de la pregunta se presentará una lista vertical de habilidades. Cada elemento incluirá una casilla de selección a la izquierda y el nombre de la habilidad a la derecha, con alineación uniforme y espacio suficiente entre los elementos. Las casillas marcadas se distinguirán mediante una palomita y el color principal de la plataforma.  En la parte inferior derecha se ubicará el botón «Siguiente», con un color destacado y una etiqueta legible. La pantalla mantendrá un fondo claro, textos con contraste suficiente y un estilo visual consistente con las pantallas anteriores.

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI 5.2 · Pantallas de Cuestionarios STAR

Las preguntas deberán mostrarse con tipografía legible, en negritas y con un tamaño mayor al del texto de apoyo, para distinguirlas claramente.  Cada pregunta estará acompañada de un cuadro de texto de varias líneas, con fondo blanco, borde gris y esquinas redondeadas. En su interior se mostrará el texto de ejemplo “Describe tu experiencia con detalle…” en color gris tenue.  El texto escrito tendrá un color oscuro y un tamaño legible. Todas las preguntas y sus cuadros de texto conservarán el mismo estilo visual.

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI 6.3 · Pantalla de Resultados

La pantalla mostrará el título “Resultados de orientación vocacional” y el texto introductorio “Estas son las carreras con mayor coincidencia con las habilidades identificadas en tus respuestas”.  Tomando como referencia el estilo de la imagen, se utilizará un fondo verde menta con círculos decorativos en tonos claros y un contenedor translúcido con bordes redondeados.  Cada carrera se presentará en una tarjeta de fondo claro y esquinas redondeadas, con los siguientes elementos gráficos:   * Una insignia con el número de posición: «1», «2» o «3». * El nombre de la carrera en negritas y con un tamaño destacado. * El porcentaje de coincidencia en una cifra visible, acompañado de la etiqueta «Coincidencia» y una barra horizontal que represente ese porcentaje. * La etiqueta «Escuelas que la ofertan», seguida de los nombres de las escuelas en forma de lista.   Las tres tarjetas compartirán el mismo estilo. La primera tendrá un borde de color más intenso para destacar su posición.  El botón «Descargar reporte» tendrá un ícono de descarga y un color contrastante. El pie de página mostrará una nota sobre el propósito académico de la plataforma y su carácter complementario a la orientación profesional.

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI 6.4 · Pantalla de Error en Resultados

La pantalla deberá presentar un ícono informativo y el título “No encontramos una coincidencia suficiente”, con tipografía destacada.  El mensaje explicativo aparecerá en un recuadro de fondo claro y bordes redondeados, con texto oscuro y legible. Se utilizarán colores neutros, acordes con la identidad visual de la plataforma.  Se mostrarán dos botones: “Intentar nuevamente”, con el color principal de la plataforma, y “Elegir otra área”, con fondo claro y borde del mismo color. Ambos tendrán etiquetas visibles y esquinas redondeadas.

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI I · Tipografía principal

Se establece IBM Plex Sans como la única familia tipográfica (sans-serif) para toda la interfaz

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI J · Jerarquía tipográfica y tamaños

Cuerpo base de texto: Configurado en 18px  Títulos principales (H1): Establecidos en 32px  Títulos secundarios (H2): Fijados en 24px  Texto secundario y metadatos: Establecido en 16px

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI K · Interlineado y espaciado

Interlineado general: Con un valor ideal de 1.5  Interlineado para campos abiertos: Fijado en 1.6  Espaciado para títulos: Ajustado a 0.01em  Margen inferior de bloques: En 1.25rem

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI L · Paleta de colores

Fondo general: #A8C1B6  Primer plano / Texto principal: #2E2E2E  Elementos interactivos: #53C9AF  Mensajes de error: #DB3539

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI M · Arquitectura de navegación

Estructura secuencial fragmentada en pantallas

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI N · Indicador de progreso

Indicador minimalista que marca el avance actual

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI O · Micro-interacciones y animaciones

Transiciones de pantalla y animaciones de botones reducidas al mínimo

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI P · Estilo de UI/UX

La plataforma deberá tener estilo denominado como Glassmorfismo.

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## RI Q · Representación de métricas

Los resultados deberan visualizarse con los datos de coincidencia mediante gráficos y explicación en texto.

**Relacionado:** [[tesis/implementacion#Sistema visual e interfaz|Sistema visual e interfaz]]

## Enlaces

- [[tesis/requisitos-funcionales|Requisitos Funcionales]]
- [[tesis/requisitos-no-funcionales|Requisitos No Funcionales]]
- [[tesis/requisitos-implementacion|Requisitos de Implementación]]
- [[index-tesis|Volver al índice de tesis]]
