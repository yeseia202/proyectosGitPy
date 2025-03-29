# Usa una imagen base de Python Slim
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias del sistema necesarias para compilar paquetes Python y Git
RUN apt-get update && apt-get install -y --no-install-recommends gcc libffi-dev libssl-dev git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia los archivos necesarios al contenedor
COPY . /app

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que Flask se ejecutará
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]