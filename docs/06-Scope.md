# Scope

El Scope (alcance o ciclo de vida) define cuándo se crea un fixture y durante cuánto tiempo permanece vivo en memoria antes de ser destruido (teardown).

En PyTest, los scopes (alcances) de las fixtures determinan cuántas veces se ejecuta una fixture y durante uanto tiempo se reutiliza el resultado.

Determina si una dependencia (como la instancia de Calculadora, una conexión a base de datos o un cliente de pruebas) se destruye y vuelve a construir para cada prueba individual, o si se comparte entre varias pruebas para ahorrar tiempo y recursos.

La jerarquía de Scopes en PyTest

PyTest organiza los scopes en una escala que va desde el aislamiento total hasta la máxima reutilización:


| Scope | Cuándo se ejecuta el Setup | Cuándo se ejecuta el Teardown | Nivel de Reutilización |
|:--|:--|:--|:--|
| `function` (por defecto) | Antes de cada función de prueba individual. | Inmediatamente después de terminar la prueba | Ninguna (aislamiento absoluto) |
| `class` | Una vez antes del primer método de una clase de tests (`class Test...`). | Despúes de que concluye el último método de esa clase | Compartido solo dentro de esa clase |
| `module` | Una ves al entrar al archivo `.py` de pruebas. | Al terminar todas las pruebas de ese archivo `.py` | Compartido por todos los test de un archivo. |
| `package` | Una ves al iniciar las pruebas dentro de un paquete/subdirectorio con `__init__.py`. | Al terminar todas las pruebas de ese paquete | Compartido a nivel de subcarpeta. |
| `session` | Una única ves cuando ejecutas el comando `pytest` en la terminal. | Al finalizar absolutamente todas las pruebas de la suite completa | Global para toda la ejecución |

Comparación con el código que veníamos trabajando

Tomando nuestra clase Calculadora:

### Caso 1: `scope="function"` (Comportamiento habitual)

```Python
@pytest.fixture(scope="function") # o simplemente @pytest.fixture
def calc():
    print("\n[SETUP]")
    yield Calculadora()
    print("\n[TEARDOWN]")

def test_uno(calc):
    calc.sumar(2, 2)

def test_dos(calc):
    calc.sumar(3, 3)
```

Orden de ejecución:
1. [SETUP] $\rightarrow$ Corre `test_uno` $\rightarrow$ [TEARDOWN]
2. [SETUP] $\rightarrow$ Corre `test_dos` $\rightarrow$ [TEARDOWN]

    Ventaja: Si `test_uno` altera el estado interno o corrompe datos de la calculadora, test_dos no se ve afectado porque recibe una instancia completamente limpia.

### Caso 2: `scope="module"` (El ejemplo anterior)

```Python
@pytest.fixture(scope="module")
def calc():
    print("\n[SETUP MÓDULO]")
    yield Calculadora()
    print("\n[TEARDOWN MÓDULO]")

def test_uno(calc):
    calc.sumar(2, 2)

def test_dos(calc):
    calc.sumar(3, 3)
```

Orden de ejecución:

1. [SETUP MÓDULO]
2. Corre `test_uno` (recibe la instancia A).
3. Corre `test_dos` (recibe la misma instancia A, con los datos acumulados de `test_uno`).
4. [TEARDOWN MÓDULO]

## Regla fundamental de compatibilidad entre dependencias

Cuando encadenas fixtures (un fixture que inyecta a otro fixture), PyTest impone una regla estricta:

Un fixture de scope más amplio NO puede depender de un fixture de scope más estrecho.

- __Permitido__: Un fixture con `scope="function"` puede consumir uno con scope="module" o scope="session" (una prueba individual puede usar un recurso compartido global).

- __Error (ScopeMismatch)__: Un fixture con `scope="module"` no puede consumir uno con `scope="function"`. PyTest no sabría qué versión de la función inyectarle a un objeto que debe vivir durante todo el archivo.

### Criterio de diseño: ¿Cuál scope elegir?

- Usa function para:
    - Lógica de negocio pura (clases de cálculo, validadores, serializadores).
    - Estados mutables donde una prueba no deba dejar basura a la siguiente.

- Usa module o session para:

    - Conexiones a bases de datos de prueba o creación de esquemas.
    - Levantar un servidor web simulado o un contenedor Docker.
    - Cargar archivos de configuración grandes o modelos de procesamiento pesados que tardan varios segundos en inicializar.