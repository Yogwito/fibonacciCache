# Taller: Caché de Fibonacci con Redis

Taller en grupo: Fibonacci recursivo con caché en Redis (TTL, contadores, listas, sets, memoización e inventario de claves).

## Reparto

| Persona   | Código | Informe |
|-----------|--------|---------|
| Arias     | Partes 1-3: conexión, `fib` sin caché, `fib_cache` con TTL. Integra y corre todo, captura la salida. | Arma el PDF final. Preguntas: parte 3 y pregunta 1. |
| López     | Partes 4, 5 y 7: contadores `stats:hits` / `stats:misses` con tasa de aciertos, historial en lista, expiración. | Pregunta 6 y lista vs set. |
| Johan     | Parte 6, bonus y parte 8a: set `consultados`, `fib_memo(90)`, inventario de claves (`DBSIZE`, conteo por prefijo y por tipo con `scan_iter`, nunca `KEYS`). | Bonus, pregunta 5 y la tabla del inventario. |
| Daza      | Parte 8b: claves con TTL y permanentes, valores finales de hits y misses con tasa de aciertos, tiempo ahorrado por el caché. | Los 3 diagramas con su comparación y preguntas 2, 3 y 4. |

## Funciones por responsable (`taller_fib.py`)

| Responsable | Funciones | Estado |
|-------------|-----------|--------|
| Arias       | `parte1_conexion`, `fib`, `parte2_sin_cache`, `fib_cache`, `parte3_secuencia` | Implementadas |
| López       | `contar`, `parte4_contadores`, `registrar_historial`, `parte5_historial`, `parte7_expiracion` | Pendiente (`# TODO LÓPEZ`) |
| Johan       | `registrar_set`, `parte6_set`, `fib_memo`, `bonus_memoizacion`, `parte8a_inventario_claves` | Pendiente (`# TODO JOHAN`) |
| Daza        | `parte8b_inventario_stats` | Pendiente (`# TODO DAZA`) |

Variables compartidas: `TTL_SEGUNDOS = 30`, `TIEMPOS_MISS` (n → ms del MISS), `LOG_PARTE3` (lista de dicts con n, resultado, estado, ms, ttl) y `SECUENCIA = [30, 30, 25, 30, 25, 32, 32]`.

`fib_cache` no hace `INCR` directamente: llama a `contar(estado)`, `registrar_historial(n)` y `registrar_set(n)`.

## Requisitos

- Python 3.12
- Entorno conda `redis-taller`
- Redis corriendo en `localhost:6379`, sin contraseña, base de datos `1`

## Cómo correr

```bash
conda activate redis-taller
pip install -r requirements.txt
python taller_fib.py
```

El notebook `taller_fib.ipynb` importa las funciones de `taller_fib.py`.

## Flujo de trabajo

- Una rama por persona: `arias/...`, `lopez/...`, `johan/...`, `daza/...` (por ejemplo `lopez/contadores`).
- Cada uno edita **solo sus funciones** en `taller_fib.py` y sus celdas del notebook.
- No cambiar nombres de funciones ni variables compartidas sin avisar al grupo.
- Los stubs imprimen `pendiente (<nombre>)` para que el programa corra completo aunque falten partes.
- Diagramas e informe final van en `docs/` (ver `docs/README.md`).
