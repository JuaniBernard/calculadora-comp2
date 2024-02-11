from queue import Queue
import socket
import threading


# Función que representa la tarea de cada hilo
def calculate_term(term, result_queue):
    # Realizar el cálculo del término y poner el resultado en la cola
    result_queue.put((term, eval(term)))


# Función para separar la expresión en términos
def separate_terms(expression):
    terms = []
    current_term = ''
    balance = 0  # Balance para verificar la corrección de los paréntesis
    last_operator = None  # Último operador

    for char in expression:
        if char in ('+', '-') and balance == 0:
            if last_operator is not None:
                terms.append(last_operator)
                last_operator = None
            if current_term:
                terms.append(current_term.strip())
                current_term = ''
            last_operator = char
        else:
            current_term += char
        if char == '(':
            balance += 1
        elif char == ')':
            balance -= 1

    if last_operator is not None:
        terms.append(last_operator)
    if current_term:
        terms.append(current_term.strip())
    print(terms)
    return terms


# Función para calcular el resultado final combinando los resultados de cada término
def calculate_final_result(terms, results):
    final_result = 0  # Inicializar el resultado final con el primer término
    j = 0
    for i in range(0, len(results)):
        _, result = results[i]
        operator = terms[j]  # Obtener el operador que precede al término
        if operator == '+' or operator != '-':
            final_result += result
        elif operator == '-':
            final_result -= result
        j = j + 2
    return final_result


# Función para manejar solicitudes de clientes
def handle_client(conn, addr):
    print(f"Conexión entrante desde {addr}")
    # Recibe la expresión matemática del cliente
    data = conn.recv(1024).decode()
    expression = data.split("\n")[-1]
    print(expression)

    # Lista para almacenar los hilos
    threads = []

    # Separar la expresión en términos con operadores
    terms = separate_terms(expression)

    # Crear una cola compartida para almacenar los resultados de cada término
    result_queue = Queue()

    # Crear y ejecutar un hilo para cada término
    for term in terms:
        if term == '+' or term == '-':
            pass
        else:
            thread = threading.Thread(target=calculate_term, args=(term, result_queue))
            threads.append(thread)
            thread.start()
            print(threads)
    # Esperar a que todos los hilos completen su ejecución
    for thread in threads:
        thread.join()

    # Recopilar los resultados de cada término
    results = []
    while not result_queue.empty():
        term, result = result_queue.get()
        results.append((term, result))
    print(results)

    # Calcular el resultado final combinando los resultados de cada término
    final_result = calculate_final_result(terms, results)

    # Enviar el resultado de vuelta al cliente
    print(type(final_result))
    print(final_result)
    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nAccess-Control-Allow-Origin: *\r\n\r\n{final_result}"
    conn.sendall(response.encode())

    # Cerrar la conexión
    conn.close()


# Configuración del servidor
HOST = '127.0.0.1'
PORT = 12343

# Crear un socket TCP/IP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Enlace del socket a la dirección y puerto
server_socket.bind((HOST, PORT))

# Escuchar conexiones entrantes
server_socket.listen(5)
print(f"Servidor escuchando en {HOST}:{PORT}")

while True:
    # Esperar por una nueva conexión
    conn, addr = server_socket.accept()
    # Manejar la conexión en un hilo separado
    client_thread = threading.Thread(target=handle_client, args=(conn, addr))
    client_thread.start()
