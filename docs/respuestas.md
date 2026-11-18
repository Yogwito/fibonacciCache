# Respuestas del taller

Todos los números salen de la misma ejecución, guardada en `salida_programa.txt`.

## Análisis de la parte 3 (HIT, MISS y TTL)

La secuencia es `30, 30, 25, 30, 25, 32, 32`. La base se limpia con `FLUSHDB` en la parte 1, así que al empezar no hay ninguna clave `fib:<n>` guardada.

| Llamada | n  | Estado | Tiempo     | TTL | Por qué |
|---------|----|--------|------------|-----|---------|
| 1       | 30 | MISS   | 45.121 ms  | 30  | `fib:30` no existe, se calcula con `fib(30)` y se guarda con `SET fib:30 ... EX 30` |
| 2       | 30 | HIT    | 0.211 ms   | 30  | `fib:30` ya está guardada, se lee con `GET` sin recalcular |
| 3       | 25 | MISS   | 4.875 ms   | 30  | `fib:25` no existe todavía |
| 4       | 30 | HIT    | 0.167 ms   | 30  | `fib:30` sigue guardada |
| 5       | 25 | HIT    | 0.276 ms   | 30  | `fib:25` ya está guardada |
| 6       | 32 | MISS   | 114.214 ms | 30  | `fib:32` no existe todavía |
| 7       | 32 | HIT    | 0.321 ms   | 30  | `fib:32` ya está guardada |

En total salen **3 MISS** (uno por cada número distinto) y **4 HIT**.

**Tiempo:** un MISS tarda lo mismo que calcular `fib(n)` sin caché, porque llama a la función recursiva de la parte 2. Por eso el MISS de 32 tarda más que el de 30, y el de 30 más que el de 25. Un HIT solo hace un `GET` a Redis, así que tarda menos de un milisegundo sin importar qué tan grande sea `n`.

**TTL:** cada clave se guarda con 30 segundos de vida. Todas las llamadas muestran TTL 30 porque la secuencia completa tarda menos de un segundo y Redis redondea el TTL a segundos enteros. Leer la clave con `GET` **no** reinicia el TTL: la clave expira 30 segundos después de que se creó, aunque se consulte muchas veces.

## Preguntas de las partes

### Parte 6: ¿por qué la lista y el set dan cantidades diferentes?

La lista permite repetir valores porque hace referencia a un historial, y un historial debe registrar cada consulta, aunque se repita, mientras que el set no guarda valores repetidos; por esta razón se dan cantidades diferentes: 7 consultas en la lista frente a 3 números distintos en el set.

### Parte 7: ¿fue HIT o MISS? ¿Por qué?

Fue MISS porque primero cambiamos el TTL de `fib:30` a 1 segundo y luego detuvimos la ejecución 2 segundos con `time.sleep`. Pasado ese tiempo la clave expiró y se borró de Redis, por eso `EXISTS` devolvió 0. Al volver a llamar `fib_cache(30)` no la encontró en el caché, así que tuvo que recalcular el valor y lo guardó otra vez: eso es un MISS.

### Bonus: ¿por qué `fib_memo(90)` es casi instantáneo, si con la versión de la parte 2 `fib(35)` ya tardaba tanto?

En la versión sin caché (`fib`), cada llamada se divide en dos llamadas recursivas sin guardar resultados, recalculando los mismos subproblemas millones de veces con complejidad exponencial O(2^n); por eso `fib(35)` tardó 479.83 ms. En cambio, `fib_memo(90)` guarda cada subproblema `fib(k)` en Redis bajo `memo:<k>`: cada valor se calcula una sola vez y las llamadas repetidas se leen de Redis en tiempo constante, reduciendo la complejidad a lineal O(n). Así `fib_memo(90)` tardó solo 38.20 ms.

## Preguntas para entregar

### 1. ¿Cuántas veces más rápido fue un HIT comparado con un MISS?

Un HIT fue **225 veces más rápido** que un MISS: el MISS tardó en promedio 54.737 ms y el HIT 0.244 ms. La función `pregunta1_hit_vs_miss()` lo calcula con los datos de la parte 3: saca el promedio de los MISS, el promedio de los HIT y los divide. La diferencia es tan grande porque en un MISS se hace todo el cálculo recursivo, que repite los mismos subproblemas una y otra vez (`fib(30)` hace más de un millón de llamadas), mientras que en un HIT solo se lee de Redis el valor que ya estaba guardado en memoria. La diferencia crece mientras más grande sea `n`.

