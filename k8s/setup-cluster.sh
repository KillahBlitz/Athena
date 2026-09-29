#!/bin/bash
# ═══════════════════════════════════════════════════════════
# Athena - Setup k3s cluster con Redis y PostgreSQL
# Ejecutar en el servidor: kinasis-root@100.95.220.1
# ═══════════════════════════════════════════════════════════

set -e

DIR_MANIFESTS="$HOME/athena-k8s"

# Configurar alias/wrapper para kubectl si es necesario
if command -v kubectl &> /dev/null; then
    KUBECTL="sudo kubectl"
elif command -v k3s &> /dev/null; then
    KUBECTL="sudo k3s kubectl"
else
    echo "[...] Instalando k3s..."
    curl -sfL https://get.k3s.io | sh -
    KUBECTL="sudo k3s kubectl"
fi

echo "============================================"
echo "  Verificando estado de k3s"
echo "============================================"

echo "[...] Esperando a que el nodo esté Ready..."
until $KUBECTL get nodes | grep -q " Ready"; do
    sleep 2
done
echo "[OK] Nodo listo:"
$KUBECTL get nodes

echo ""
echo "============================================"
echo "  Creando manifiestos en $DIR_MANIFESTS"
echo "============================================"

mkdir -p "$DIR_MANIFESTS"

# --- Redis Secret ---
cat > "$DIR_MANIFESTS/redis-secret.yaml" << 'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: redis-secret
type: Opaque
data:
  password: a2luYXNpczIwMjU=
EOF

# --- Redis Deployment ---
cat > "$DIR_MANIFESTS/redis-deployment.yaml" << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  labels:
    app: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command: ["redis-server", "--requirepass", "$(REDIS_PASSWORD)"]
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: password
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "250m"
EOF

# --- Redis Service (NodePort) ---
cat > "$DIR_MANIFESTS/redis-service.yaml" << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  labels:
    app: redis
spec:
  type: NodePort
  selector:
    app: redis
  ports:
  - protocol: TCP
    port: 6379
    targetPort: 6379
    nodePort: 30379
EOF

# --- PostgreSQL Secret ---
cat > "$DIR_MANIFESTS/postgres-secret.yaml" << 'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
data:
  POSTGRES_USER: YWRtaW4=
  POSTGRES_PASSWORD: cGFzc3dvcmQ=
  POSTGRES_DB: YXRoZW5h
EOF

# --- PostgreSQL PVC ---
cat > "$DIR_MANIFESTS/postgres-pvc.yaml" << 'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 10Gi
EOF

# --- PostgreSQL Deployment ---
cat > "$DIR_MANIFESTS/postgres-deployment.yaml" << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  labels:
    app: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:17
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_PASSWORD
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_DB
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
          subPath: pgdata
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
EOF

# --- PostgreSQL Service (NodePort) ---
cat > "$DIR_MANIFESTS/postgres-service.yaml" << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  labels:
    app: postgres
spec:
  type: NodePort
  selector:
    app: postgres
  ports:
  - protocol: TCP
    port: 5432
    targetPort: 5432
    nodePort: 30432
EOF

echo "[OK] 7 manifiestos creados en $DIR_MANIFESTS"
ls -la "$DIR_MANIFESTS"

echo ""
echo "============================================"
echo "  Aplicando manifiestos al cluster"
echo "============================================"

$KUBECTL apply -f "$DIR_MANIFESTS/redis-secret.yaml"
$KUBECTL apply -f "$DIR_MANIFESTS/postgres-secret.yaml"
$KUBECTL apply -f "$DIR_MANIFESTS/postgres-pvc.yaml"
$KUBECTL apply -f "$DIR_MANIFESTS/redis-deployment.yaml"
$KUBECTL apply -f "$DIR_MANIFESTS/redis-service.yaml"
$KUBECTL apply -f "$DIR_MANIFESTS/postgres-deployment.yaml"
$KUBECTL apply -f "$DIR_MANIFESTS/postgres-service.yaml"

echo "[OK] Todos los manifiestos aplicados"

echo ""
echo "============================================"
echo "  Esperando a que los pods estén Ready"
echo "============================================"

echo "[...] Esperando pod de Redis..."
$KUBECTL rollout status deployment/redis --timeout=120s
echo "[OK] Redis listo"

echo "[...] Esperando pod de PostgreSQL..."
$KUBECTL rollout status deployment/postgres --timeout=120s
echo "[OK] PostgreSQL listo"

echo ""
$KUBECTL get pods -o wide
echo ""
$KUBECTL get svc -o wide

echo ""
echo "============================================"
echo "  Inicializando tablas de PostgreSQL"
echo "============================================"

PG_POD=$($KUBECTL get pod -l app=postgres -o jsonpath='{.items[0].metadata.name}')
echo "[...] Pod de PostgreSQL: $PG_POD"

# Esperar a que postgres acepte conexiones internamente
echo "[...] Verificando que PostgreSQL responda..."
until $KUBECTL exec "$PG_POD" -- pg_isready -U admin -d athena &> /dev/null; do
    sleep 2
done

# Crear script SQL dentro del pod (BLOQUE 1: CATÁLOGOS, USUARIOS, RELACIONES Y RESULTADOS)
$KUBECTL exec -i "$PG_POD" -- psql -U admin -d athena << 'SQLEOF'
BEGIN;

