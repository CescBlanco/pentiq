import requests
import pandas as pd

# ⚠️ Fotmob protege su API con la cabecera anti-bot "x-mas" (+ referer/cookie).
# Sin ella, requests.get() no da error, pero te sirve una respuesta de una capa
# de caché distinta a la que ves logueado en el navegador -> datos diferentes.
# La forma robusta de resolverlo es usar una librería que la mantenga
# actualizada, por ejemplo:
#   pip install mobfot
# o
#   pip install fotmob-api  (github.com/C-Roensholt/fotmob-api)
#
# Aquí dejo la versión "manual" con al menos headers de navegador real,
# que reduce (no elimina del todo) el problema, y arreglo los bugs de
# merge/columnas que también estaban rompiendo tus números.

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"),
    "Referer": "https://www.fotmob.com/",
    "Accept": "application/json, text/plain, */*",
}

session = requests.Session()
session.headers.update(HEADERS)


def obtener_metricas_completas(id_liga, season_in=2025, season_out=2026, pais="ENG", debug=False):
    temporada = f"{season_in}/{season_out}"
    params = {"id": id_liga, "ccode3": pais, "season": temporada}

    r = session.get("https://www.fotmob.com/api/data/leagues", params=params)
    r.raise_for_status()
    data = r.json()

    stats = data.get("stats", {})
    equipos_stats = stats.get("teams", [])

    if debug:
        # Imprime los nombres REALES que trae fotmob, en vez de asumirlos.
        print("Nombres de bloques disponibles:")
        for b in equipos_stats:
            print(" -", b.get("name"))

    # En vez de adivinar nombres exactos, buscamos por coincidencia parcial
    objetivo = {
        "expected_goals_team": "expected_goals",
        "expected_points_team": "expected_points",
        "expected_goals_conceded_team": "expected_goals_conceded",
        "xg_diff_team": "xg_diff",
        "expected_goals_diff_team": "xg_diff",
        "xpts_diff_team": "xpts_diff",
        "expected_points_diff_team": "xpts_diff",
    }

    fetch_urls = {}
    for bloque in equipos_stats:
        nombre = bloque.get("name")
        if nombre in objetivo:
            fetch_urls[objetivo[nombre]] = bloque.get("fetchAllUrl")

    resultados = {}

    for alias, url in fetch_urls.items():
        if not url:
            continue
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = "https://www.fotmob.com" + url

        r2 = session.get(url)
        r2.raise_for_status()
        datos = r2.json()

        toplists = datos.get("TopLists") or []
        if not toplists:
            continue
        stat_list = toplists[0].get("StatList", [])
        if not stat_list:
            continue

        df = pd.DataFrame(stat_list)

        # nos quedamos con lo esencial y usamos TeamId como llave si existe
        keep = {
            "ParticipantName": "team",
            "ParticipantId": "team_id",
            "MatchesPlayed": "played",
            "StatValue": alias,
            "Rank": f"rank_{alias}",
        }
        cols_presentes = {k: v for k, v in keep.items() if k in df.columns}
        df = df.rename(columns=cols_presentes)

        columnas_finales = ["team"]
        if "team_id" in df.columns:
            columnas_finales.append("team_id")
        columnas_finales += [c for c in ["played", alias, f"rank_{alias}"] if c in df.columns]

        resultados[alias] = df[columnas_finales]

    if not resultados:
        raise ValueError("No se encontró ninguno de los bloques esperados. "
                          "Ejecuta con debug=True para ver los nombres reales.")

    # 4️⃣ Unir todas las métricas SOLO por equipo (nunca por "played",
    # que puede variar ligeramente entre endpoints y duplicar/perder filas)
    df_final = None
    llave = "team_id" if all("team_id" in df.columns for df in resultados.values()) else "team"

    for alias, df in resultados.items():
        df_reducido = df.drop(columns=[c for c in ["played"] if c in df.columns and df_final is not None])
        if df_final is None:
            df_final = df
        else:
            # evitamos duplicar "played" y "team" en cada merge
            cols_extra = [c for c in df.columns if c not in (llave, "team", "played")]
            df_final = df_final.merge(df[[llave] + cols_extra], on=llave, how="outer")

    df_final["Temporada"] = temporada

    if "expected_points" in df_final.columns:
        df_final = df_final.sort_values(by="expected_points", ascending=False)
    elif "expected_goals" in df_final.columns:
        df_final = df_final.sort_values(by="expected_goals", ascending=False)

    df_final.reset_index(drop=True, inplace=True)

    # xGDiff/xPTSDiff: si fotmob ya nos dio los endpoints de diff, no los recalculamos
    # a mano (SubStatValue no es "goles concedidos", así que restar a mano da un número
    # distinto al que muestra la web). Solo como fallback si no vinieron:
    if "xg_diff" not in df_final.columns and {"expected_goals", "expected_goals_conceded"} <= set(df_final.columns):
        df_final["xGDiff"] = df_final["expected_goals"] - df_final["expected_goals_conceded"]

    return df_final


