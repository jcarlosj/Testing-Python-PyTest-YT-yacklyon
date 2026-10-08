# Aspectos clave no cubiertos en el ejemplo Con Inyección de Dependencias con PyTest

Aunque el ejemplo muestra la inyección básica (un objeto inyectado en una función), la inyección de dependencias en PyTest abarca varios conceptos avanzados esenciales:

1. __Inyección encadenada (Fixtures que inyectan otros Fixtures)__

    Las dependencias no solo se inyectan en las pruebas; un fixture puede inyectarse dentro de otro para armar estructuras complejas por capas:

    ```Python
    import pytest

    # Define Funcionalidad
    class Calculadora:
        def __init__(self):
            self.config = {}


    # Define Fixtures (Inyección de dependencias)

    @pytest.fixture
    def configuracion_avanzada():
        return {"precision": 4, "modo": "cientifico"}


    @pytest.fixture
    def calculadora_configurada(configuracion_avanzada):
        calc = Calculadora()
        calc.config = configuracion_avanzada
        return calc


    # Define Prueba con patrón AAA
    def test_modo(calculadora_configurada):
        # 1. Arrange (Preparar)
        # El fixture provee la calculadora; aquí definimos el valor esperado.
        modo_esperado = "cientifico"

        # 2. Act (Actuar)
        # Extraemos o ejecutamos la acción que produce el resultado a verificar.
        modo_obtenido = calculadora_configurada.config.get("modo")

        # 3. Assert (Afirmar / Verificar)
        # Validamos que el resultado obtenido coincide con el esperado.
        assert modo_obtenido == modo_esperado
    ```

2. __Ciclo de vida con limpieza (`yield` para Teardown)__

    Tu ejemplo solo construye (return), pero la inyección en PyTest también administra la destrucción limpia del recurso inyectado:

    ```Python
    import pytest

    # 1. Definición de la funcionalidad
    class Calculadora:
        def __init__(self):
            self.config = {}
            self.archivo_abierto = False

        def abrir_archivo_logs(self):
            self.archivo_abierto = True
            print("\n[SETUP] Archivo de bitácora abierto.")

        def cerrar_archivo_logs(self):
            self.archivo_abierto = False
            print("\n[TEARDOWN] Archivo de bitácora cerrado de forma segura.")


    # 2. Fixture 1: Configuración base
    @pytest.fixture
    def configuracion_avanzada():
        return {"precision": 4, "modo": "cientifico"}


    # 3. Fixture 2: Encadenamiento con ciclo de vida completo (Setup + Teardown)
    @pytest.fixture
    def calculadora_con_bitacora(configuracion_avanzada):
        # --- SETUP (Arrange global del fixture) ---
        calc = Calculadora()
        calc.config = configuracion_avanzada
        calc.abrir_archivo_logs()

        yield calc  # Inyecta la instancia lista al test

        # --- TEARDOWN (Limpieza post-test) ---
        calc.cerrar_archivo_logs()


    # 4. Prueba estructurada con AAA
    def test_modo_con_bitacora(calculadora_con_bitacora):
        # Arrange (Preparar)
        modo_esperado = "cientifico"

        # Act (Actuar)
        modo_obtenido = calculadora_con_bitacora.config.get("modo")
        esta_activa_bitacora = calculadora_con_bitacora.archivo_abierto

        # Assert (Afirmar / Verificar)
        assert modo_obtenido == modo_esperado
        assert esta_activa_bitacora is True

        # Nota: No escribes Teardown aquí. Al terminar este bloque,
        # PyTest salta automáticamente a ejecutar 'calc.cerrar_archivo_logs()'.
    ```

3. Control de vida útil (scope)

    Si la instanciación de la dependencia fuera costosa (por ejemplo, conectar una base de datos o compilar un binario), puedes reutilizar la misma instancia inyectada en múltiples tests:

    ```Python
    # Se inyecta la MISMA instancia a todos los tests del módulo sin recrearla
    @pytest.fixture(scope="module")
    def calculadora():
        return Calculadora()
    ```

    Este fragmento encaja cambiando el ciclo de vida (scope) del fixture, lo que altera cómo se gestiona y comparte el recurso entre las pruebas de un mismo archivo `.py` (módulo).

    __¿Qué cambia con scope="module"?__
    1. Comportamiento por defecto `(scope="function")`:
        - Test 1 arranca $\rightarrow$ se crea una `Calculadora` $\rightarrow$ corre Test 1 $\rightarrow$ se descarta.
        - Test 2 arranca $\rightarrow$ se crea otra `Calculadora` nueva $\rightarrow$ corre Test 2 $\rightarrow$ se descarta.
    2. Comportamiento con `scope="module"`:
        - Entra el archivo de pruebas completo $\rightarrow$ se crea una única instancia de `Calculadora`.
        - Test 1 recibe esa instancia y se ejecuta.
        - Test 2 recibe exactamente la misma instancia en memoria (mismo espacio de memoria y estado acumulado).
        - Al terminar el último test del archivo $\rightarrow$ se ejecuta el Teardown (si existiera `yield`).