CREATE TABLE IF NOT EXISTS public.area (
    id_area INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    nombre_area VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.escuela (
    id_escuela INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    nombre_escuela VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.habilidad (
    id_habilidad INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public.carrera (
    id_carrera INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    nombre_carrera VARCHAR(200) NOT NULL,
    id_area INTEGER NOT NULL,
    CONSTRAINT fk_carrera_area
        FOREIGN KEY (id_area) REFERENCES public.area (id_area)
);

CREATE TABLE IF NOT EXISTS public.usuario (
    id_usuario INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid_usuario VARCHAR(50) NOT NULL DEFAULT ('USER-' || gen_random_uuid()::text),
    nombre VARCHAR(60) NOT NULL,
    correo VARCHAR(150) NOT NULL,
    id_area INTEGER,
    CONSTRAINT uq_usuario_uuid UNIQUE (uuid_usuario),
    CONSTRAINT fk_usuario_area
        FOREIGN KEY (id_area) REFERENCES public.area (id_area)
);

CREATE TABLE IF NOT EXISTS public.carrera_escuela (
    id_carrera INTEGER NOT NULL,
    id_escuela INTEGER NOT NULL,
    CONSTRAINT pk_carrera_escuela PRIMARY KEY (id_carrera, id_escuela),
    CONSTRAINT fk_carrera_escuela_carrera
        FOREIGN KEY (id_carrera) REFERENCES public.carrera (id_carrera),
    CONSTRAINT fk_carrera_escuela_escuela
        FOREIGN KEY (id_escuela) REFERENCES public.escuela (id_escuela)
);

CREATE TABLE IF NOT EXISTS public.carrera_habilidad (
    id_carrera INTEGER NOT NULL,
    id_habilidad INTEGER NOT NULL,
    CONSTRAINT pk_carrera_habilidad PRIMARY KEY (id_carrera, id_habilidad),
    CONSTRAINT fk_carrera_habilidad_carrera
        FOREIGN KEY (id_carrera) REFERENCES public.carrera (id_carrera),
    CONSTRAINT fk_carrera_habilidad_habilidad
        FOREIGN KEY (id_habilidad) REFERENCES public.habilidad (id_habilidad)
);

CREATE TABLE IF NOT EXISTS public.usuario_habilidad (
    id_usuario INTEGER NOT NULL,
    id_habilidad INTEGER NOT NULL,
    cumplimiento_criterio FLOAT,
    CONSTRAINT fk_usuario_habilidad_usuario
        FOREIGN KEY (id_usuario) REFERENCES public.usuario (id_usuario),
    CONSTRAINT fk_usuario_habilidad_habilidad
        FOREIGN KEY (id_habilidad) REFERENCES public.habilidad (id_habilidad)
);

CREATE TABLE IF NOT EXISTS public.resultado (
    id_resultado INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid_usuario VARCHAR(50) NOT NULL,
    id_carrera INTEGER NOT NULL,
    porcentaje_coincidencia NUMERIC(5,2) NOT NULL,
    top SMALLINT NOT NULL,
    CONSTRAINT uq_resultado_usuario_carrera UNIQUE (uuid_usuario, id_carrera),
    CONSTRAINT uq_resultado_usuario_top UNIQUE (uuid_usuario, top),
    CONSTRAINT fk_resultado_usuario
        FOREIGN KEY (uuid_usuario) REFERENCES public.usuario (uuid_usuario),
    CONSTRAINT fk_resultado_carrera
        FOREIGN KEY (id_carrera) REFERENCES public.carrera (id_carrera)
);

CREATE TABLE IF NOT EXISTS public.criterio (
    id_criterio INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    nombre_subhabilidad TEXT NOT NULL,
    id_habilidad INTEGER NOT NULL,
    CONSTRAINT fk_criterio_habilidad
        FOREIGN KEY (id_habilidad) REFERENCES public.habilidad (id_habilidad)
);

COMMIT;
SQLEOF

echo "[OK] Tablas creadas"
echo ""
echo "[...] Verificando tablas..."
$KUBECTL exec -i "$PG_POD" -- psql -U admin -d athena -c "\dt public.*"

echo ""
echo "============================================"
echo "  Verificación final de servicios"
echo "============================================"

# Probar Redis Streams
REDIS_POD=$($KUBECTL get pod -l app=redis -o jsonpath='{.items[0].metadata.name}')
echo "[...] Probando Redis Streams en pod: $REDIS_POD..."
$KUBECTL exec -i "$REDIS_POD" -- redis-cli -a kinasis2025 XADD test_stream '*' msg "hola_desde_athena_devel" 2>/dev/null
RESULT=$($KUBECTL exec -i "$REDIS_POD" -- redis-cli -a kinasis2025 XRANGE test_stream - + 2>/dev/null)
echo "    Stream test_stream: $RESULT"
$KUBECTL exec -i "$REDIS_POD" -- redis-cli -a kinasis2025 DEL test_stream 2>/dev/null
echo "[OK] Redis Streams funcionando perfectamente"

# Probar PostgreSQL
echo "[...] Probando PostgreSQL..."
TABLE_COUNT=$($KUBECTL exec -i "$PG_POD" -- psql -U admin -d athena -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'")
echo "[OK] PostgreSQL tiene$TABLE_COUNT tablas creadas y listas"

