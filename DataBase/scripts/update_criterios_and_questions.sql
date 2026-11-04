
BEGIN;

--PREGUNTAS ABIERTAS RIASEC
UPDATE pregunta_cuestionario
SET pregunta_abierta = '¿Qué te motiva de realizar actividades prácticas o técnicas y en qué tipo de tareas disfrutas trabajar con herramientas, equipos o materiales?'
WHERE riasec_id = 1;

UPDATE pregunta_cuestionario
SET pregunta_abierta = '¿Qué temas o problemas te encuentras teniendo curiosidad y que te gustaría investigar, estudiar y comprender para poder explicar algo?'
WHERE riasec_id = 2;

UPDATE pregunta_cuestionario
SET pregunta_abierta = '¿Cómo deseas ayudar, guiar, educar o monitorear a otras personas en distintas situaciones?'
WHERE riasec_id = 4;

UPDATE pregunta_cuestionario
SET pregunta_abierta = 'Si tuvieras la oportunidad de liderar un proyecto, ¿cómo organizarías y motivarías al equipo para alcanzar los objetivos?'
WHERE riasec_id = 5;

UPDATE pregunta_cuestionario
SET pregunta_abierta = '¿Cómo sueles organizar tus actividades o datos y qué métodos o sistemas te ayudan a que todo funcione de manera clara y eficiente?'
WHERE riasec_id = 6;


--CORRECCION DE CRITERIOS 

UPDATE criterios
SET desc_criterio = 'Registrar y controlar procedimientos normativos para el cumplimiento de planes de política ambiental',
    resumen_criterio = 'Control de procedimientos normativos ambientales'
WHERE criterio_id = 119;


UPDATE criterios
SET desc_criterio = 'Clasificar y organizar registros de datos conforme a protocolos y estándares telemáticos',
    resumen_criterio = 'Organización y registro de datos telemáticos'
WHERE criterio_id = 221;


UPDATE criterios
SET desc_criterio = 'Registrar sistemáticamente la historia clínica del paciente conforme a la normativa médica vigente',
    resumen_criterio = 'Registro normativo de historias clínicas'
WHERE criterio_id = 318;


UPDATE criterios
SET desc_criterio = 'Verificar registros y cumplimiento de procedimientos operativos en ventas especializadas',
    resumen_criterio = 'Verificación de procedimientos de ventas'
WHERE criterio_id = 390;


UPDATE criterios
SET desc_criterio = 'Analizar fenómenos complejos mediante el modelado y la investigación matemática rigurosa',
    resumen_criterio = 'Análisis y modelado de fenómenos matemáticos'
WHERE criterio_id = 182;


UPDATE criterios
SET desc_criterio = 'Analizar e investigar la correlación clínica de estudios paraclínicos para el diagnóstico de patologías',
    resumen_criterio = 'Análisis diagnóstico de estudios de laboratorio'
WHERE criterio_id = 321;


UPDATE criterios
SET desc_criterio = 'Investigar el comportamiento de mercados y analizar empíricamente escenarios económicos',
    resumen_criterio = 'Investigación y análisis de mercados económicos'
WHERE criterio_id = 363;


UPDATE criterios
SET desc_criterio = 'Operar instrumentos de medición física y equipos de control técnico en entornos industriales',
    resumen_criterio = 'Operación de instrumentos de medición física'
WHERE criterio_id = 247;


UPDATE criterios
SET desc_criterio = 'Manejar instrumental de laboratorio y equipos biotecnológicos para la obtención de productos biológicos',
    resumen_criterio = 'Manejo de equipo biotecnológico de laboratorio'
WHERE criterio_id = 265;


UPDATE criterios
SET desc_criterio = 'Operar equipos radiológicos odontológicos y manipular instrumental para tomas intraorales',
    resumen_criterio = 'Operación de equipo radiológico intraoral'
WHERE criterio_id = 289;

