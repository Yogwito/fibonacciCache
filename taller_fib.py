import time

import redis

r = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)

TTL_SEGUNDOS = 30
TIEMPOS_MISS = {}
LOG_PARTE3 = []
SECUENCIA = [30, 30, 25, 30, 25, 32, 32]

CLAVE_HITS = "stats:hits"
CLAVE_MISSES = "stats:misses"
CLAVE_HISTORIAL = "historial"
CLAVE_CONSULTADOS = "consultados"


def parte1_conexion():
    print("\n=== Parte 1: Conexión ===")
    print("PING:", r.ping())
    r.flushdb()
    print("FLUSHDB: base de datos 1 vaciada")
    print("DBSIZE:", r.dbsize())


def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def parte2_sin_cache():
    print("\n=== Parte 2: Fibonacci sin caché ===")
    for n in [30, 32, 35]:
        inicio = time.perf_counter()
        resultado = fib(n)
        ms = (time.perf_counter() - inicio) * 1000
        print("fib(" + str(n) + ") =", resultado, "->", round(ms, 2), "ms")


def fib_cache(n):
    clave = "fib:" + str(n)
    inicio = time.perf_counter()
    valor = r.get(clave)
    if valor != None:
        resultado = int(valor)
        estado = "HIT"
    else:
        resultado = fib(n)
        r.set(clave, resultado, ex=TTL_SEGUNDOS)
        estado = "MISS"
    ms = (time.perf_counter() - inicio) * 1000
    ttl = r.ttl(clave)

    contar(estado)
    registrar_historial(n)
    registrar_set(n)

    if estado == "MISS":
        TIEMPOS_MISS[n] = ms
    consulta = {"n": n, "resultado": resultado, "estado": estado, "ms": ms, "ttl": ttl}
    LOG_PARTE3.append(consulta)
    return resultado, estado, ms, ttl


def parte3_secuencia():
    print("\n=== Parte 3: Fibonacci con caché y TTL ===")
    for n in SECUENCIA:
        resultado, estado, ms, ttl = fib_cache(n)
        print("n:", n, "| resultado:", resultado, "|", estado, "|", round(ms, 3), "ms | ttl:", ttl)


def pregunta1_hit_vs_miss():
    print("\n=== Pregunta 1: HIT vs MISS ===")

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

    if cantidad_hit == 0 or cantidad_miss == 0:
        print("No hay HIT y MISS para comparar")
        return

    promedio_hit = suma_hit / cantidad_hit
    promedio_miss = suma_miss / cantidad_miss
    veces = promedio_miss / promedio_hit

    print("Promedio de un MISS:", round(promedio_miss, 3), "ms")
    print("Promedio de un HIT:", round(promedio_hit, 3), "ms")
    print("Un HIT fue", round(veces), "veces más rápido que un MISS")

def contar(estado):
    if estado == "HIT":
        r.incr(CLAVE_HITS)
    elif estado == "MISS":
        r.incr(CLAVE_MISSES)

def parte4_contadores():
    print("\n=== Parte 4: Contadores ===")
    hits = int(r.get(CLAVE_HITS))
    misses = int(r.get(CLAVE_MISSES))
    tasa = hits / (hits + misses) * 100
    print("Hits:", hits)
    print("Misses:", misses)
    print(f"Tasa de aciertos: {tasa:.2f}%")

def registrar_historial(n):
    r.lpush(CLAVE_HISTORIAL, n)

def parte5_historial():
    print("\n=== Parte 5: Historial ===")
    ultimas = r.lrange(CLAVE_HISTORIAL, 0, 4)
    total = r.llen(CLAVE_HISTORIAL)
    print("Últimas 5 consultas:", ultimas)
    print("Total de consultas:", total)


def parte7_expiracion():
    print("\n=== Parte 7: Expiración ===")
    r.expire("fib:30", 1)
    print("EXPIRE fib:30 a 1 segundo")
    time.sleep(2)
    print("EXISTS fib:30 ->", r.exists("fib:30"))
    resultado, estado, ms, ttl = fib_cache(30) 
    print(f"fib_cache(30) -> {resultado} {estado} {ms:.3f} ms")


def registrar_set(n):
    r.sadd(CLAVE_CONSULTADOS, n)


def parte6_set():
    print("\n=== Parte 6: Set de consultados ===")
    distintos = r.scard(CLAVE_CONSULTADOS)
    esta_30 = r.sismember(CLAVE_CONSULTADOS, 30)
    esta_10 = r.sismember(CLAVE_CONSULTADOS, 10)
    print("Números distintos:", distintos)
    print("¿El 30 fue consultado?:", bool(esta_30))
    print("¿El 10 fue consultado?:", bool(esta_10))


def fib_memo(n):
    if n < 2:
        return n
    clave = f"memo:{n}"
    valor = r.get(clave)
    if valor is not None:
        return int(valor)
    resultado = fib_memo(n - 1) + fib_memo(n - 2)
    r.set(clave, resultado)
    return resultado


def bonus_memoizacion():
    print("\n=== Bonus: Memoización ===")
    t0 = time.perf_counter()
    res = fib_memo(90)
    ms = (time.perf_counter() - t0) * 1000
    print(f"fib_memo(90) = {res}  ->  {ms:.2f} ms")


def parte8a_inventario_claves():
    print("\n=== Parte 8a: Inventario de claves ===")
    total = r.dbsize()
    print("Total de claves (DBSIZE):", total)

    prefijos = {"fib:*": 0, "memo:*": 0, "stats:*": 0, "sin prefijo": 0}
    tipos = {"string": 0, "list": 0, "set": 0}

    for clave in r.scan_iter():
        if clave.startswith("fib:"):
            prefijos["fib:*"] += 1
        elif clave.startswith("memo:"):
            prefijos["memo:*"] += 1
        elif clave.startswith("stats:"):
            prefijos["stats:*"] += 1
        else:
            prefijos["sin prefijo"] += 1

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

def parte8b_inventario_stats():
    print("\n=== Parte 8b: Inventario de estadísticas ===")
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
    print(f"Hits: {r.get('stats:hits')}")
    print(f"Misses: {r.get('stats:misses')}")
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
