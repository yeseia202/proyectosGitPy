# Usa una imagen base de Python Alpine
FROM python:3.9-alpine

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias del sistema necesarias para compilar paquetes Python
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

# Copia los archivos necesarios al contenedor
COPY . /app

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que Flask se ejecutará
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]