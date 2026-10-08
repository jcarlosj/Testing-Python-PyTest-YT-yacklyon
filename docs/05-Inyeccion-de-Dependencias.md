# Inyección de Dependencias

La inyección de dependencias (DI) en el contexto de __PyTest__ es el mecanismo mediante el cual el framework suministra automáticamente a cada función de prueba los recursos, configuraciones o datos que necesita (sus dependencias) directamente a través de sus parámetros, en lugar de que la prueba tenga que crearlos, instanciarlos o importarlos explícitamente dentro de su cuerpo.

## Comparación: Sin Inyección vs. Con Inyección de PyTest

### SIN Inyección de Dependencias (acoplamiento directo dentro de la prueba)

La prueba asume la responsabilidad de instanciar, configurar y cerrar todo:

Archivo: `test_calculadora_sin_inyeccion_de_dependencias.py`

```Python
# Define Funcionalidad
class Calculadora:
    def sumar(self, a, b):
        return a + b
    
    def restar(self, a, b):
        return a - b


# Define las pruebas
def test_sumar():
    # 1. Arrange (Preparar)
    numero_1 = 2
    numero_2 = 3

    # 2. Act (Actuar)
    calculadora = Calculadora()
    resultado = calculadora.sumar(numero_1, numero_2)    

    # 3. Assert (Afirmar/Verificar)
    assert resultado == 5


def test_restar():
    # 1. Arrange (Preparar)
    numero_1 = 5
    numero_2 = 3

    # 2. Act (Actuar)
    calculadora = Calculadora()    

    # 3. Assert (Afirmar/Verificar)
    assert calculadora.restar(numero_1, numero_2) == 2
```

Diferencias clave frente al enfoque con inyección

- __Sin parámetros en los tests:__ Las funciones de prueba quedan vacías de argumentos (`def test_sumar():`), ya que no reciben ningún recurso externo provisto por el framework.

- __Duplicación de inicialización (Boilerplate):__ La línea `calculadora = Calculadora()` debe repetirse en cada test que la necesite. Si mañana el constructor de la clase cambia (por ejemplo, a `Calculadora(modo="decimal")`), tendrías que modificar manualmente cada una de las pruebas en lugar de actualizar un solo fixture.

- __Acoplamiento fuerte:__ La prueba queda directamente amarrada a la clase concreta Calculadora, eliminando la posibilidad de intercambiarla de forma transparente por una versión simulada (mock) o preconfigurada.

### CON Inyección de Dependencias usando PyTest

La prueba solo declara qué necesita para trabajar; PyTest se encarga de proveerlo

Archivo: `test_calculadora_con_inyeccion_de_dependencias.py`

```Python
import pytest

# Define Funcionalidad
class Calculadora:
    def sumar(self, a, b):
        return a + b
    
    def restar(self, a, b):
        return a - b


# Fixture: Proveedor de la dependencia
@pytest.fixture
def calculadora():
    return Calculadora()


# Define las pruebas (reciben la dependencia por parámetro)
def test_sumar(calculadora):
    # 1. Arrange (Preparar)
    numero_1 = 2
    numero_2 = 3

    # 2. Act (Actuar) - La instancia ya fue provista por PyTest
    resultado = calculadora.sumar(numero_1, numero_2)

    # 3. Assert (Afirmar/Verificar)
    assert resultado == 5


def test_restar(calculadora):
    # 1. Arrange (Preparar)
    numero_1 = 5
    numero_2 = 3

    # 2. Act (Actuar) y 3. Assert (Afirmar/Verificar)
    assert calculadora.restar(numero_1, numero_2) == 2
```

Cambios aplicados:

- __Extracción del Setup:__ La línea `calculadora = Calculadora()` se retira de ambas funciones y se delega al fixture `@pytest.fixture def calculadora():`.

- __Inyección en la firma:__ Tanto `test_sumar(calculadora)` como `test_restar(calculadora)` reciben el objeto listo para usar a través de sus argumentos.

- __Separación de responsabilidades:__ La etapa de preparación (Arrange) en las pruebas ahora solo se enfoca en los datos de entrada (`numero_1`, `numero_2`), mientras que la instanciación de la herramienta queda centralizada.
