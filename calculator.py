import threading
from queue import Queue


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
        if operator == '+':
            final_result += result
        elif operator == '-':
            final_result -= result
        j = j + 2
    return final_result


# Expresión matemática
expression = "-4 + (2*4) - (4-2+(4*0))"

# Lista para almacenar los hilos
threads = []

# Crear una cola compartida para almacenar los resultados de cada término
result_queue = Queue()

# Separar la expresión en términos con operadores
terms = separate_terms(expression)

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

print("Final Result:", final_result)