4. Inyección parametrizada (Generación automática de combinaciones)

    Un fixture puede inyectar múltiples variantes de datos sin necesidad de duplicar el código de prueba:

    ```Python
    @pytest.fixture(params=[
        (1, 2, 3),
        (10, 5, 15),
        (-2, 2, 0)
    ])
    def datos_suma(request):
        return request.param # Inyecta una tupla a la vez

    def test_sumas_multiples(calculadora, datos_suma): # Dos dependencias inyectadas
        a, b, esperado = datos_suma
        assert calculadora.sumar(a, b) == esperado
    ```

    Este fragmento introduce la parametrización de fixtures. En el diseño de pruebas, esto permite resolver un reto común: probar la misma lógica de negocio frente a múltiples juegos de datos sin duplicar funciones de prueba ni escribir bucles for manuales.

    Al combinarse con lo anterior, pytest realiza una inyección compuesta:

    1. Inyecta el servicio/herramienta (la calculadora, que puede tener scope="module" y teardown con yield).
    2. Inyecta dinámicamente cada conjunto de datos del fixture parametrizado (datos_suma).

    Por cada tupla definida en params, pytest genera y ejecuta una prueba unitaria independiente.

## Código completo integrado (Arquitectura completa + AAA)

- Separación de responsabilidades (lógica de negocio vs. pruebas).
- Ciclo de vida y limpieza (scope="module", yield / teardown).
- Inyección de dependencias múltiples (objeto de servicio + datos parametrizados).
- Estructura AAA (Arrange, Act, Assert).

```Python
import pytest


# ==========================================
# 1. Lógica de negocio (SUT: System Under Test)
# ==========================================
class Calculadora:
    def __init__(self):
        self.config = {}
        self.bitacora_activa = False

    def abrir_bitacora(self):
        self.bitacora_activa = True

    def cerrar_bitacora(self):
        self.bitacora_activa = False

    def sumar(self, a, b):
        return a + b


# ==========================================
# 2. Fixtures: Proveedores de dependencias
# ==========================================

# Dependencia de servicio: Se inicializa una sola vez para todo el módulo
@pytest.fixture(scope="module")
def calculadora():
    # --- SETUP ---
    calc = Calculadora()
    calc.config = {"modo": "estándar"}
    calc.abrir_bitacora()

    yield calc  # Inyecta la instancia lista para operar

    # --- TEARDOWN ---
    calc.cerrar_bitacora()


# Dependencia de datos: Parametrizada con 'request'
# 'request' es un fixture interno de pytest que expone el contexto de ejecución
@pytest.fixture(
    params=[
        (1, 2, 3),      # Caso 1: números pequeños
        (10, 5, 15),    # Caso 2: decenas
        (-2, 2, 0),     # Caso 3: números negativos/cero
    ],
    ids=["pequenos", "decenas", "negativo_y_positivo"]  # Etiquetas opcionales para la terminal
)
def datos_suma(request):
    # Entrega una tupla a la vez en cada iteración
    return request.param


# ==========================================
# 3. Prueba unitaria con Inyección Múltiple y AAA
# ==========================================
def test_sumas_multiples(calculadora, datos_suma):
    # 1. Arrange (Preparar)
    # Desempaquetamos los datos provistos por el fixture parametrizado
    operando_a, operando_b, resultado_esperado = datos_suma

    # 2. Act (Actuar)
    # Ejecutamos la operación usando la instancia provista por el fixture calculadora
    resultado_obtenido = calculadora.sumar(operando_a, operando_b)

    # 3. Assert (Afirmar / Verificar)
    assert resultado_obtenido == resultado_esperado
```

### ¿Cómo interactúan el Scope y la Parametrización?

El orden de ejecución exacto que realiza pytest tras bambalinas es el siguiente:
1. Entra al archivo: Ejecuta el Setup de `calculadora` (`abrir_bitacora()`).
2. Ejecución 1 (`test_sumas_multiples[pequenos]`):
    - Inyecta la `calculadora` existente y la tupla `(1, 2, 3)`.
    - Verifica $1 + 2 = 3$.
3. Ejecución 2 (`test_sumas_multiples[decenas]`):
    - Inyecta la misma `calculadora` (no se reconstruye) y la tupla `(10, 5, 15)`.
    - Verifica $10 + 5 = 15$.
4. Ejecución 3 (`test_sumas_multiples[negativo_y_positivo]`):
    - Inyecta la misma `calculadora` y la tupla `(-2, 2, 0)`.
    - Verifica $-2 + 2 = 0$.
5. Sale del archivo: Ejecuta el Teardown de `calculadora` (`cerrar_bitacora()`).

### ¿Por qué este enfoque supera a un bucle `for` dentro del test?
Si hubieras escrito un `for a, b, esperado in lista`: dentro de un único test:
- Si el primer caso falla, el bucle se detiene inmediatamente y nunca sabrías si el caso 2 y el caso 3 funcionaban.
- Con el fixture parametrizado, la terminal reporta 3 pruebas distintas. Si una falla, las otras dos continúan ejecutándose y el reporte de introspección te dirá con precisión milimétrica qué combinación de datos falló.