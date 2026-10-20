import type { BackendAreaDTO, BackendQuestionaryResponseDTO } from '../../../types/area'

export const OFFICIAL_AREAS_FALLBACK: BackendAreaDTO[] = [
  { area_id: 1, nom_area: 'Ciencias Físico Matemáticas' },
  { area_id: 2, nom_area: 'Ciencias Médico Biológicas' },
  { area_id: 3, nom_area: 'Ciencias Sociales y Administrativas' }
]

export const OFFICIAL_QUESTIONARY_FALLBACK: Record<number, BackendQuestionaryResponseDTO> = {
  1: {
    area_id: 1,
    nom_area: 'Ingeniería y Ciencias Físico Matemáticas',
    objetivos: {
      "1": "¿Te interesa diseñar, operar y mantener sistemas aeronáuticos, además de administrar recursos para su funcionamiento?",
      "2": "¿Te interesa diseñar soluciones para prevenir o reducir la contaminación y gestionar de manera sustentable los recursos naturales?",
      "3": "¿Te interesa combinar tecnología, ingeniería y ciencias de la salud para mejorar equipos o procesos de atención médica?",
      "4": "¿Te interesa diseñar dispositivos tecnológicos que imiten funciones o características de los seres vivos?",
      "5": "¿Te interesa aplicar procesos biológicos y químicos para desarrollar soluciones en alimentos, ambiente o producción sustentable?",
      "6": "¿Te interesa utilizar la biotecnología para desarrollar soluciones que atiendan necesidades sociales o productivas?",
      "7": "¿Te interesa planear y desarrollar obras de infraestructura considerando su funcionamiento, administración y impacto sustentable?",
      "8": "¿Te interesa diseñar y administrar sistemas eléctricos y participar en su instalación, operación y mantenimiento?",
      "9": "¿Te interesa desarrollar o mejorar alimentos y procesos de producción utilizando conocimientos científicos y tecnológicos?",
      "10": "¿Te interesa diseñar y evaluar soluciones computacionales para resolver problemas tecnológicos y participar en proyectos?",
      "11": "¿Te interesa diseñar y evaluar dispositivos o sistemas electrónicos y de comunicación para resolver problemas tecnológicos?",
      "12": "¿Te interesa diseñar y mejorar sistemas de control y automatización para hacer más eficientes los procesos?",
      "13": "¿Te interesa desarrollar tecnologías para aprovechar la energía de manera eficiente y con menor impacto ambiental?",
      "14": "¿Te interesa desarrollar y dirigir proyectos informáticos que resuelvan necesidades de organizaciones y considerar sus efectos sociales y éticos?",
      "15": "¿Te interesa desarrollar sistemas inteligentes mediante algoritmos y técnicas de inteligencia artificial para resolver problemas?",
      "16": "¿Te interesa analizar fenómenos atmosféricos y elaborar pronósticos para apoyar la prevención de riesgos y atender problemas climáticos?",
      "17": "¿Te interesa analizar y mejorar sistemas de movilidad urbana considerando aspectos sociales, ambientales, económicos y tecnológicos?",
      "18": "¿Te interesa analizar el sector energético y desarrollar soluciones o modelos de negocio que sean técnica y económicamente viables y sustentables?",
      "19": "¿Te interesa diseñar y poner en funcionamiento sistemas robóticos o automatizados para procesos industriales?",
      "20": "¿Te interesa analizar problemas ambientales y proponer sistemas para prevenir, reducir o controlar la contaminación?",
      "21": "¿Te interesa desarrollar soluciones y trabajar con los distintos sistemas que integran los vehículos automotrices?",
      "22": "¿Te interesa diseñar, desarrollar e implementar sistemas computacionales utilizando tecnologías y estándares de calidad?",
      "23": "¿Te interesa diseñar y optimizar sistemas energéticos y redes inteligentes mediante tecnologías de monitoreo y control?",
      "24": "¿Te interesa analizar y mejorar sistemas de transporte considerando factores sociales, ambientales, económicos y tecnológicos?",
      "25": "¿Te interesa aplicar conocimientos científicos para desarrollar productos, procesos o tecnología en la industria farmacéutica?",
      "26": "¿Te interesa diseñar y gestionar sistemas ferroviarios buscando que sean seguros, eficientes y sustentables?",
      "27": "¿Te interesa combinar óptica, electrónica y computación para desarrollar productos o servicios tecnológicos?",
      "28": "¿Te interesa analizar datos geofísicos para estudiar el subsuelo, evaluar recursos naturales o identificar riesgos?",
      "29": "¿Te interesa estudiar la Tierra para explorar recursos naturales, evaluar su aprovechamiento o analizar riesgos geológicos?",
      "30": "¿Te interesa analizar y mejorar procesos y sistemas para aumentar la productividad, calidad y eficiencia de una organización?",
      "31": "¿Te interesa utilizar modelos matemáticos para resolver problemas y predecir posibles escenarios en organizaciones o procesos?",
      "32": "¿Te interesa diseñar, fabricar y mejorar máquinas o sistemas mecánicos para aumentar su eficiencia y calidad?",
      "33": "¿Te interesa diseñar, programar y controlar sistemas que integren mecánica, electrónica y tecnología?",
      "34": "¿Te interesa trabajar en la exploración y explotación de recursos energéticos y optimizar los procesos relacionados con ellos?",
      "35": "¿Te interesa desarrollar procesos químicos y tecnologías que mejoren la producción industrial de manera sustentable?",
      "36": "¿Te interesa participar en procesos de transformación y manejo de petróleo y gas considerando aspectos técnicos, económicos y ambientales?",
      "37": "¿Te interesa diseñar y administrar sistemas de comunicación para procesar, almacenar y transmitir datos, voz o video?",
      "38": "¿Te interesa diseñar y mejorar procesos de producción de la industria textil considerando calidad, mercado y sustentabilidad?",
      "39": "¿Te interesa obtener y analizar datos del territorio mediante herramientas topográficas y geodésicas para desarrollar proyectos?",
      "40": "¿Te interesa analizar grandes cantidades de datos para obtener información útil y apoyar la toma de decisiones?",
      "41": "¿Te interesa utilizar tecnologías de información y análisis de datos para resolver necesidades estratégicas de las organizaciones?",
      "42": "¿Te interesa estudiar y utilizar las matemáticas y la física para comprender fenómenos y resolver problemas científicos?",
      "43": "¿Te interesa analizar problemas complejos y diseñar soluciones mediante algoritmos y razonamiento matemático?"
    },
    preguntas: []
  },
  2: {
    area_id: 2,
    nom_area: 'Ciencias Médico Biológicas',
    objetivos: {
      "44": "¿Te interesa investigar y aplicar conocimientos de química y biología para resolver problemas biomédicos, ecológicos o biotecnológicos?",
      "45": "¿Te interesa estudiar los seres vivos y aplicar conocimientos biológicos para resolver problemas ambientales o relacionados con recursos naturales?",
      "46": "¿Te interesa cuidar y promover la salud de las personas mediante atención integral y trabajo colaborativo con otros profesionales?",
      "47": "¿Te interesa brindar atención de enfermería y participar en el cuidado de la salud materna y obstétrica?",
      "48": "¿Te interesa analizar problemas relacionados con la alimentación y proponer alternativas para mejorar la nutrición de las personas?",
      "49": "¿Te interesa prevenir, diagnosticar y atender problemas de salud bucodental mediante una atención integral?",
      "50": "¿Te interesa evaluar y cuidar la salud visual y ocular para contribuir a la calidad de vida de las personas?",
      "51": "¿Te interesa evaluar el funcionamiento psicológico, promover el bienestar y comprender el comportamiento humano mediante la investigación?",
      "52": "¿Te interesa investigar problemáticas sociales y diseñar intervenciones para apoyar a personas, familias, grupos o comunidades?",
      "53": "¿Te interesa prevenir y atender problemas de salud y participar en investigación dentro del campo médico?",
      "54": "¿Te interesa diagnosticar y atender problemas de salud y asumir responsabilidades de servicio y liderazgo en el ámbito médico?",
      "55": "¿Te interesa trabajar en la industria farmacéutica, la atención a la salud o la investigación de medicamentos y productos farmacéuticos?"
    },
    preguntas: []
  },
  3: {
    area_id: 3,
    nom_area: 'Ciencias Sociales y Administrativas',
    objetivos: {
      "56": "¿Te interesa gestionar organizaciones y procesos utilizando herramientas administrativas y tecnológicas para contribuir a su desarrollo?",
      "57": "¿Te interesa analizar y gestionar información financiera, fiscal y contable para apoyar la toma de decisiones de una organización?",
      "58": "¿Te interesa dirigir y desarrollar empresas mediante liderazgo y una visión integral de las organizaciones?",
      "59": "¿Te interesa organizar y gestionar información documental y dirigir servicios archivísticos?",
      "60": "¿Te interesa organizar y dirigir servicios de información para atender las necesidades de los usuarios?",
      "61": "¿Te interesa analizar problemas económicos e investigar alternativas que puedan contribuir al desarrollo de la sociedad?",
      "62": "¿Te interesa diseñar estrategias de marketing digital utilizando plataformas tecnológicas para mejorar la competitividad de una organización?",
      "63": "¿Te interesa crear y dirigir negocios digitales utilizando tecnología, análisis de datos e innovación?",
      "64": "¿Te interesa identificar oportunidades en mercados internacionales y diseñar estrategias para desarrollar negocios de importación y exportación?",
      "65": "¿Te interesa administrar procesos comerciales, identificar oportunidades y proponer soluciones para una organización?",
      "66": "¿Te interesa analizar el sector turístico, investigar sus necesidades y proponer soluciones para contribuir a su desarrollo?"
    },
    preguntas: []
  }
}
