# Taller: Caché de Fibonacci con Redis

Taller en grupo: Fibonacci recursivo con caché en Redis (TTL, contadores, listas, sets, memoización e inventario de claves).

## Integrantes

Arias, López, Johan y Daza.

## Contenido (`taller_fib.py`)

| Parte | Qué hace | Funciones |
|-------|----------|-----------|
| 1-3 | Conexión, `fib` sin caché y `fib_cache` con TTL | `parte1_conexion`, `fib`, `parte2_sin_cache`, `fib_cache`, `parte3_secuencia`, `pregunta1_hit_vs_miss` |
| 4, 5 y 7 | Contadores de hits y misses, historial en lista, expiración | `contar`, `parte4_contadores`, `registrar_historial`, `parte5_historial`, `parte7_expiracion` |
| 6, bonus y 8a | Set de consultados, `fib_memo(90)`, inventario de claves con `scan_iter` | `registrar_set`, `parte6_set`, `fib_memo`, `bonus_memoizacion`, `parte8a_inventario_claves` |
| 8b | Claves con TTL y permanentes, tasa de aciertos, tiempo ahorrado | `parte8b_inventario_stats` |

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

- Trabajar en ramas aparte y luego integrar en `main`.
- No cambiar nombres de funciones ni variables compartidas sin avisar al grupo.
- Diagramas e informe final van en `docs/` (ver `docs/README.md`).
