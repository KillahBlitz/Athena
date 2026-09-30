FROM python:3.14-slim

WORKDIR /app

# Dependencias compartidas por todos los microservicios (kinasis-library desde PyPI)
COPY assets/requirements.txt assets/internal_requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r internal_requirements.txt

# Codigo fuente completo
COPY src ./src

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Imagen generica para TODOS los servicios (workers/consumers).
# Cada Deployment selecciona su entrypoint sobrescribiendo "args".
# Ej. classifier -> args: ["src/tasks/classifier_event_handler.py"]
#     extractor  -> args: ["src/tasks/extractor_event_handler.py"]
#     generator  -> args: ["src/tasks/generator_event_handler.py"]
ENTRYPOINT ["python"]
CMD ["src/tasks/classifier_event_handler.py"]