UPDATE criterios
SET desc_criterio = 'Utilizar herramientas de software técnico y diagramación operativa para reconfigurar procesos empresariales',
    resumen_criterio = 'Uso de herramientas de software operativo empresarial'
WHERE criterio_id = 344;


UPDATE criterios
SET desc_criterio = 'Asesorar a personal sanitario y multidisciplinario en el diseño funcional de unidades de salud',
    resumen_criterio = 'Asesoría en diseño de unidades sanitarias'
WHERE criterio_id = 15;


UPDATE criterios
SET desc_criterio = 'Capacitar y asesorar a profesionales y usuarios en la integración de tecnología biónica',
    resumen_criterio = 'Capacitación y asesoría en tecnología biónica'
WHERE criterio_id = 21;

UPDATE criterios
SET desc_criterio = 'Asesorar técnicamente a grupos de trabajo en aplicaciones y procesos de ingeniería bioquímica',
    resumen_criterio = 'Asesoría técnica en ingeniería bioquímica'
WHERE criterio_id = 27;


UPDATE criterios
SET desc_criterio = 'Capacitar a usuarios y personal técnico en el uso seguro de soluciones biotecnológicas',
    resumen_criterio = 'Capacitación en soluciones biotecnológicas'
WHERE criterio_id = 33;


UPDATE criterios
SET desc_criterio = 'Orientar y capacitar a personal operativo y comunidades sobre el impacto de obras civiles',
    resumen_criterio = 'Orientación y capacitación en obras civiles'
WHERE criterio_id = 39;

UPDATE criterios
SET desc_criterio = 'Asesorar y capacitar a usuarios finales y equipos en la adopción de herramientas informáticas',
    resumen_criterio = 'Asesoría y capacitación a usuarios informáticos'
WHERE criterio_id = 81;

UPDATE criterios
SET desc_criterio = 'Guiar y capacitar a usuarios y equipos de trabajo en el uso ético y efectivo de la inteligencia artificial',
    resumen_criterio = 'Capacitación en uso de inteligencia artificial'
WHERE criterio_id = 87;


UPDATE criterios
SET desc_criterio = 'Orientar y asesorar a tripulaciones de vuelo y personal aeronáutico sobre condiciones meteorológicas',
    resumen_criterio = 'Asesoría meteorológica a tripulaciones aéreas'
WHERE criterio_id = 93;

UPDATE criterios
SET desc_criterio = 'Asesorar y orientar a grupos ciudadanos y operadores en cultura de movilidad urbana sustentable',
    resumen_criterio = 'Asesoría en cultura de movilidad urbana'
WHERE criterio_id = 99;

UPDATE criterios
SET desc_criterio = 'Capacitar a comunidades y organizaciones en prácticas de cuidado ambiental y sustentabilidad',
    resumen_criterio = 'Capacitación comunitaria en cuidado ambiental'
WHERE criterio_id = 117;


UPDATE criterios
SET desc_criterio = 'Asesorar y formar a usuarios y equipos de desarrollo en el manejo de soluciones computacionales',
    resumen_criterio = 'Asesoría y formación en sistemas computacionales'
WHERE criterio_id = 129;


UPDATE criterios
SET desc_criterio = 'Capacitar a personal técnico en buenas prácticas de manufactura y seguridad farmacéutica',
    resumen_criterio = 'Capacitación en seguridad farmacéutica'
WHERE criterio_id = 147;


UPDATE criterios
SET desc_criterio = 'Capacitar y asesorar al personal operativo en protocolos de seguridad y servicio ferroviario',
    resumen_criterio = 'Capacitación en protocolos de servicio ferroviario'
WHERE criterio_id = 153;


UPDATE criterios
SET desc_criterio = 'Asesorar a especialistas y técnicos en la aplicación de tecnologías ópticas y fotónicas',
    resumen_criterio = 'Asesoría en aplicaciones de tecnología fotónica'
WHERE criterio_id = 159;


