# Respuestas de Arias

## Análisis de la parte 3 (HIT, MISS y TTL)

La secuencia es `30, 30, 25, 30, 25, 32, 32`. La base se limpia con `FLUSHDB` en la parte 1, así que al empezar no hay ninguna clave `fib:<n>` guardada.

| Llamada | n  | Estado esperado | Por qué |
|---------|----|-----------------|---------|
| 1       | 30 | MISS | `fib:30` no existe, se calcula con `fib(30)` y se guarda con `SET fib:30 ... EX 30` |
| 2       | 30 | HIT  | `fib:30` ya está guardada, se lee con `GET` sin recalcular |
| 3       | 25 | MISS | `fib:25` no existe todavía |
| 4       | 30 | HIT  | `fib:30` sigue guardada |
| 5       | 25 | HIT  | `fib:25` ya está guardada |
| 6       | 32 | MISS | `fib:32` no existe todavía |
| 7       | 32 | HIT  | `fib:32` ya está guardada |

En total salen **3 MISS** (uno por cada número distinto) y **4 HIT**.

**Tiempo:** un MISS tarda lo mismo que calcular `fib(n)` sin caché, porque llama a la función recursiva de la parte 2. Por eso el MISS de 32 tarda más que el de 30, y el de 30 más que el de 25. Un HIT solo hace un `GET` a Redis, así que tarda menos de un milisegundo sin importar qué tan grande sea `n`.

**TTL:** cada clave se guarda con 30 segundos de vida. En nuestra ejecución todas las llamadas muestran TTL 30, porque la secuencia completa tarda menos de un segundo y Redis redondea el TTL a segundos enteros. Si se esperara entre llamadas, en los HIT se vería el TTL bajando (29, 28, ...). Leer la clave con `GET` **no** reinicia el TTL: la clave expira 30 segundos después de que se creó, aunque se consulte muchas veces. Como toda la secuencia termina en menos de 30 segundos, ninguna clave alcanza a expirar durante la parte 3.

## Pregunta 1: ¿Cuántas veces más rápido fue un HIT comparado con un MISS?

La función `pregunta1_hit_vs_miss()` de `taller_fib.py` lo calcula con los datos de la parte 3 (`LOG_PARTE3`):

1. Saca el promedio de tiempo de los MISS.
2. Saca el promedio de tiempo de los HIT.
3. Divide: `veces = promedio_miss / promedio_hit`.

**Resultado medido:** un HIT fue **200 veces** más rápido que un MISS
(promedio MISS: 55.496 ms, promedio HIT: 0.278 ms). Los números cambian un poco en cada ejecución, pero la diferencia siempre es de cientos de veces.

**Por qué la diferencia es tan grande:** en un MISS el programa hace todo el cálculo recursivo, que repite los mismos subproblemas miles de veces (por ejemplo, `fib(30)` hace más de un millón de llamadas). En un HIT no se calcula nada: solo se le pide a Redis el valor que ya estaba guardado en memoria. Por eso un HIT es cientos o miles de veces más rápido, y la diferencia crece mientras más grande sea `n`.

### Salida real de la parte 3

| n  | resultado | estado | ms      | ttl |
|----|-----------|--------|---------|-----|
| 30 | 832040    | MISS   | 45.561  | 30  |
| 30 | 832040    | HIT    | 0.311   | 30  |
| 25 | 75025     | MISS   | 4.591   | 30  |
| 30 | 832040    | HIT    | 0.340   | 30  |
| 25 | 75025     | HIT    | 0.276   | 30  |
| 32 | 2178309   | MISS   | 116.335 | 30  |
| 32 | 2178309   | HIT    | 0.185   | 30  |

La salida completa del programa está en `salida_programa.txt`.
