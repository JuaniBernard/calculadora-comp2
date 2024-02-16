import json
from multiprocessing import shared_memory as shm


# Definir una clase para manejar la memoria compartida
class SharedMemoryManager:
    def __init__(self):
        self.shared_memory = shm.SharedMemory(create=True, size=1024)
        self.data = {}

        # Inicializar la memoria compartida con un diccionario vacío
        self.shared_memory.buf[0:len(json.dumps(self.data))] = json.dumps(self.data).encode()

    def update_result(self, expression, result):
        print("Cadena JSON a almacenar en la memoria compartida:", expression)
        # Cargar los resultados anteriores desde la memoria compartida
        previous_data = self.get_results()
        # Actualizar los resultados con el nuevo resultado
        previous_data[expression] = result
        # Convertir los resultados a cadena JSON
        json_string = json.dumps(previous_data)
        # Escribir la cadena JSON en la memoria compartida
        self.shared_memory.buf[0:len(json_string)] = json_string.encode()

    def get_results(self):
        # Leer la cadena JSON completa de la memoria compartida
        json_data = self.shared_memory.buf[:].tobytes().decode().strip('\x00')
        # Decodificar la cadena JSON
        return json.loads(json_data)
