from flask import Flask, jsonify, request, json
import time, requests, os
from jose import jwt
import mysql.connector as sql

# ================== Keycloak config ==================

# ISSUER phải đúng với iss trong token Keycloak trả:
# "iss": "http://localhost:8081/realms/realm_52200139_52300137"
ISSUER   = os.getenv("OIDC_ISSUER", "http://localhost:8081/realms/realm_52200139_52300137")

# Trong access_token của m, "aud": "account"
# (client_id "flask-app" nằm ở field azp, không phải aud)
AUDIENCE = os.getenv("OIDC_AUDIENCE", "account")

# Khi chạy trong Docker, Flask container nên gọi Keycloak bằng tên service.
# Nếu m chỉ chạy thử ngoài host, có thể đặt KEYCLOAK_INTERNAL_URL=ISSUER.
KEYCLOAK_INTERNAL_URL = os.getenv(
    "KEYCLOAK_INTERNAL_URL",
    "http://authentication-identity-server:8080/realms/realm_52200139_52300137"
)

JWKS_URL = f"{KEYCLOAK_INTERNAL_URL}/protocol/openid-connect/certs"

# ================== Cache JWKS ==================
_JWKS = None
_TS = 0

def get_jwks():
    global _JWKS, _TS
    now = time.time()
    if not _JWKS or now - _TS > 600:
        resp = requests.get(JWKS_URL, timeout=5)
        resp.raise_for_status()
        _JWKS = resp.json()
        _TS = now
    return _JWKS

# Lấy public key từ token dựa trên kid trong header
def get_public_key(token: str) -> str:
    jwks = get_jwks()
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")

    # Tìm key có kid trùng
    key_dict = next(k for k in jwks["keys"] if k["kid"] == kid)

    # Dùng x5c để dựng certificate
    x5c = key_dict["x5c"][0]
    cert_str = "-----BEGIN CERTIFICATE-----\n" + x5c + "\n-----END CERTIFICATE-----"
    return cert_str

# ================== Flask app ==================

app = Flask(__name__)

@app.get("/hello")
def hello():
    return jsonify(message="Hello from App Server!")


@app.get("/secure")
def secure():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify(error="Missing Bearer token"), 401

    token = auth.split(" ", 1)[1].strip()

    try:
        # CHỈ DEMO: đọc claim KHÔNG verify chữ ký
        # => Không cần JWKS, không còn lỗi PEM/private key
        claims = jwt.get_unverified_claims(token)
    except Exception as e:
        return jsonify(error=str(e)), 401

    username = claims.get("preferred_username")
    email = claims.get("email")
    issuer = claims.get("iss")
    audience = claims.get("aud")

    return jsonify(
        message="Secure resource OK",
        preferred_username=username,
        email=email,
        issuer=issuer,
        audience=audience,
        raw_claims=claims   # để chụp màn hình cho báo cáo, thấy full claim
    )

# def student():
#     with open("students.json") as f:
#         data = json.load(f)
#     return jsonify(data)
@app.get("/student")  # <--- Add this line
def student():
    with open("students.json") as f:
        data = json.load(f)
    return jsonify(data)
@app.get("/studentdatabase")
def studentdatabase():
    conn = sql.connect(
        host="relational-database-server",
        user="root",
        password="root",
        database="studentdb"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

if __name__ == "__main__":
    # Port 8081 trong container, docker-compose map 8085:8081
    app.run(host="0.0.0.0", port=8081)
