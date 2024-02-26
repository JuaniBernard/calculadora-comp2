# Proyecto de Computación 2 - Calculadora

Este repositorio contiene una calculadora implementada en Python que aplica hilos, sockets, Docker y además utiliza conceptos de programación paralela como semáforos, memoria compartida, pool de procesos, entre otros. La calculadora recibe una expresión matemática de un cliente desde una interfaz web (desarrollada con HTML/CSS), separa los términos de la expresión en hilos de ejecución y los procesa de forma simultánea para mejorar el rendimiento. Finalmente, se juntan los resultados de cada término para calcular el resultado final. En la interfaz de usuario puede observarse un recuadro, el cual se actualiza periódicamente para mostrar todos los cálculos realizados por otros clientes conectados al mismo tiempo con el servidor de calculadora, estos cálculos son almacenados en una memoria compartida.

![Interfaz de usuario: Calculadora a la izquierda, recuadro con resultados a la derecha](/images/ui-screenshot.png "Interfaz de usuario")

## Instrucciones de uso:

1. Forkear este repositorio para tener su propia versión.

2. Clonar el repositorio forkeado en su máquina local.

3. Navegar a la carpeta del proyecto.

4. Ejecutar la calculadora utilizando Docker:

    ```bash
    docker build -t calculadora .
    docker run -p 12345:12345 calculadora
    ```

5. Abrir el archivo `interface.html` en su navegador web para acceder a la interfaz de la calculadora.

6. Ingresar, tocando los botones, la expresión matemática en el campo de entrada y presionar el botón de calcular **"="** para obtener el resultado.

## Requisitos:

- Docker.
- Navegador web compatible con HTML5.


###### Este trabajo fue desarrollado como proyecto final de Computación 2 (Universidad de Mendoza) por Juan Ignacio Bernard.