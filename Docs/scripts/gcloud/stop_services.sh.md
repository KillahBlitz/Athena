# stop_services.sh — política de activación de Cloud SQL

[Índice de documentación](../../index.md) · [Abrir archivo original](../../../Scripts/gcloud/stop_services.sh)

**Archivo documentado:** `Scripts/gcloud/stop_services.sh`  
**Revisión:** 2026-10-19. Descripción basada en el contenido local; no implica una ejecución del archivo.

Contiene un único comando que solicita **desactivar** la instancia de Cloud SQL llamada `athena-db`, cambiando su política de activación a `NEVER`.

```bash
gcloud sql instances patch athena-db --activation-policy=NEVER
```

## Entradas y ejecución

No acepta argumentos ni define variables. Utiliza la instalación de `gcloud`, la identidad autenticada y el proyecto seleccionado en su configuración; el archivo no fija `--project`. Antes de usarlo, comprobar ese proyecto y que la instancia exista allí.

Desde la raíz del repositorio puede invocarse con `bash Scripts/gcloud/stop_services.sh`. No tiene shebang ni lógica adicional, por lo que se documenta la ejecución explícita con `bash`.

## Efectos y alcance

El cambio afecta un recurso remoto y puede afectar la disponibilidad de las conexiones de los notebooks. No crea la instancia, no carga datos, no despliega Backend o Frontend y no configura credenciales. En particular, `upload_services.sh` activa una instancia; su nombre no significa que suba archivos o servicios.

No incluye validación previa, reintentos ni comprobación posterior; la salida y el código de retorno son los del CLI. Esta documentación no ejecutó el comando.

## Archivos relacionados

- [Operación complementaria](upload_services.sh.md)
- [Configuración usada por los notebooks de DB](../python/jupyter/lib/set_envs.py.md)