def obtener_tabla_posiciones(id_liga, season_in=2025, season_out=2026, pais="ENG", debug=False):
    """
    Extrae las 5 tablas que se ven en la pestaña 'Tabla' de fotmob:
    Todos, Local, Visitante, Últimos 5 partidos (form) y xG.

    OJO: esto viene de una parte distinta del JSON que las métricas de
    'Estad. Equipos' -> está en data['table'][0]['data']['table'], NO en
    data['stats']['teams']. Por eso el scraper original nunca la encontraba.
    """
    temporada = f"{season_in}/{season_out}"
    params = {"id": id_liga, "ccode3": pais, "season": temporada}

    r = session.get("https://www.fotmob.com/api/data/leagues", params=params)
    r.raise_for_status()
    data = r.json()

    # A veces la respuesta trae la tabla "partida" (torneos con grupos) y
    # entonces 'table' es una lista con más de un elemento en vez de un dict
    # directo -> por eso probamos ambas rutas.
    try:
        tablas = data["table"][0]["data"]["table"]
    except (KeyError, IndexError, TypeError):
        try:
            tablas = data["table"][0]["data"]["tables"]
            if debug:
                print("⚠️ Esta liga tiene tabla partida en grupos, revisa 'tablas' manualmente.")
            return tablas
        except (KeyError, IndexError, TypeError):
            raise ValueError("No se encontró la estructura de tabla esperada. "
                              "Ejecuta con debug=True e inspecciona 'data[\"table\"]' a mano.")

    if debug:
        print("Pestañas de tabla disponibles:", list(tablas.keys()))

    resultado = {}
    for filtro in ["all", "home", "away", "form", "xg"]:
        filas = tablas.get(filtro)
        if not filas:
            continue
        df = pd.DataFrame(filas)
        df["filtro"] = filtro
        df["Temporada"] = temporada
        resultado[filtro] = df

        if debug:
            print(f"\nColumnas de '{filtro}':", list(df.columns))

    return resultado


# IDs de fotmob para las 5 grandes ligas europeas
GRANDES_LIGAS = {
    "Premier League": {"id": 47, "pais": "ENG"},
    "La Liga":        {"id": 87, "pais": "ESP"},
    "Serie A":        {"id": 55, "pais": "ITA"},
    "Bundesliga":     {"id": 54, "pais": "GER"},
    "Ligue 1":        {"id": 53, "pais": "FRA"},
}


def obtener_tablas_grandes_ligas(season_in=2025, season_out=2026, debug=False):
    """
    Recorre las 5 grandes ligas y devuelve un diccionario anidado:
        { "Premier League": {"all": df, "home": df, "away": df, "form": df, "xg": df},
          "La Liga":        {...},
          ... }
    Cada df ya trae las columnas 'liga' y 'Temporada' añadidas.
    """
    resultado = {}
    for liga, info in GRANDES_LIGAS.items():
        if debug:
            print(f"\n=== {liga} ===")
        try:
            tablas = obtener_tabla_posiciones(
                info["id"], season_in, season_out, pais=info["pais"], debug=debug
            )
        except Exception as e:
            print(f"⚠️ Error obteniendo {liga}: {e}")
            continue

        for filtro, df in tablas.items():
            df["liga"] = liga

        resultado[liga] = tablas

    return resultado


def unir_tablas_por_filtro(dict_ligas, filtro="xg"):
    """
    Útil si en vez de un dict por liga quieres un único DataFrame con
    todas las ligas juntas para un filtro dado (p.ej. "xg").
    """
    dfs = [tablas[filtro] for tablas in dict_ligas.values() if filtro in tablas]
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


if __name__ == "__main__":
    # Métricas agregadas (xG, xPTS, xGA...) de "Estad. Equipos" - Premier League de ejemplo
    df_metricas = obtener_metricas_completas(47, debug=True)
    print(df_metricas)

    # Un dict con las 5 tablas de cada una de las 5 grandes ligas
    todas_las_ligas = obtener_tablas_grandes_ligas(debug=True)

    # Acceso individual, por ejemplo:
    df_xg_premier = todas_las_ligas["Premier League"]["xg"]
    df_xg_laliga = todas_las_ligas["La Liga"]["xg"]
    df_todos_seriea = todas_las_ligas["Serie A"]["all"]

    print("\n--- xG Premier League ---")
    print(df_xg_premier)

    # O si prefieres una sola tabla "xg" con las 5 ligas apiladas:
    df_xg_todas = unir_tablas_por_filtro(todas_las_ligas, "xg")
    print("\n--- xG de las 5 grandes ligas junto ---")
    print(df_xg_todas)
