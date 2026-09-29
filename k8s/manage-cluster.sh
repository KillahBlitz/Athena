#!/bin/bash
# ═══════════════════════════════════════════════════════════
# Athena - Script de Gestión y Operación del Cluster (k3s)
# Uso: ./manage-cluster.sh [start|stop|restart|update|rollback|status]
# ═══════════════════════════════════════════════════════════

set -e

# Detectar comando kubectl
if command -v kubectl &> /dev/null; then
    KUBECTL="sudo kubectl"
elif command -v k3s &> /dev/null; then
    KUBECTL="sudo k3s kubectl"
else
    echo "[ERROR] No se encontró kubectl ni k3s en el sistema."
    exit 1
fi

ACTION=${1:-status}
TARGET=${2:-all}  # all, redis, postgres

print_banner() {
    echo "============================================================"
    echo "   Athena Cluster Manager - Acción: $ACTION | Objetivo: $TARGET"
    echo "============================================================"
}

show_status() {
    print_banner
    echo "[...] Estado de Pods:"
    $KUBECTL get pods -o wide
    echo ""
    echo "[...] Estado de Servicios y Puertos (NodePorts):"
    $KUBECTL get svc -o wide
    echo ""
    echo "[...] Estado de Volúmenes Persistentes:"
    $KUBECTL get pvc
}

case $ACTION in
    start)
        print_banner
        echo "[...] Iniciando servicios (escalando a 1 réplica)..."
        if [ "$TARGET" == "all" ] || [ "$TARGET" == "redis" ]; then
            $KUBECTL scale deployment/redis --replicas=1
            echo "[OK] Deployment redis escalado a 1"
        fi
        if [ "$TARGET" == "all" ] || [ "$TARGET" == "postgres" ]; then
            $KUBECTL scale deployment/postgres --replicas=1
            echo "[OK] Deployment postgres escalado a 1"
        fi
        echo ""
        echo "[...] Esperando disponibilidad de pods..."
        [ "$TARGET" == "all" ] || [ "$TARGET" == "redis" ] && $KUBECTL rollout status deployment/redis --timeout=60s
        [ "$TARGET" == "all" ] || [ "$TARGET" == "postgres" ] && $KUBECTL rollout status deployment/postgres --timeout=60s
        echo "[OK] Servicios iniciados correctamente."
        ;;

    stop)
        print_banner
        echo "[...] Pausando servicios (escalando a 0 réplicas)..."
        echo "[NOTA] Los datos persistentes (PVC) y configuraciones (Secrets) permanecen intactos."
        if [ "$TARGET" == "all" ] || [ "$TARGET" == "redis" ]; then
            $KUBECTL scale deployment/redis --replicas=0
            echo "[OK] Deployment redis pausado."
        fi
        if [ "$TARGET" == "all" ] || [ "$TARGET" == "postgres" ]; then
            $KUBECTL scale deployment/postgres --replicas=0
            echo "[OK] Deployment postgres pausado."
        fi
        echo "[OK] Servicios detenidos. Recursos de CPU y RAM liberados."
        ;;

    restart)
        print_banner
        echo "[...] Reiniciando despliegues..."
        if [ "$TARGET" == "all" ] || [ "$TARGET" == "redis" ]; then
            $KUBECTL rollout restart deployment/redis
            $KUBECTL rollout status deployment/redis --timeout=60s
        fi
        if [ "$TARGET" == "all" ] || [ "$TARGET" == "postgres" ]; then
            $KUBECTL rollout restart deployment/postgres
            $KUBECTL rollout status deployment/postgres --timeout=60s
        fi
        echo "[OK] Reinicio completado exitosamente."
        ;;

    update)
        print_banner
        echo "[...] Ejecutando actualización progresiva (RollingUpdate)..."
        echo "[INFO] Kubernetes levantará el pod nuevo y mantendrá el servicio activo antes de retirar el anterior."
        if [ "$TARGET" == "all" ] || [ "$TARGET" == "redis" ]; then
            echo "[...] Actualizando Redis..."
            $KUBECTL rollout restart deployment/redis
            $KUBECTL rollout status deployment/redis --timeout=120s
        fi
        if [ "$TARGET" == "all" ] || [ "$TARGET" == "postgres" ]; then
            echo "[...] Actualizando PostgreSQL..."
            $KUBECTL rollout restart deployment/postgres
            $KUBECTL rollout status deployment/postgres --timeout=120s
        fi
        echo "[OK] Actualización progresiva completada sin pérdida de servicio."
        ;;

    rollback)
        print_banner
        echo "[...] ¡Revirtiendo actualización al estado anterior (Rollback)!"
        if [ "$TARGET" == "all" ] || [ "$TARGET" == "redis" ]; then
            echo "[...] Deshaciendo último cambio en Redis..."
            $KUBECTL rollout undo deployment/redis
            $KUBECTL rollout status deployment/redis --timeout=60s
        fi
        if [ "$TARGET" == "all" ] || [ "$TARGET" == "postgres" ]; then
            echo "[...] Deshaciendo último cambio en PostgreSQL..."
            $KUBECTL rollout undo deployment/postgres
            $KUBECTL rollout status deployment/postgres --timeout=60s
        fi
        echo "[OK] Rollback completado a la versión funcional previa."
        ;;

    history)
        print_banner
        echo "[...] Historial de despliegues y revisiones:"
        if [ "$TARGET" == "all" ] || [ "$TARGET" == "redis" ]; then
            echo "--- Historial Redis ---"
            $KUBECTL rollout history deployment/redis
        fi
        if [ "$TARGET" == "all" ] || [ "$TARGET" == "postgres" ]; then
            echo "--- Historial PostgreSQL ---"
            $KUBECTL rollout history deployment/postgres
        fi
        ;;

    status)
        show_status
        ;;

    *)
        echo "Uso: $0 {start|stop|restart|update|rollback|history|status} [all|redis|postgres]"
        echo ""
        echo "Ejemplos:"
        echo "  $0 start              # Iniciar todos los servicios"
        echo "  $0 stop               # Pausar todos los servicios (0 réplicas)"
        echo "  $0 stop redis         # Pausar únicamente Redis"
        echo "  $0 update             # Aplicar actualización progresiva (RollingUpdate)"
        echo "  $0 rollback           # Revertir a la versión previa si hay fallos"
        echo "  $0 history            # Ver historial de despliegues"
        echo "  $0 status             # Ver estado actual de pods y puertos"
        exit 1
        ;;
esac
