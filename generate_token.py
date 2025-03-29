import os
import jwt
import uuid
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

APP_KEY = os.getenv("APP_KEY")
VALID_IDENTIFIERS = eval(os.getenv("HEXOME_API_VALID_IDENTIFIERS"))

def generate_token(identifier):
    """Genera un token JWT para un identificador válido."""
    if identifier not in VALID_IDENTIFIERS:
        raise ValueError("Identificador no válido.")
    
    payload = {
        "identifier": identifier
    }
    token = jwt.encode(payload, APP_KEY, algorithm="HS256")
    return token

if __name__ == "__main__":
    identifier = input("Introduce un identificador válido: ")
    try:
        token = generate_token(identifier)
        print(f"Token JWT generado: {token}")
    except ValueError as e:
        print(e)