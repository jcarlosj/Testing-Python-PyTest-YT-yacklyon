# Primera Prueba Automática usando PyTest

## Convenciones de Nombres

Una convención de nombres mos permite encontrar automáticamente nuestros archivos y funciones de prueba, para ello todos los nombres de los archivos de prueba integrarán la cadena `test_` en el nombre del archivo de las siguientes formas

- `test_usuario.py` (Forma Tradicional)
- `producto_test.py`
- `_categoria_test.py`

## Estructura AAA

Debemos considerar definir la prueba en partes perfectamente entendibles y claras usando la estructura AAA

1. __Arrange:__ Preparar los datos

    En esta primera etapa se configura el escenario y las condiciones necesarias para la prueba. Aquí es donde inicializas las variables, creas los objetos, configuras los datos de prueba (inputs) y preparas los simulacros (mocks) si son necesarios.

2. __Act:__ Ejecutar la función a probar

    Es la ejecución real del código que se quiere probar. En esta línea (normalmente es una sola línea de código) se invoca al método, función o componente bajo prueba pasándole los datos preparados en el paso anterior y capturando el resultado obtenido.

3. __Assert:__ Verificar el resultado

    Es la fase de comprobación. Aquí se verifica que el resultado obtenido sea igual al resultado esperado. Se utilizan métodos de afirmación (como assertEquals, assertTrue, expect, etc.). Si la afirmación se cumple, la prueba pasa; si no, la prueba falla.

## Directorios (Carpetas) Importantes

### `__pycache__`

Es un directorio (carpeta) que Python crea automáticamente cuando ejecutas archivos importas módulos. Se guardan versiones compiladas de manera temporal de los archivos que tenemos disponibles.

### `.pytest_cache`

Es un directorio (carpeta) oculto que pytest crea automáticamente cuando ejecutas tus pruebas. Se guardará de forma temporal que nos pueda ayudar a recolectar datos de ejecuciones pasadas.

## Definiendo Primera Prueba Automatizada

1. __Se define la funcionalidad__

    Archivo: `validacion.py`

    ```Python
    def es_email_valido( email: str ) -> bool:
        # Se valida que el email tenga el formato basico
        return "@" in email and "." in email and email.endswith(".com")

    # Prueba Manual
    # print(es_email_valido('jcarlosj@gmail.com'))
    ```

2. __Se diseña la prueba__

    Archivo: `test_validacion.py`

    ```Python
    from validacion import es_email_valido

    # Prueba Automatizada
    def test_es_email_valido_con_formato_correcto():
        # 1. Arrange (Preparar)
        email = "usuario@correo.com"

        # 2. Act (Actuar)
        resultado = es_email_valido(email)

        # 3. Assert (Afirmar/Verificar)
        assert resultado == True, "El email deberia ser valido"

    def test_es_email_sin_arroba():
        # 1. Arrange (Preparar)
        email = "usuario.correo.com"

        # 2. Act (Actuar)
        resultado = es_email_valido(email)

        # 3. Assert (Afirmar/Verificar)
        assert resultado == False, "El email deberia ser invalido porque no tiene arroba"
    ```

3. __Se ejecuta la prueba__

    __Opción 1:__ Ejecuta todos las pruebas
    ```bash
    pytest
    ```

    __Opción 2:__ Desglozar la función todas las Pruebas 

    ```bash
    pytest -v
    ```
    
    __Opción 3:__ Ejecuta todas las pruebas de un archivo específico
    ```bash
    pytest -k ./test_validación.py
    ```

    __Opción 4:__ Ejecuta una prueba específica buscandola por una parte del nombre del archivo.
    ```bash
    pytest -k 'sin_arroba'
    ```