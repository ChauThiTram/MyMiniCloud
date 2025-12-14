from jose import jwt
import requests

def verify_token(token):
    # Lấy JWKS từ Keycloak
    jwks_url = "http://localhost:8081/realms/realm_52200139_52300137/protocol/openid-connect/certs"
    jwks = requests.get(jwks_url).json()

    # Lấy kid từ header token
    kid = jwt.get_unverified_header(token)['kid']
    key = next(k for k in jwks['keys'] if k['kid'] == kid)

    # Verify token RS256
    payload = jwt.decode(
        token,
        key,
        algorithms=['RS256'],
        audience='flask-app',  # phải trùng với client_id trong Keycloak
        issuer='http://localhost:8081/realms/realm_52200139_52300137'
    )

    return payload
