"""
╔══════════════════════════════════════════════════════════════════╗
║           ALGORITMO ALFA-BETA PRUNING (PODA ALFA-BETA)          ║
║         Implementación con Tres en Raya (Tic-Tac-Toe)           ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os

# ─────────────────────────────────────────────────────────────────
#  COLORES ANSI
# ─────────────────────────────────────────────────────────────────
RESET    = "\033[0m"
ROJO     = "\033[91m"
VERDE    = "\033[92m"
AMARILLO = "\033[93m"
CYAN     = "\033[96m"
MAGENTA  = "\033[95m"
AZUL     = "\033[94m"
GRIS     = "\033[90m"
NEGRITA  = "\033[1m"

# ─────────────────────────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────────────────────────
JUGADOR_X = "X"
JUGADOR_O = "O"
VACIO     = "·"
INF       =  float('inf')
NINF      = -float('inf')

MAX_NODOS_VERBOSE = 120   # Por encima de este estimado → modo silencioso

# ─────────────────────────────────────────────────────────────────
#  ESTADO GLOBAL
# ─────────────────────────────────────────────────────────────────
stats = {
    "nodos_evaluados": 0,
    "ramas_podadas":   0,
    "podas_alfa":      0,
    "podas_beta":      0,
    "prof_max":        0,
}
log_arbol = []
modo_silencioso = False

# ─────────────────────────────────────────────────────────────────
#  TABLERO
# ─────────────────────────────────────────────────────────────────

def copiar_tablero(t):
    return t[:]

def hacer_movimiento(t, pos, jugador):
    nuevo = copiar_tablero(t)
    nuevo[pos] = jugador
    return nuevo

def obtener_movimientos(t):
    return [i for i, c in enumerate(t) if c == VACIO]

def imprimir_tablero(t, titulo="", resaltar=None, es_poda=False):
    c_titulo = ROJO if es_poda else CYAN
    c_borde  = ROJO if es_poda else AZUL
    if titulo:
        print(f"\n{c_titulo}{NEGRITA}  {titulo}{RESET}")
    sep = f"{c_borde}  ┼───┼───┼───┼{RESET}"
    print(sep)
    for fila in range(3):
        fila_str = f"{c_borde}  │{RESET}"
        for col in range(3):
            idx = fila * 3 + col
            celda = t[idx]
            if celda == JUGADOR_X:
                cc = VERDE
            elif celda == JUGADOR_O:
                cc = AMARILLO
            else:
                cc = GRIS
            if resaltar == idx:
                cc = MAGENTA + NEGRITA
            fila_str += f" {cc}{celda}{RESET} {c_borde}│{RESET}"
        print(fila_str)
        print(sep)

# ─────────────────────────────────────────────────────────────────
#  LÓGICA DEL JUEGO
# ─────────────────────────────────────────────────────────────────

LINEAS = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6),
]

def verificar_ganador(t):
    for a, b, c in LINEAS:
        if t[a] == t[b] == t[c] != VACIO:
            return +10 if t[a] == JUGADOR_X else -10
    return 0

def es_terminal(t):
    return verificar_ganador(t) != 0 or not obtener_movimientos(t)

def heuristica(t, prof):
    v = verificar_ganador(t)
    if v ==  10: return 10 - prof
    if v == -10: return -10 + prof
    return 0

# ─────────────────────────────────────────────────────────────────
#  ALFA-BETA PRUNING
# ─────────────────────────────────────────────────────────────────

def alfa_beta(t, prof, alfa, beta, es_max, mov_ant=None):
    global stats, modo_silencioso
    verbose = not modo_silencioso

    stats["prof_max"] = max(stats["prof_max"], prof)
    indent = "  " * prof

    # ── Caso base ────────────────────────────────────────────────
    if es_terminal(t):
        stats["nodos_evaluados"] += 1
        valor = heuristica(t, prof)
        ganador = verificar_ganador(t)
        if ganador > 0:   res = f"{VERDE}X GANA{RESET}"
        elif ganador < 0: res = f"{AMARILLO}O GANA{RESET}"
        else:             res = f"{GRIS}EMPATE{RESET}"

        if verbose:
            imprimir_tablero(t,
                titulo=f"[P{prof}] Terminal | valor={CYAN}{valor}{RESET} | {res}",
                resaltar=mov_ant)
            print(f"{indent}  {GRIS}↩ retorna {CYAN}{valor}{RESET}  α={alfa}  β={beta}")

        log_arbol.append(("terminal", prof,
            f"Terminal → valor={valor}  ({'X gana' if ganador>0 else 'O gana' if ganador<0 else 'empate'})",
            valor))
        return valor

    movimientos = obtener_movimientos(t)

    # ── Nodo MAX ─────────────────────────────────────────────────
    if es_max:
        mejor = NINF
        if verbose:
            imprimir_tablero(t,
                titulo=f"[P{prof}] {VERDE}MAX (X){RESET} | α={CYAN}{alfa}{RESET}  β={MAGENTA}{beta}{RESET}",
                resaltar=mov_ant)
            print(f"{indent}  Movimientos disponibles: {movimientos}")

        for mov in movimientos:
            stats["nodos_evaluados"] += 1
            if verbose:
                print(f"\n{indent}{VERDE}► MAX prueba pos={mov}{RESET}")

            valor = alfa_beta(hacer_movimiento(t, mov, JUGADOR_X),
                              prof + 1, alfa, beta, False, mov)

            if valor > mejor:
                mejor = valor
                if verbose:
                    print(f"{indent}  {VERDE}✔ MAX actualiza mejor={mejor}{RESET}")

            alfa = max(alfa, mejor)

            # PODA BETA
            if mejor >= beta:
                stats["ramas_podadas"] += 1
                stats["podas_beta"]    += 1
                restantes = movimientos[movimientos.index(mov) + 1:]
                print(f"\n{indent}{ROJO}{NEGRITA}✂ PODA BETA [P{prof}]{RESET}  "
                      f"{ROJO}valor={mejor} ≥ β={beta}  → MIN nunca elegiría esto{RESET}")
                print(f"{indent}  {ROJO}Ramas ignoradas: {restantes}{RESET}")
                for pos_p in restantes:
                    imprimir_tablero(
                        hacer_movimiento(t, pos_p, JUGADOR_X),
                        titulo=f"[✂ PODADA] pos={pos_p} — no se evalúa",
                        resaltar=pos_p, es_poda=True)
                log_arbol.append(("poda_beta", prof,
                    f"PODA BETA: {mejor}≥β={beta}  ignoradas={restantes}", mejor))
                break

        if verbose:
            print(f"{indent}{VERDE}↩ MAX retorna {mejor}{RESET}  α={alfa}  β={beta}")
        return mejor

    # ── Nodo MIN ─────────────────────────────────────────────────
    else:
        mejor = INF
        if verbose:
            imprimir_tablero(t,
                titulo=f"[P{prof}] {AMARILLO}MIN (O){RESET} | α={CYAN}{alfa}{RESET}  β={MAGENTA}{beta}{RESET}",
                resaltar=mov_ant)
            print(f"{indent}  Movimientos disponibles: {movimientos}")

        for mov in movimientos:
            stats["nodos_evaluados"] += 1
            if verbose:
                print(f"\n{indent}{AMARILLO}► MIN prueba pos={mov}{RESET}")

            valor = alfa_beta(hacer_movimiento(t, mov, JUGADOR_O),
                              prof + 1, alfa, beta, True, mov)

            if valor < mejor:
                mejor = valor
                if verbose:
                    print(f"{indent}  {AMARILLO}✔ MIN actualiza mejor={mejor}{RESET}")

            beta = min(beta, mejor)

            # PODA ALFA
            if mejor <= alfa:
                stats["ramas_podadas"] += 1
                stats["podas_alfa"]    += 1
                restantes = movimientos[movimientos.index(mov) + 1:]
                print(f"\n{indent}{ROJO}{NEGRITA}✂ PODA ALFA [P{prof}]{RESET}  "
                      f"{ROJO}valor={mejor} ≤ α={alfa}  → MAX nunca elegiría esto{RESET}")
                print(f"{indent}  {ROJO}Ramas ignoradas: {restantes}{RESET}")
                for pos_p in restantes:
                    imprimir_tablero(
                        hacer_movimiento(t, pos_p, JUGADOR_O),
                        titulo=f"[✂ PODADA] pos={pos_p} — no se evalúa",
                        resaltar=pos_p, es_poda=True)
                log_arbol.append(("poda_alfa", prof,
                    f"PODA ALFA: {mejor}≤α={alfa}  ignoradas={restantes}", mejor))
                break

        if verbose:
            print(f"{indent}{AMARILLO}↩ MIN retorna {mejor}{RESET}  α={alfa}  β={beta}")
        return mejor

# ─────────────────────────────────────────────────────────────────
#  BÚSQUEDA PRINCIPAL
# ─────────────────────────────────────────────────────────────────

def estimar_nodos(t):
    vacias = len(obtener_movimientos(t))
    total = 1
    for i in range(vacias, 0, -1):
        total *= i
        if total > MAX_NODOS_VERBOSE * 10:
            return total
    return total

def buscar_mejor_movimiento(tablero):
    global stats, log_arbol, modo_silencioso
    for k in stats: stats[k] = 0
    log_arbol.clear()

    estimado = estimar_nodos(tablero)
    modo_silencioso = estimado > MAX_NODOS_VERBOSE

    print(f"\n{CYAN}{'═'*62}{RESET}")
    print(f"{CYAN}{NEGRITA}  ALFA-BETA PRUNING{RESET}")
    if modo_silencioso:
        print(f"  {AMARILLO}⚠  Árbol grande (~{estimado}+ nodos sin poda).{RESET}")
        print(f"  {AMARILLO}   Modo SILENCIOSO: se muestran solo las PODAS.{RESET}")
    else:
        print(f"  {VERDE}Árbol pequeño. Mostrando TODOS los nodos.{RESET}")
    print(f"{CYAN}{'═'*62}{RESET}\n")

    mejor_val = NINF
    mejor_pos = -1

    for mov in obtener_movimientos(tablero):
        print(f"{MAGENTA}{'─'*62}{RESET}")
        print(f"{MAGENTA}{NEGRITA}  ► Raíz: X juega en posición {mov}{RESET}")
        print(f"{MAGENTA}{'─'*62}{RESET}")

        valor = alfa_beta(hacer_movimiento(tablero, mov, JUGADOR_X),
                          1, NINF, INF, False, mov)
        print(f"\n  {CYAN}pos={mov} → valor={valor}{RESET}")

        if valor > mejor_val:
            mejor_val = valor
            mejor_pos = mov

    return mejor_pos, mejor_val

# ─────────────────────────────────────────────────────────────────
#  RESUMEN Y ESTADÍSTICAS
# ─────────────────────────────────────────────────────────────────

def imprimir_resumen():
    print(f"\n{CYAN}{'═'*62}{RESET}")
    print(f"{CYAN}{NEGRITA}  RESUMEN DEL ÁRBOL{RESET}")
    print(f"{CYAN}{'═'*62}{RESET}")
    if not log_arbol:
        print(f"  {GRIS}(sin eventos registrados){RESET}")
        return
    for tipo, nivel, msg, val in log_arbol:
        pad = "  " + "  │  " * max(0, nivel - 1) + "  ├─ "
        if tipo == "terminal":
            icono, color = "◉", GRIS
        elif "poda" in tipo:
            icono, color = "✂", ROJO
        else:
            icono, color = "★", VERDE
        print(f"{pad}{color}{icono} [N{nivel}] {msg}{RESET}")

def imprimir_estadisticas(mejor_pos, mejor_val):
    print(f"\n{CYAN}{'═'*62}{RESET}")
    print(f"{CYAN}{NEGRITA}  RESULTADO FINAL{RESET}")
    print(f"{CYAN}{'═'*62}{RESET}")
    print(f"  {VERDE}Mejor posición → {NEGRITA}{mejor_pos}{RESET}")
    print(f"  {VERDE}Valor heurístico → {NEGRITA}{mejor_val}{RESET}")
    print(f"\n  {AZUL}Nodos evaluados  : {stats['nodos_evaluados']}{RESET}")
    print(f"  {ROJO}Ramas podadas    : {stats['ramas_podadas']}{RESET}")
    print(f"  {ROJO}  ✂ Podas alfa   : {stats['podas_alfa']}{RESET}")
    print(f"  {ROJO}  ✂ Podas beta   : {stats['podas_beta']}{RESET}")
    print(f"  {AMARILLO}Profundidad máx  : {stats['prof_max']}{RESET}")
    print(f"\n  {GRIS}Leyenda: {VERDE}X{GRIS}=MAX  {AMARILLO}O{GRIS}=MIN  "
          f"{MAGENTA}■{GRIS}=último mov  {ROJO}■{GRIS}=rama podada{RESET}")
    print(f"{CYAN}{'═'*62}{RESET}\n")

# ─────────────────────────────────────────────────────────────────
#  ESCENARIOS
# ─────────────────────────────────────────────────────────────────

ESCENARIOS = {
    "1": {
        "nombre": "Final inminente (2 vacías) — árbol mínimo, poda inmediata",
        "desc":   "X puede ganar en 1 movimiento",
        "tablero": [
            JUGADOR_X, JUGADOR_O, JUGADOR_X,
            JUGADOR_O, JUGADOR_X, JUGADOR_O,
            VACIO,     JUGADOR_O, VACIO,
        ],
    },
    "2": {
        "nombre": "Partida avanzada (3 vacías) — varias podas visibles",
        "desc":   "X tiene dos en fila, O debe bloquear",
        "tablero": [
            JUGADOR_X, JUGADOR_O, JUGADOR_X,
            JUGADOR_O, JUGADOR_X, VACIO,
            VACIO,     VACIO,     JUGADOR_O,
        ],
    },
    "3": {
        "nombre": "Partida media (4 vacías) — árbol mediano",
        "desc":   "X en centro, múltiples caminos",
        "tablero": [
            JUGADOR_X, JUGADOR_O, VACIO,
            VACIO,     JUGADOR_X, JUGADOR_O,
            VACIO,     VACIO,     VACIO,
        ],
    },
    "4": {
        "nombre": "Tablero abierto (5 vacías) — modo silencioso",
        "desc":   "Solo se imprimen las podas (árbol grande)",
        "tablero": [
            JUGADOR_X, JUGADOR_O, VACIO,
            VACIO,     JUGADOR_X, VACIO,
            VACIO,     JUGADOR_O, VACIO,
        ],
    },
}

def tablero_custom():
    print(f"\n{CYAN}  Ingresa cada fila: 3 valores separados por espacio.{RESET}")
    print(f"  {CYAN}Valores válidos: X  O  · (punto = vacío){RESET}\n")
    validos = {JUGADOR_X, JUGADOR_O, VACIO}
    tablero = []
    for fila in range(3):
        while True:
            ent = input(f"  Fila {fila+1}: ").strip().upper().replace('.', VACIO)
            partes = ent.split()
            if len(partes) == 3 and all(p in validos for p in partes):
                tablero.extend(partes)
                break
            print(f"  {ROJO}Entrada inválida. Ejemplo:  X · O{RESET}")
    return tablero

# ─────────────────────────────────────────────────────────────────
#  MENÚ Y MAIN
# ─────────────────────────────────────────────────────────────────

def limpiar():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu():
    limpiar()
    print(f"""
{CYAN}{NEGRITA}╔══════════════════════════════════════════════════════════╗
║        ALFA-BETA PRUNING — TRES EN RAYA (Python)         ║
╚══════════════════════════════════════════════════════════╝{RESET}
  {VERDE}X = MAX  (maximiza){RESET}   {AMARILLO}O = MIN  (minimiza){RESET}   {ROJO}✂ = Poda{RESET}

  {NEGRITA}Escenarios (ordenados de menor a mayor árbol):{RESET}""")
    for k, v in ESCENARIOS.items():
        n = len(obtener_movimientos(v["tablero"]))
        print(f"  {CYAN}[{k}]{RESET} {v['nombre']}  {GRIS}({n} vacías){RESET}")
        print(f"      {GRIS}{v['desc']}{RESET}")
    print(f"  {CYAN}[5]{RESET} Tablero personalizado")
    print(f"  {CYAN}[6]{RESET} Salir\n")
    return input(f"  {NEGRITA}Opción [1-6]: {RESET}").strip()

def main():
    while True:
        opcion = menu()

        if opcion in ESCENARIOS:
            tablero = ESCENARIOS[opcion]["tablero"][:]
            print(f"\n  {AMARILLO}{ESCENARIOS[opcion]['desc']}{RESET}")
        elif opcion == "5":
            tablero = tablero_custom()
        elif opcion == "6":
            print(f"\n{CYAN}  ¡Hasta luego!{RESET}\n")
            break
        else:
            print(f"\n{ROJO}  Opción no válida.{RESET}")
            input("  ENTER para continuar...")
            continue

        if es_terminal(tablero):
            print(f"\n{ROJO}  El tablero ya está en estado terminal (juego terminado).{RESET}")
            input("  ENTER para continuar...")
            continue

        if not obtener_movimientos(tablero):
            print(f"\n{ROJO}  No quedan movimientos disponibles.{RESET}")
            input("  ENTER para continuar...")
            continue

        print(f"\n{NEGRITA}  Tablero de entrada:{RESET}")
        imprimir_tablero(tablero)
        input(f"\n{GRIS}  Presiona ENTER para ejecutar la búsqueda...{RESET}")
        limpiar()

        mejor_pos, mejor_val = buscar_mejor_movimiento(tablero)

        imprimir_resumen()
        imprimir_estadisticas(mejor_pos, mejor_val)

        print(f"{VERDE}{NEGRITA}  Tablero tras el mejor movimiento de X:{RESET}")
        imprimir_tablero(hacer_movimiento(tablero, mejor_pos, JUGADOR_X),
                         titulo=f"Mejor jugada → posición {mejor_pos}",
                         resaltar=mejor_pos)

        input(f"\n{GRIS}  ENTER para volver al menú...{RESET}")
        limpiar()


if __name__ == "__main__":
    main()