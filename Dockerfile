FROM python:3.9

WORKDIR /calculadora-comp2

COPY calculator.py .
COPY shared_memory_manager.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 12345

CMD [ "python3", "./calculator.py" ]