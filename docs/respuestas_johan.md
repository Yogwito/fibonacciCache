# Respuestas de Johan

## Bonus (Memoización): ¿Por qué `fib_memo(90)` es casi instantáneo, si con la versión de la parte 2 `fib(35)` ya tardaba tanto?

En la versión sin caché (`fib`), cada llamada se divide en dos llamadas recursivas (`fib(n-1)` y `fib(n-2)`) sin guardar resultados, por lo que recalcula los mismos subproblemas millones de veces y su complejidad es exponencial $O(2^n)$. Por eso `fib(35)` ya tardó **486.76 ms** (según `salida_programa.txt`).

En cambio, `fib_memo(90)` guarda cada subproblema `fib(k)` en Redis bajo la clave `memo:<k>`. La primera vez que se necesita un valor se calcula una sola vez, y cuando otra rama de la recursión vuelve a pedirlo, simplemente lo lee de Redis en tiempo constante $O(1)$ sin volver a abrir la recursión. Así la complejidad baja de exponencial $O(2^n)$ a lineal $O(n)$, logrando calcular `fib_memo(90) = 2880067194370816120` en solo **39.60 ms**.

## Pregunta 5: Según el inventario de la parte 8, ¿qué estructura ocupa más claves y por qué?

El prefijo que más claves ocupa es **`memo:*`** (tipo `string`), con **89 claves** (`memo:2` hasta `memo:90`) de un total de **96 claves** (`DBSIZE = 96`).

Esto pasa porque `fib_memo(90)` crea una clave individual en Redis por cada subproblema intermedio calculado desde `2` hasta `90` (los casos base `0` y `1` retornan directo). En comparación:

- `fib:*` solo guarda una clave por cada número distinto consultado en la secuencia (**3 claves**: `fib:25`, `fib:30`, `fib:32`).
- `stats:*` solo usa **2 claves** (`stats:hits` y `stats:misses`).
- `historial` (`list`) y `consultados` (`set`) agrupan todos sus elementos dentro de **1 sola clave** cada uno.

## Tabla del inventario de claves (Parte 8)

Datos tomados de la ejecución oficial registrada en `salida_programa.txt` (y verificados con la Parte 8b en el notebook):

### Resumen general y desglose por prefijo / tipo

| Categoría            | Elemento / Prefijo                       | Tipo (`TYPE`) | Cantidad | Expiración (`TTL`)         |
| -------------------- | ---------------------------------------- | ------------- | -------- | -------------------------- |
| **Total (`DBSIZE`)** | Todas las claves en DB 1                 | —             | **96**   | 3 con TTL / 93 permanentes |
| **Por prefijo**      | `fib:*` (`fib:25`, `fib:30`, `fib:32`)   | `string`      | **3**    | Con expiración (\~26s–30s) |
| **Por prefijo**      | `memo:*` (`memo:2` a `memo:90`)          | `string`      | **89**   | Permanente (`TTL = -1`)    |
| **Por prefijo**      | `stats:*` (`stats:hits`, `stats:misses`) | `string`      | **2**    | Permanente (`TTL = -1`)    |
| **Por prefijo**      | Sin prefijo (`historial`)                | `list`        | **1**    | Permanente (`TTL = -1`)    |
| **Por prefijo**      | Sin prefijo (`consultados`)              | `set`         | **1**    | Permanente (`TTL = -1`)    |

### Conteo por tipo de dato (`TYPE`)

| Tipo de dato | Cantidad | Claves incluidas                            |
| ------------ | -------- | ------------------------------------------- |
| `string`     | **94**   | `fib:*` (3) + `memo:*` (89) + `stats:*` (2) |
| `list`       | **1**    | `historial`                                 |
| `set`        | **1**    | `consultados`                               |
| **Total**    | **96**   | —                                           |

### Estadísticas finales y tiempo ahorrado (contando Parte 7)

| Métrica                   | Valor         | Detalle                                                                                                                        |
| ------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `stats:hits`              | **4**         | 4 HITs en la Parte 3 (`30`, `30`, `25`, `32`)                                                                                  |
| `stats:misses`            | **4**         | 3 MISSes en la Parte 3 (`30`, `25`, `32`) + 1 MISS en la Parte 7 (`30`)                                                        |
| Tasa de aciertos final    | **50.0%**     | `4 / (4 + 4) * 100`                                                                                                            |
| Tiempo ahorrado (Parte 3) | **205 ms**    | Calculado en la ejecución de la Parte 8b (~205 ms; 210.94 ms usando los MISS de `salida_programa.txt`)                       |
