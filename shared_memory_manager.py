import json
from multiprocessing import Lock
from multiprocessing import shared_memory as shm


# Definir una clase para manejar la memoria compartida
class SharedMemoryManager:
    def __init__(self):
        self.shared_memory = shm.SharedMemory(create=True, size=1024)
        self.data = {}
        self.read_lock = Lock()
        self.write_lock = Lock()
        # Inicializar la memoria compartida con un diccionario vacío
        self.shared_memory.buf[0:len(json.dumps(self.data))] = json.dumps(self.data).encode()

    def update_result(self, expression, result):
        print("Cadena JSON a almacenar en la memoria compartida:", expression)
        with self.write_lock:  # Adquirir el semáforo antes de actualizar la memoria compartida
            # Cargar los resultados anteriores desde la memoria compartida
            previous_data = self.get_results()
            # Actualizar los resultados con el nuevo resultado
            previous_data[expression] = result
            # Convertir los resultados a cadena JSON
            json_string = json.dumps(previous_data)
            # Escribir la cadena JSON en la memoria compartida
            self.shared_memory.buf[0:len(json_string)] = json_string.encode()

    def get_results(self):
        with self.read_lock:  # Adquirir el semáforo antes de leer la memoria compartida
            # Leer la cadena JSON completa de la memoria compartida
            json_data = self.shared_memory.buf[:].tobytes().decode().strip('\x00')
            # Decodificar la cadena JSON
            return json.loads(json_data)

    def clear_results(self):
        with self.write_lock:  # Adquirir el semáforo antes de limpiar la memoria compartida
            # Llenar la memoria compartida con ceros
            self.shared_memory.buf[:self.shared_memory.size] = b'\x00' * self.shared_memory.size
            # Crear un diccionario vacío
            self.data = {}
            # Escribir el diccionario vacío como JSON en la memoria compartida
            self.shared_memory.buf[0:len(json.dumps(self.data))] = json.dumps(self.data).encode()
