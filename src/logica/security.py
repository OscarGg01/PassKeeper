import os
from cryptography.fernet import Fernet

RUTA_CONTRASEÑA_MAESTRA = "master_password.txt"
RUTA_CLAVE = "clave.key"


# Genera o carga la clave de encriptación
def cargar_clave():
    if os.path.exists(RUTA_CLAVE):
        with open(RUTA_CLAVE, "rb") as file:
            clave = file.read()
    else:
        clave = Fernet.generate_key()
        with open(RUTA_CLAVE, "wb") as file:
            file.write(clave)
    return clave


clave = cargar_clave()
f = Fernet(clave)


def encriptar_contraseña(contraseña):
    """Encripta la contraseña proporcionada."""
    return f.encrypt(contraseña.encode()).decode()


def desencriptar_contraseña(contraseña_encriptada):
    """Desencripta la contraseña encriptada."""
    return f.decrypt(contraseña_encriptada.encode()).decode()


def verificar_contraseña_maestra(contraseña):
    """Verifica si la contraseña proporcionada coincide con la contraseña maestra almacenada."""
    if os.path.exists(RUTA_CONTRASEÑA_MAESTRA):
        with open(RUTA_CONTRASEÑA_MAESTRA, "r") as file:
            contraseña_encriptada = file.read()
        return desencriptar_contraseña(contraseña_encriptada) == contraseña
    else:
        return False


def establecer_contraseña_maestra(contraseña):
    """Establece una nueva contraseña maestra encriptada."""
    with open(RUTA_CONTRASEÑA_MAESTRA, "w") as file:
        file.write(encriptar_contraseña(contraseña))
