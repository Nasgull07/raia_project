"""
Script para generar certificados SSL autofirmados para HTTPS
Usa la librería cryptography de Python (no requiere OpenSSL externo)
"""
import sys
import socket
import ipaddress
from pathlib import Path
from datetime import datetime, timedelta

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print("❌ La librería 'cryptography' no está instalada.")
    print("   Instálala con: pip install cryptography")
    sys.exit(1)

def obtener_ip_local():
    """Obtiene la IP local de la red"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

def generar_certificados():
    """Genera certificados SSL autofirmados usando cryptography"""
    
    cert_path = Path(__file__).parent / "cert.pem"
    key_path = Path(__file__).parent / "key.pem"
    
    # Si ya existen, preguntar si sobrescribir
    if cert_path.exists() or key_path.exists():
        respuesta = input("⚠️  Los certificados ya existen. ¿Sobrescribir? (s/n): ")
        if respuesta.lower() != 's':
            print("Cancelado")
            return
    
    print("🔐 Generando certificados SSL autofirmados...")
    
    # Obtener IP local
    ip_local = obtener_ip_local()
    if ip_local:
        print(f"   📍 Detectada IP local: {ip_local}")
    else:
        print(f"   ⚠️  No se pudo detectar IP local, solo se usará localhost")
    
    try:
        # Generar clave privada
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Información del certificado
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Estado"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Ciudad"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "RAIA OCR"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        # Crear lista de nombres alternativos (SAN)
        san_list = [
            x509.DNSName("localhost"),
            x509.DNSName("*.localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]
        
        # Agregar IP local si se detectó
        if ip_local:
            try:
                san_list.append(x509.IPAddress(ipaddress.IPv4Address(ip_local)))
            except:
                pass
        
        # Crear certificado
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Guardar clave privada
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Guardar certificado
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        print(f"\n✅ Certificados generados correctamente:")
        print(f"   - Certificado: {cert_path}")
        print(f"   - Clave privada: {key_path}")
        print(f"   - Válido por: 365 días")
        print(f"   - Válido para: localhost, 127.0.0.1" + (f", {ip_local}" if ip_local else ""))
        print(f"\n⚠️  Nota: Los navegadores mostrarán una advertencia de seguridad.")
        print(f"   Esto es normal con certificados autofirmados.")
        print(f"   Deberás aceptar manualmente el riesgo en tu navegador.")
        
    except Exception as e:
        print(f"❌ Error al generar certificados: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generar_certificados()