UPDATE criterios
SET desc_criterio = 'Orientar y capacitar a brigadas de campo y personal técnico en métodos geofísicos',
    resumen_criterio = 'Capacitación en métodos de exploración geofísica'
WHERE criterio_id = 165;


UPDATE criterios
SET desc_criterio = 'Capacitar a personal laboral en metodologías de productividad, seguridad y ergonomía',
    resumen_criterio = 'Capacitación laboral en productividad y ergonomía'
WHERE criterio_id = 177;


UPDATE criterios
SET desc_criterio = 'Capacitar al personal de campo en medidas de seguridad y operación en plantas petroleras',
    resumen_criterio = 'Capacitación operativa en plantas petroleras'
WHERE criterio_id = 213;


UPDATE criterios
SET desc_criterio = 'Asesorar a directivos y usuarios no técnicos en la interpretación y uso de modelos de datos',
    resumen_criterio = 'Asesoría en interpretación de modelos de datos'
WHERE criterio_id = 237;


UPDATE criterios
SET desc_criterio = 'Asesorar a clientes y organizaciones en la resolución de problemas informáticos',
    resumen_criterio = 'Asesoría informática a organizaciones'
WHERE criterio_id = 243;


UPDATE criterios
SET desc_criterio = 'Asesorar a equipos técnicos en la lógica y aplicación práctica de soluciones algorítmicas',
    resumen_criterio = 'Asesoría técnica en diseño algorítmico'
WHERE criterio_id = 255;

UPDATE criterios
SET desc_criterio = 'Orientar a la población y personal sanitario en prevención de riesgos microbiológicos',
    resumen_criterio = 'Orientación en prevención microbiológica y salud'
WHERE criterio_id = 261;

UPDATE criterios
SET desc_criterio = 'Orientar y educar a los pacientes en salud visual, uso de lentes y hábitos preventivos',
    resumen_criterio = 'Educación y orientación en salud visual'
WHERE criterio_id = 298;

UPDATE criterios
SET desc_criterio = 'Asesorar a profesionales de la salud en el uso racional y seguridad de medicamentos',
    resumen_criterio = 'Asesoría en uso racional de medicamentos'
WHERE criterio_id = 328;

UPDATE criterios
SET desc_criterio = 'Capacitar al personal organizacional en desarrollo humano, trabajo en equipo y clima laboral',
    resumen_criterio = 'Capacitación organizacional en trabajo en equipo'
WHERE criterio_id = 334;

UPDATE criterios
SET desc_criterio = 'Asesorar a clientes y contribuyentes en materia contable, tributaria y financiera',
    resumen_criterio = 'Asesoría contable y tributaria a clientes'
WHERE criterio_id = 340;

UPDATE criterios
SET desc_criterio = 'Orientar y capacitar a usuarios e investigadores en habilidades informacionales y búsqueda bibliográfica',
    resumen_criterio = 'Orientación a usuarios en búsqueda bibliográfica'
WHERE criterio_id = 358;

UPDATE criterios
SET desc_criterio = 'Asesorar y educar a grupos sociales en finanzas personales y programas económicos comunitarios',
    resumen_criterio = 'Asesoría y educación en finanzas comunitarias'
WHERE criterio_id = 364;

UPDATE criterios
SET desc_criterio = 'Asesorar a clientes y emprendedores en estrategias de posicionamiento digital y servicio al consumidor',
    resumen_criterio = 'Asesoría a clientes en marketing digital'
WHERE criterio_id = 370;

UPDATE criterios
SET desc_criterio = 'Asesorar a usuarios y empresas en la adopción de modelos comerciales y plataformas digitales',
    resumen_criterio = 'Asesoría a empresas en negocios digitales'
WHERE criterio_id = 376;

UPDATE criterios
SET desc_criterio = 'Asesorar y orientar a clientes y socios comerciales en la satisfacción de necesidades de mercado',
    resumen_criterio = 'Asesoría comercial y atención a clientes'
WHERE criterio_id = 388;

COMMIT;
