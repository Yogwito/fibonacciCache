"""
Taller: Caché de Fibonacci con Redis
====================================

Reparto de funciones (cada persona edita SOLO sus funciones):
- Arias     : parte1_conexion, fib, parte2_sin_cache, fib_cache, parte3_secuencia, pregunta1_hit_vs_miss
- López     : contar, parte4_contadores, registrar_historial, parte5_historial, parte7_expiracion
- Johan     : registrar_set, parte6_set, fib_memo, bonus_memoizacion, parte8a_inventario_claves
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
CLAVE_CONSULTADOS = "consultados"      # set (Johan)


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
    registrar_set(n)          # Johan

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


def pregunta1_hit_vs_miss():
    """Pregunta 1: cuántas veces más rápido fue un HIT comparado con un MISS."""
    print("\n=== Pregunta 1: HIT vs MISS (Arias) ===")

    # sumo los tiempos de los HIT y de los MISS de la parte 3
    suma_hit = 0
    cantidad_hit = 0
    suma_miss = 0
    cantidad_miss = 0
    for consulta in LOG_PARTE3:
        if consulta["estado"] == "HIT":
            suma_hit = suma_hit + consulta["ms"]
            cantidad_hit = cantidad_hit + 1
        else:
            suma_miss = suma_miss + consulta["ms"]
            cantidad_miss = cantidad_miss + 1

    # si no hubo HIT o MISS no se puede comparar
    if cantidad_hit == 0 or cantidad_miss == 0:
        print("No hay HIT y MISS para comparar")
        return

    promedio_hit = suma_hit / cantidad_hit
    promedio_miss = suma_miss / cantidad_miss
    veces = promedio_miss / promedio_hit

    print("Promedio de un MISS:", round(promedio_miss, 3), "ms")
    print("Promedio de un HIT:", round(promedio_hit, 3), "ms")
    print("Un HIT fue", round(veces), "veces más rápido que un MISS")


# ===========================================================================
# LÓPEZ — Partes 4, 5 y 7 (pendientes)
# ===========================================================================
def contar(estado):
    if estado == "HIT":#esta bien la consulta
        r.incr(CLAVE_HITS)
    elif estado == "MISS":#esta mal la consulta
        r.incr(CLAVE_MISSES)

def parte4_contadores():
    print("\n=== Parte 4 lop ===")
    hits = int(r.get(CLAVE_HITS))
    misses = int(r.get(CLAVE_MISSES))
    tasa = hits / (hits + misses) * 100 #aciertos entre el total de consultas en porcentaje
    print("Hits:", hits)
    print("Misses:", misses)
    print(f"Tasa de aciertos: {tasa:.2f}%")

def registrar_historial(n):
    r.lpush(CLAVE_HISTORIAL, n)#se mete n al inicio de la lista historial (la más reciente primero)

def parte5_historial():
    print("\n=== Parte 5 lop ===")
    ultimas = r.lrange(CLAVE_HISTORIAL, 0, 4) #el taller dice que devuelve las 5 consultas mas recientes
    total = r.llen(CLAVE_HISTORIAL) #el total de consultas realizadas
    print("Últimas 5 consultas:", ultimas)
    print("Total de consultas:", total)


def parte7_expiracion():
    print("\n=== Parte 7 lop ===")
    r.expire("fib:30", 1) #cambiamos el TTL de fib:30 a 1 segundo
    print("EXPIRE fib:30 a 1 segundo")
    time.sleep(2)
    print("EXISTS fib:30 ->", r.exists("fib:30"))# devuelve 1 si existe y 0 si no.
    resultado, estado, ms, ttl = fib_cache(30) 
    print(f"fib_cache(30) -> {resultado} {estado} {ms:.3f} ms")#muestra si fue hit o miss junto al tiempo


# ===========================================================================
# JOHAN — Parte 6, bonus y parte 8a
# ===========================================================================
def registrar_set(n):
    # guarda cada n en el set consultados
    r.sadd(CLAVE_CONSULTADOS, n)


def parte6_set():
    print("\n=== Parte 6: Set de consultados (Johan) ===")
    distintos = r.scard(CLAVE_CONSULTADOS)  # cantidad de unicos
    esta_30 = r.sismember(CLAVE_CONSULTADOS, 30)  # revisa si esta el 30
    esta_10 = r.sismember(CLAVE_CONSULTADOS, 10)  # revisa si esta el 10
    print("Números distintos:", distintos)
    print("¿El 30 fue consultado?:", bool(esta_30))
    print("¿El 10 fue consultado?:", bool(esta_10))


def fib_memo(n):
    # caso base
    if n < 2:
        return n
    clave = f"memo:{n}"
    # revisa si ya esta en redis
    valor = r.get(clave)
    if valor is not None:
        return int(valor)
    # calcula recursivo y guarda en redis
    resultado = fib_memo(n - 1) + fib_memo(n - 2)
    r.set(clave, resultado)
    return resultado


def bonus_memoizacion():
    print("\n=== Bonus: Memoización (Johan) ===")
    t0 = time.perf_counter()
    res = fib_memo(90)  # calcula fib de 90
    ms = (time.perf_counter() - t0) * 1000
    print(f"fib_memo(90) = {res}  ->  {ms:.2f} ms")


def parte8a_inventario_claves():
    print("\n=== Parte 8a: Inventario de claves (Johan) ===")
    total = r.dbsize()  # total de claves
    print("Total de claves (DBSIZE):", total)

    prefijos = {"fib:*": 0, "memo:*": 0, "stats:*": 0, "sin prefijo": 0}
    tipos = {"string": 0, "list": 0, "set": 0}

    # usa scan_iter para no usar keys
    for clave in r.scan_iter():
        # conteo por prefijo
        if clave.startswith("fib:"):
            prefijos["fib:*"] += 1
        elif clave.startswith("memo:"):
            prefijos["memo:*"] += 1
        elif clave.startswith("stats:"):
            prefijos["stats:*"] += 1
        else:
            prefijos["sin prefijo"] += 1

        # conteo por tipo
        tipo = r.type(clave)
        if tipo in tipos:
            tipos[tipo] += 1
        else:
            tipos[tipo] = 1

    print("\nClaves por prefijo:")
    for p, cant in prefijos.items():
        print(f"  {p}: {cant}")

    print("\nClaves por tipo:")
    for t, cant in tipos.items():
        print(f"  {t}: {cant}")


# ===========================================================================
# DAZA — Parte 8b (pendiente)
# ===========================================================================
def parte8b_inventario_stats():
    print("\n=== Parte 8b: Inventario de estadísticas (Daza) ===")
    print()

    total_permanentes = 0

    for clave in r.scan_iter():

        tiempo = r.ttl(clave)

        if tiempo == -1:
            total_permanentes += 1

        elif tiempo >= 0:
            print(f"{clave} tiene expiracion y le quedan {tiempo}s")

    print()
    print(f"Total de claves permanentes: {total_permanentes}")

    hits = int(r.get("stats:hits"))
    misses = int(r.get("stats:misses"))

    porcentaje = hits/(hits+misses) * 100
    print()
    print(f"Hits: {r.get("stats:hits")}")
    print(f"Misses: {r.get("stats:misses")}")
    print(f"Tasa de aciertos: {porcentaje}%")
    print()

    print("Tiempo ahorrado")

    tiempo_ahorrado = 0

    for i in range(len(LOG_PARTE3)):
        if LOG_PARTE3[i]["estado"]=="HIT":
            n = LOG_PARTE3[i]["n"]
            inicio=time.perf_counter()
            fib(n)
            tiempo_calculo =(time.perf_counter()-inicio) * 1000

            tiempo_hit=LOG_PARTE3[i]["ms"]

            ahorro =tiempo_calculo-tiempo_hit
            tiempo_ahorrado += ahorro

            print(f"N: {n}")
            print(f"tiempo normal: {tiempo_calculo}ms")
            print(f"tiempo del hit: {tiempo_hit}ms")
            print(f"tiempo ahorrado: {ahorro}ms")

    print(f"tiempo ahorrado en total: {tiempo_ahorrado}ms")
  


    


# ===========================================================================
# Programa principal (Arias integra)
# ===========================================================================
def main():
    parte1_conexion()
    parte2_sin_cache()
    parte3_secuencia()
    pregunta1_hit_vs_miss()
    parte4_contadores()
    parte5_historial()
    parte6_set()
    parte7_expiracion()
    bonus_memoizacion()
    parte8a_inventario_claves()
    parte8b_inventario_stats()


if __name__ == "__main__":
    main()
