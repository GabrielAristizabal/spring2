  GNU nano 7.2                                                            cliente.py                                                                     
import requests

# Reemplaza con el DNS público del ALB + endpoint
URL = "http://balanceador-952015566.us-east-1.elb.amazonaws.com/pedido"

def main():
    try:
        r = requests.get(URL, timeout=5, headers={"Accept": "application/json"})
        print("Status code:", r.status_code)
        print("Respuesta cruda:", r.text)
        if r.ok and r.headers.get("Content-Type", "").startswith("application/json"):
            print("JSON parseado:", r.json())
    except Exception as e:
        print("❌ Excepción al llamar al ALB:", e)

if __name__ == "__main__":
    main()






