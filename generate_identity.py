from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID
import os

CERT_DIR = r"C:\dev\RAR_V1\certs"
KEY_FILE = os.path.join(CERT_DIR, "produccion_liquid.key")
CSR_FILE = os.path.join(CERT_DIR, "produccion_liquid.csr")

def generate_identity():
    # Ensure certs directory exists
    if not os.path.exists(CERT_DIR):
        print(f"Creating directory: {CERT_DIR}")
        os.makedirs(CERT_DIR)

    # 1. Create Private Key
    print("Generating Private Key (2048 bits)...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Save Private Key
    with open(KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    print(f"[OK] Private Key saved to: {KEY_FILE}")

    # 2. Generate CSR
    print("Generating Certificate Signing Request (CSR)...")
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "AR"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SONIDO LIQUIDO S.R.L."),
        x509.NameAttribute(NameOID.COMMON_NAME, "LiquidSound_Prod"),
        # Note: 'CUIT' is usually not a standard OID here, but often included in Organization Name or as a custom field. 
        # AFIP standard usually puts CUIT in 'serialNumber' or simply relies on the OU being 'IT' or similar + O=org name.
        # However, the user specifically asked for CUIT: 30715603973 in the CSR data. 
        # Often for AFIP one puts 'CUIT 30715603973' as the Organization Name or simpler.
        # But let's check standard practice. Standard is to include CUIT as 'serialNumber' = 'CUIT 30715603973'.
        # Or simply O="SONIDO LIQUIDO S.R.L.", CN="LiquidSound_Prod", C="AR" and the CUIT is bound during the certificate generation process on the AFIP site.
        # But wait, looking at the instruction: "Datos para el CSR: ... CUIT: 30715603973".
        # I'll include it as a standard OID if possible, or usually it's `serialNumber`.
        x509.NameAttribute(NameOID.SERIAL_NUMBER, "CUIT 30715603973"),
    ])).sign(private_key, hashes.SHA256(), default_backend())

    # Save CSR
    with open(CSR_FILE, "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))
    print(f"[OK] CSR saved to: {CSR_FILE}")

if __name__ == "__main__":
    try:
        generate_identity()
    except Exception as e:
        print(f"[ERROR]: {e}")
