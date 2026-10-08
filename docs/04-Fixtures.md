# Fixtures

Un fixture en Python (principalmente popularizado por pytest) es una función que se encarga de preparar el entorno o los datos necesarios antes de que se ejecute una prueba, y opcionalmente limpiar o destruir esos recursos una vez que la prueba finaliza.

En términos sencillos: es el mecanismo para resolver el Setup (preparación) y el Teardown (limpieza) de manera modular, reutilizable y desacoplada de la prueba en sí.

## ¿Qué problemas resuelve un Fixture?

Sin fixtures, es común repetir la creación de objetos, conexiones o archivos en cada función de test:

- __Duplicación__ de código: Repetir 5 o 10 líneas de configuración en 20 pruebas distintas.

- __Mantenimiento frágil__: Si cambia la estructura del modelo o la base de datos, hay que actualizar decenas de pruebas manualmente.

- __Falta de aislamiento__: Si una prueba modifica un objeto compartido o deja archivos creados en el disco, puede provocar que otras pruebas fallen de rebote.

## ¿Cómo funciona un Fixture en `pytest`?

Se define decorando una función con @pytest.fixture. Luego, cualquier función de prueba que necesite ese recurso simplemente lo declara como un parámetro con el mismo nombre (mediante inyección de dependencias).

### 1. Fixture simple: Suministro de datos de prueba

```Python
import pytest

@pytest.fixture
def usuario():
    usuario = {
        "nombre": "Juan Carlos",
        "edad": 48,
        "email": "jcarlosj@correo.co",
        "activo": True
    }
    
    return usuario

# Test 1: Verificar que el nombre sea correcto
def test_nombre(usuario):
    assert usuario["nombre"] == "Juan Carlos"

# Test 2: Verificar que la edad sea correcta
def test_edad(usuario):
    assert usuario["edad"] == 48
    
# Test 3: Verificar que el email sea correcto
def test_email(usuario):
    assert usuario["email"] == "jcarlosj@correo.co"

# Test 4: Verificar que sea un email valido
def test_email_valido(usuario):
    assert "@" in usuario["email"]
    assert "." in usuario["email"]
    assert len(usuario["email"]) > 5
    assert usuario["email"].split("@")[1].count(".") > 0
    assert usuario["email"].count("@") == 1

# Test 5: Verificar que el estado sea activo
def test_activo(usuario):
    assert usuario["activo"] is True
```

### 2. Fixture con ciclo de vida completo (Setup + Teardown)

Cuando necesitas inicializar un recurso (abrir una base de datos temporal, crear un archivo, levantar un cliente HTTP) y destruirlo al terminar la prueba, se usa la palabra clave `yield`:

- Todo lo que está antes de yield se ejecuta antes del test (Setup).
- El valor que acompaña al yield es lo que recibe la prueba.
- Todo lo que está después de yield se ejecuta después del test (Teardown), incluso si la prueba falló.

```Python
import pytest
import sqlite3

@pytest.fixture
def db_en_memoria():
    # --- SETUP ---
    conexion = sqlite3.connect(":memory:")
    cursor = conexion.cursor()
    cursor.execute("CREATE TABLE productos (id INTEGER PRIMARY KEY, nombre TEXT)")
    
    yield conexion  # Entrega la conexión al test
    
    # --- TEARDOWN ---
    conexion.close()

def test_insertar_producto(db_en_memoria):
    cursor = db_en_memoria.cursor()
    cursor.execute("INSERT INTO productos (nombre) VALUES ('Teclado')")
    
    cursor.execute("SELECT COUNT(*) FROM productos")
    total = cursor.fetchone()[0]
    
    assert total == 1
```

#### Alcance de un Fixture (scope)

Por defecto, un fixture se ejecuta una vez por cada función de prueba (scope="function"), garantizando aislamiento total. Sin embargo, para recursos pesados de inicializar (como levantar un contenedor Docker o cargar un modelo de Machine Learning), se puede ajustar su ciclo de vida con el parámetro scope:

| Scope | Descripción |
| :--- | :--- |
| `function` (por defecto) | Antes de cada función de test individual |
| `class` | Una sola vez por cada clase de pruebas. |
| `module`| Una sola vez por cada archivo `.py` |
| `session`| Una sola vez para toda la batería de pruebas que corras en la terminal |

```Python
# Se ejecuta una sola vez para todo el archivo de pruebas
@pytest.fixture(scope="module")
def cliente_api():
    cliente = inicializar_cliente_pesado()
    yield cliente
    cliente.cerrar()
```

### Compartir fixtures globalmente: `conftest.py`

Si tienes fixtures que necesitan múltiples archivos de prueba, no necesitas importarlos manualmente. En pytest, cualquier fixture colocado en un archivo especial llamado conftest.py en la raíz o en los directorios de tests queda disponible automáticamente para todos los tests de ese directorio y sus subdirectorios.

## Estructura de archivos profesional

En proyectos reales no se colocan las pruebas sueltas en la raíz junto al código fuente; se separan en su propio directorio `tests/` para mantener limpio el entorno de producción y empaquetado.

### 1. Estructura estándar recomendada (Layout con carpeta `tests/`)

```Text
raiz-proyecto/
│
├── mi_paquete/               # Código fuente de tu aplicación
│   ├── __init__.py
│   ├── auth.py
│   └── usuario.py            # Lógica de negocio (ej. clases o funciones)
│
├── tests/                    # Directorio exclusivo de pruebas
│   ├── __init__.py           # Opcional, pero recomendado para resolución de paquetes
│   ├── conftest.py           # Fixtures compartidos para TODAS las pruebas
│   ├── test_auth.py          # Pruebas de autenticación
│   └── test_usuario.py       # Pruebas de usuarios (consume fixtures de conftest.py)
│
├── pyproject.toml            # Configuración del proyecto / dependencias
└── README.md
```

### 2. Estructura modular (Múltiples conftest.py por ámbito)

pytest permite jerarquías de conftest.py. Un fixture definido en un subdirectorio solo afecta a las pruebas de ese subdirectorio:

```Text
mi_proyecto/
│
├── src/
│   └── ...
│
└── tests/
    ├── conftest.py           # Fixtures globales (ej. cliente HTTP general, db en memoria)
    │
    ├── unit/                 # Pruebas unitarias puras
    │   ├── test_modelos.py
    │   └── test_validaciones.py
    │
    └── api/                  # Pruebas de integración o endpoints
        ├── conftest.py       # Fixtures exclusivos para la API (ej. tokens JWT, headers simulados)
        └── test_endpoints.py
```

Reglas clave para trabajar con `conftest.py`

- __Nunca importar conftest directamente:__ Si escribes `from conftest import usuario`, rompes el ciclo de inyección y el aislamiento de `pytest`.
- __Alcance descendente:__ Los fixtures en `tests/conftest.py` están disponibles para cualquier test dentro de `tests/` y cualquier subcarpeta (`tests/unit/`, etc.).
- __Mantenerlo enfocado:__ Usa `conftest.py` para datos y configuraciones reutilizables por varios archivos de prueba. Si un fixture solo le sirve a una prueba en específico, es preferible definirlo directamente dentro de ese archivo `test_*.py`.