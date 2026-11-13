"""
Taller: Caché de Fibonacci con Redis
====================================

Reparto de funciones (cada persona edita SOLO sus funciones):
- Arias     : parte1_conexion, fib, parte2_sin_cache, fib_cache, parte3_secuencia
- López     : contar, parte4_contadores, registrar_historial, parte5_historial, parte7_expiracion
- Villaneda : registrar_set, parte6_set, fib_memo, bonus_memoizacion, parte8a_inventario_claves
- Daza      : parte8b_inventario_stats

Requisitos: Redis en localhost:6379, sin contraseña, base de datos 1.
Ejecutar:   python taller_fib.py
"""

import time

import redis

# ---------------------------------------------------------------------------
# Conexión y variables compartidas (no cambiar sin avisar al grupo)
# ---------------------------------------------------------------------------
r = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)

TTL_SEGUNDOS = 30                      # TTL de las claves fib:<n>
TIEMPOS_MISS = {}                      # n -> ms que tardó el MISS de fib_cache(n)
LOG_PARTE3 = []                        # lista de dicts: {n, resultado, estado, ms, ttl}
SECUENCIA = [30, 30, 25, 30, 25, 32, 32]

# Nombres de claves usados por todo el grupo
CLAVE_HITS = "stats:hits"
CLAVE_MISSES = "stats:misses"
CLAVE_HISTORIAL = "historial"          # lista (López)
CLAVE_CONSULTADOS = "consultados"      # set (Villaneda)


# ===========================================================================
# ARIAS — Partes 1, 2 y 3 (implementadas)
# ===========================================================================
def parte1_conexion():
    """Parte 1: PING, FLUSHDB y DBSIZE sobre la base de datos 1."""
    print("\n=== Parte 1: Conexión (Arias) ===")
    print("PING   ->", r.ping())
    r.flushdb()
    print("FLUSHDB -> base de datos 1 vaciada")
    print("DBSIZE ->", r.dbsize())


def fib(n):
    """Fibonacci recursivo puro, sin caché (a propósito lento)."""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def parte2_sin_cache():
    """Parte 2: mide el tiempo de fib(30), fib(32) y fib(35) sin caché."""
    print("\n=== Parte 2: Fibonacci sin caché (Arias) ===")
    for n in (30, 32, 35):
        t0 = time.perf_counter()
        resultado = fib(n)
        ms = (time.perf_counter() - t0) * 1000
        print(f"fib({n}) = {resultado}  ->  {ms:.2f} ms")


def fib_cache(n):
    """
    Busca fib:<n> en Redis.
    - Si existe: HIT.
    - Si no: calcula con fib(n), guarda con TTL_SEGUNDOS y es MISS.
    Los contadores los incrementa contar() (López), NO esta función.
    Devuelve (resultado, estado, ms, ttl).
    """
    clave = f"fib:{n}"
    t0 = time.perf_counter()
    valor = r.get(clave)
    if valor is not None:
        resultado = int(valor)
        estado = "HIT"
    else:
        resultado = fib(n)
        r.set(clave, resultado, ex=TTL_SEGUNDOS)
        estado = "MISS"
    ms = (time.perf_counter() - t0) * 1000
    ttl = r.ttl(clave)

    contar(estado)            # López
    registrar_historial(n)    # López
    registrar_set(n)          # Villaneda

    if estado == "MISS":
        TIEMPOS_MISS[n] = ms
    LOG_PARTE3.append({"n": n, "resultado": resultado, "estado": estado, "ms": ms, "ttl": ttl})
    return resultado, estado, ms, ttl


def parte3_secuencia():
    """Parte 3: ejecuta fib_cache sobre SECUENCIA y muestra HIT/MISS, tiempo y TTL."""
    print("\n=== Parte 3: Fibonacci con caché y TTL (Arias) ===")
    print(f"{'n':>4} {'resultado':>12} {'estado':>6} {'ms':>10} {'ttl':>5}")
    for n in SECUENCIA:
        resultado, estado, ms, ttl = fib_cache(n)
        print(f"{n:>4} {resultado:>12} {estado:>6} {ms:>10.3f} {ttl:>5}")


