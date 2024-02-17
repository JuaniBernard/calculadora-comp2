import json
import multiprocessing
from queue import Queue
from shared_memory_manager import SharedMemoryManager
import socket
import threading
import time

result_queue_semaphore = threading.Semaphore()

shared_memory_manager = SharedMemoryManager()


# Función que representa la tarea de cada hilo
def calculate_term(term, result_queue):
    # Adquirir el semáforo antes de poner el resultado en la cola
    print(f"Hilo {threading.current_thread().name} adquiriendo semáforo")
    result_queue_semaphore.acquire()
    print(f"Hilo {threading.current_thread().name} semáforo adquirido")
    # Realizar el cálculo del término y poner el resultado en la cola
    result_queue.put((term, eval(term)))
    # Liberar el semáforo después de poner el resultado en la cola
    result_queue_semaphore.release()
    print(f"Hilo {threading.current_thread().name} semáforo liberado")
    # Simular cálculo intensivo
    time.sleep(6)


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
def handle_client(conn, addr, request):
    parent_process = multiprocessing.current_process().name
    print(f"Proceso {parent_process} para conexión desde {addr}")
    # Recibe la expresión matemática del cliente
    expression = request.split("\n")[-1]
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

    # Actualizar los resultados en la memoria compartida
    shared_memory_manager.update_result(expression, final_result)

    # Enviar el resultado de vuelta al cliente
    print(type(final_result))
    print(final_result)
    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nAccess-Control-Allow-Origin: *\r\n\r\n{final_result}"
    conn.sendall(response.encode())

    # Cerrar la conexión
    conn.close()


# Función para manejar conexiones entrantes en un proceso
def accept_connections(server_socket):
    while True:
        # Esperar por una nueva conexión
        conn, addr = server_socket.accept()
        # Decodificar la solicitud HTTP
        request = conn.recv(1024).decode()
        # Verificar el tipo de solicitud
        if "GET /results HTTP/1.1" in request:
            # Si la solicitud es para los resultados, se maneja así
            handle_results_request(conn)
        elif "POST / HTTP/1.1" in request:
            # Si la solicitud es calcular una expresión matemática, se maneja así
            handle_client(conn, addr, request)


# Función para manejar solicitudes de resultados de memoria compartida
def handle_results_request(conn):
    # Obtener los resultados de la memoria compartida
    results = shared_memory_manager.get_results()
    # Convertir los resultados a formato JSON
    json_results = json.dumps(results)
    # Enviar los resultados al cliente
    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{json_results}"
    conn.sendall(response.encode())
    # Cerrar la conexión
    conn.close()


# Función para manejar las actualizaciones de la memoria compartida
def shared_memory_updater():
    while True:
        time.sleep(5)
        results = shared_memory_manager.get_results()
        print("Resultados en memoria compartida:", results)


# Iniciar el hilo de actualización de memoria compartida
shared_memory_updater_thread = threading.Thread(target=shared_memory_updater)
shared_memory_updater_thread.start()

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

# Crear un pool de procesos para representar conexiones al servidor
num_processes = 4
with multiprocessing.Pool(processes=num_processes) as pool:
    # Cada proceso en el pool ejecuta la función accept_connections
    pool.map(accept_connections, [server_socket] * num_processes)