### 2. ¿Qué pasaría con el caché si no usaras TTL?

Sin el TTL las claves no expirarían nunca y por lo tanto se quedarían almacenadas, esto provocaría que se acumulen y ocupen espacio en memoria que luego se tendría que limpiar manualmente si se quiere guardar algo más.

### 3. ¿En qué casos reales usarías un caché con expiración?

En una página web se podrían guardar imágenes u otros elementos, ya que es muy normal cerrar y entrar a una página repetidas veces; el caché ayudaría a que cargue más rápido cuando se vuelve a visitar. También podría ser útil en videojuegos online para guardar información de partidas, como las estadísticas, y que no se tengan que consultar al servidor constantemente.

### 4. ¿Por qué se usó la base de datos 1 y no la 0?

Para separar los datos de este taller de los que creamos en clase, ya que esos se almacenaron en la base de datos 0 y así no se mezclaría la información de ambas.

### 5. Según el inventario de la parte 8, ¿qué estructura ocupa más claves y por qué?

El prefijo que más claves ocupa es **`memo:*`** (tipo `string`), con **89 claves** (`memo:2` hasta `memo:90`) de un total de **96 claves** (`DBSIZE = 96`). Esto pasa porque `fib_memo(90)` crea una clave individual en Redis por cada subproblema intermedio calculado desde `2` hasta `90` (los casos base `0` y `1` retornan directo). En comparación:

- `fib:*` solo guarda una clave por cada número distinto consultado en la secuencia (**3 claves**: `fib:25`, `fib:30`, `fib:32`).
- `stats:*` solo usa **2 claves** (`stats:hits` y `stats:misses`).
- `historial` (`list`) y `consultados` (`set`) agrupan todos sus elementos dentro de **1 sola clave** cada uno.

### 6. Si ejecutas el programa otra vez dentro de los 30 segundos siguientes, ¿cambiaría el inventario? ¿Y si esperas más de 30 segundos sin ejecutar FLUSHDB?

Si ejecutamos el programa otra vez dentro de los 30 segundos, el inventario no cambia: siguen las mismas 96 claves, porque las `fib:*` aún no expiran y todas las consultas serían HIT. Solo cambian los valores (los contadores y el historial siguen aumentando). Si esperamos más de 30 segundos sin ejecutar `FLUSHDB`, las claves `fib:*` expiran y se borran, y el inventario baja de 96 a 93 claves: quedan solo las `memo:*`, `historial`, `consultados`, `stats:hits` y `stats:misses`, que son permanentes. Al consultar de nuevo serían MISS, se recalcularía y las claves `fib:*` se volverían a crear.

## Tabla del inventario de claves (parte 8)

### Por prefijo, tipo y expiración

| Prefijo / clave | Tipo (`TYPE`) | Cantidad | Expiración (`TTL`) |
|---|---|---|---|
| `fib:*` (`fib:25`, `fib:30`, `fib:32`) | `string` | 3 | Con expiración: 28 s, 30 s y 28 s |
| `memo:*` (`memo:2` a `memo:90`) | `string` | 89 | Permanente (`TTL = -1`) |
| `stats:*` (`stats:hits`, `stats:misses`) | `string` | 2 | Permanente (`TTL = -1`) |
| Sin prefijo: `historial` | `list` | 1 | Permanente (`TTL = -1`) |
| Sin prefijo: `consultados` | `set` | 1 | Permanente (`TTL = -1`) |
| **Total (`DBSIZE`)** | | **96** | 3 con expiración / 93 permanentes |

### Por tipo de dato

| Tipo | Cantidad | Claves |
|---|---|---|
| `string` | 94 | `fib:*` (3) + `memo:*` (89) + `stats:*` (2) |
| `list` | 1 | `historial` |
| `set` | 1 | `consultados` |
| **Total** | **96** | |

### Estadísticas finales (incluye la consulta de la parte 7)

| Métrica | Valor | Detalle |
|---|---|---|
| `stats:hits` | 4 | Los 4 HIT de la parte 3 |
| `stats:misses` | 4 | 3 MISS de la parte 3 + 1 MISS de la parte 7 |
| Tasa de aciertos | 50.0 % | `4 / (4 + 4) * 100` |
| Tiempo ahorrado en la parte 3 | 203.23 ms | Lo que habrían tardado los 4 HIT calculando `fib(n)`, menos lo que tardaron realmente: 42.82 + 43.00 + 3.56 + 113.85 ms |
