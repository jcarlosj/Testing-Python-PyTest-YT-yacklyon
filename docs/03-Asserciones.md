# Asserts (Afirmaciones/Verificaciones)

Una aserción tiene como objetivo afirmar/verificar algo. Cuando definimos las aserciones es importante tener en cuenta los siguientes aspectos:

- __Nombres de las Pruebas:__ Escribir los nombres claros de la prueba que se está diseñando.

    `test_1` no nos deja claro específicamente que prueba se esta verificando.

- __No mezclar varios conceptos:__ A la hora de realizar verificaciones debemos evitar mezclar varias verificaciones diferentes dentro del contexto de una prueba. Es difícil saber qué falló si se rompe. Recomendación separarlos en pruebas pequeñas con un solo propósito de verificación.

Para ilustrar estos dos errores comunes (el antipatrón de nombres genéricos y el antipatrón del "test monstruo" que mezcla conceptos), tomemos como base una función simple de registro de usuarios:

Archivo: `registrar_usuario.py`, en este se desarrolla la funcionalidad requerida

```Python
# Código a probar (lógica de negocio básica)
def registrar_usuario(nombre, edad, email):
    if not nombre.strip():
        raise ValueError("El nombre no puede estar vacío")
    if edad < 18:
        raise ValueError("El usuario debe ser mayor de edad")
    if "@" not in email:
        raise ValueError("El formato de correo es inválido")
    
    return {
        "nombre": nombre.strip(),
        "edad": edad,
        "email": email.lower(),
        "activo": True
    }
```

## 1. El antipatrón: Lo que NO se debe hacer

Instrospección: Inspección Automática de Fallos

Aquí se cometen ambos errores al mismo tiempo: nombres sin significado (`test_1`, `test_2`) y un solo test que valida creación, validaciones, transformaciones de texto y estados de negocio.

Archivo: `test_registrar_usuario.py`

```Python
import pytest

# ERROR 1: Nombre completamente ambiguo.
# Si falla, en la terminal solo leerás "FAILED test_1". No sabes qué falló.
# ERROR 2: Mezcla múltiples conceptos en un solo bloque.
def test_1():
    # Concepto A: Creación básica
    u1 = registrar_usuario("Carlos", 25, "carlos@mail.com")
    assert u1["activo"] is True
    assert u1["edad"] == 25
    
    # Concepto B: Transformación de datos (limpieza de espacios y minúsculas)
    u2 = registrar_usuario("  Ana  ", 30, "ANA@MAIL.COM")
    assert u2["nombre"] == "Ana"
    assert u2["email"] == "ana@mail.com"

    # Concepto C: Validación de edad
    with pytest.raises(ValueError):
        registrar_usuario("Pedro", 15, "pedro@mail.com")

    # Concepto D: Validación de correo
    with pytest.raises(ValueError):
        registrar_usuario("Laura", 20, "correo_invalido")


# ERROR 1 reiterado: Nombre sin contexto de escenario ni resultado esperado
def test_2():
    with pytest.raises(ValueError):
        registrar_usuario("", 22, "test@mail.com")
```

Por qué causa problemas este enfoque:

- __Efecto dominó__: Si assert u1["activo"] is True falla, la ejecución se detiene de inmediato. Los conceptos B, C y D nunca se ejecutan, ocultando si esas otras partes funcionan o también están rotas.

- __Depuración lenta__: El reporte de error dirá test_1 FAILED, obligando a entrar al código a buscar el número de línea exacto para entender si falló el correo, la edad o los espacios del nombre.

## 2. La refactorización: Lo que SÍ se debe hacer

Dividir cada comportamiento en una prueba atómica con nombres descriptivos que expliquen: qué se prueba, bajo qué condición y cuál es el resultado esperado (patrón habitual: `test_[accion]_[escenario]_[resultado]`).

```Python
import pytest

# --- Pruebas de Flujo Exitoso (Happy Path) y Transformación ---

def test_registrar_usuario_con_datos_validos_retorna_usuario_activo():
    resultado = registrar_usuario("Carlos", 25, "carlos@mail.com")
    
    assert resultado["activo"] is True
    assert resultado["nombre"] == "Carlos"


def test_registrar_usuario_normaliza_espacios_y_convierte_email_a_minusculas():
    resultado = registrar_usuario("  Ana  ", 30, "ANA@MAIL.COM")
    
    assert resultado["nombre"] == "Ana"
    assert resultado["email"] == "ana@mail.com"


# --- Pruebas de Validaciones y Errores (Un concepto por prueba) ---

def test_registrar_usuario_menor_de_edad_lanza_error():
    with pytest.raises(ValueError, match="mayor de edad"):
        registrar_usuario("Pedro", 17, "pedro@mail.com")


def test_registrar_usuario_con_email_sin_arroba_lanza_error():
    with pytest.raises(ValueError, match="correo es inválido"):
        registrar_usuario("Laura", 20, "correosinformato.com")


def test_registrar_usuario_con_nombre_en_blanco_lanza_error():
    with pytest.raises(ValueError, match="no puede estar vacío"):
        registrar_usuario("   ", 22, "test@mail.com")
```

Al estructurarlo de esta manera, si alguien modifica la validación de edad y rompe el código, la terminal mostrará directamente:
> `FAILED test_registrar_usuario_menor_de_edad_lanza_error`

El diagnóstico es instantáneo sin necesidad de inspeccionar trazas extensas.