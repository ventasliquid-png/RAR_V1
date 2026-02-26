from cryptography import x509
from cryptography.hazmat.backends import default_backend
import os

def dump_cert(p):
    if not os.path.exists(p):
        print(f"File not found: {p}")
        return
    try:
        with open(p, 'rb') as f:
            cert = x509.load_pem_x509_certificate(f.read(), default_backend())
            print(f"--- {p} ---")
            print(f"Subject: {cert.subject}")
            for attr in cert.subject:
                print(f"  {attr.oid._name}: {attr.value}")
    except Exception as e:
        print(f"Error reading {p}: {e}")

certs_to_check = [
    'certs/certificado.crt',
    'certs/certificado_06_02_2026.crt',
    'certs/sonidoliquido.crt'
]

for c in certs_to_check:
    dump_cert(c)
