import requests, time

URL = "http://balanceador-952015566.us-east-1.elb.amazonaws.com"  # ← pon tu DNS con esquema

def fetch_json(url, tries=3, timeout=5):
    for _ in range(tries):
        r = requests.get(url, timeout=timeout, headers={"Accept": "application/json"})
        if r.ok and r.headers.get("Content-Type","").startswith("application/json"):
            return r.json()
        time.sleep(0.2)  # backoff corto
    # Si llega aquí, algo está mal en infraestructura; devolvemos None sin spam
    return None

for i in range(10):
    data = fetch_json(URL)
    if data is not None:
        print(f"Respuesta {i+1}: {data}")
    else:
        # Un único mensaje claro si falla tras reintentos
        print(f"Respuesta {i+1}: Error al obtener JSON (revisa ALB/health checks/SG)")