# ===========================================================================
# LÓPEZ — Partes 4, 5 y 7 (pendientes)
# ===========================================================================
def contar(estado):
    # TODO LÓPEZ: INCR stats:hits si estado == "HIT", INCR stats:misses si estado == "MISS".
    print("pendiente (López)")


def parte4_contadores():
    # TODO LÓPEZ: GET stats:hits y stats:misses, imprimirlos y calcular
    #             tasa de aciertos = hits / (hits + misses) * 100.
    print("\n=== Parte 4: Contadores (López) ===")
    print("pendiente (López)")


def registrar_historial(n):
    # TODO LÓPEZ: LPUSH historial n (guardar cada consulta en la lista).
    print("pendiente (López)")


def parte5_historial():
    # TODO LÓPEZ: LRANGE historial 0 -1 para mostrar el historial y LLEN historial para su tamaño.
    print("\n=== Parte 5: Historial en lista (López) ===")
    print("pendiente (López)")


def parte7_expiracion():
    # TODO LÓPEZ: EXPIRE sobre una clave fib:<n> con un TTL corto, esperar,
    #             y comprobar con EXISTS que la clave ya expiró.
    print("\n=== Parte 7: Expiración (López) ===")
    print("pendiente (López)")


# ===========================================================================
# VILLANEDA — Parte 6, bonus y parte 8a (pendientes)
# ===========================================================================
def registrar_set(n):
    # TODO VILLANEDA: SADD consultados n (cada n se guarda una sola vez).
    print("pendiente (Villaneda)")


def parte6_set():
    # TODO VILLANEDA: SCARD consultados (cuántos n distintos) y
    #                 SISMEMBER consultados <n> para revisar si un n ya se consultó.
    print("\n=== Parte 6: Set de consultados (Villaneda) ===")
    print("pendiente (Villaneda)")


def fib_memo(n):
    # TODO VILLANEDA: Fibonacci memoizado en Redis guardando cada subresultado
    #                 en memo:<k>. NO modificar fib().
    print("pendiente (Villaneda)")
    return None


def bonus_memoizacion():
    # TODO VILLANEDA: medir fib_memo(90) e imprimir resultado y tiempo.
    print("\n=== Bonus: Memoización (Villaneda) ===")
    print("pendiente (Villaneda)")


def parte8a_inventario_claves():
    # TODO VILLANEDA: DBSIZE; contar claves por prefijo (fib:, memo:, stats:, ...)
    #                 y por tipo (TYPE) recorriendo r.scan_iter(). NUNCA usar KEYS.
    print("\n=== Parte 8a: Inventario de claves (Villaneda) ===")
    print("pendiente (Villaneda)")


# ===========================================================================
# DAZA — Parte 8b (pendiente)
# ===========================================================================
def parte8b_inventario_stats():
    # TODO DAZA: con TTL separar claves con expiración y claves permanentes (TTL = -1);
    #            mostrar valores finales de stats:hits y stats:misses con la tasa de aciertos;
    #            calcular el tiempo ahorrado por el caché usando TIEMPOS_MISS y LOG_PARTE3
    #            (cada HIT de n ahorra aprox. TIEMPOS_MISS[n] - ms del HIT).
    print("\n=== Parte 8b: Inventario de estadísticas (Daza) ===")
    print("pendiente (Daza)")


# ===========================================================================
# Programa principal (Arias integra)
# ===========================================================================
def main():
    parte1_conexion()
    parte2_sin_cache()
    parte3_secuencia()
    parte4_contadores()
    parte5_historial()
    parte6_set()
    parte7_expiracion()
    bonus_memoizacion()
    parte8a_inventario_claves()
    parte8b_inventario_stats()


if __name__ == "__main__":
    main()
