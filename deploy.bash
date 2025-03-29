#!/bin/bash

# Crear el archivo .env si no existe
if [ ! -f .env ]; then
    touch .env
    echo "ENVIRONMENT=development" >> .env
fi

# Cargar variables de entorno desde el archivo .env
export $(grep -v '^#' .env | xargs)

# Función para encontrar un puerto libre
find_free_port() {
    while true; do
        PORT=$(shuf -i 2000-65000 -n 1)
        if ! lsof -i:$PORT >/dev/null; then
            echo $PORT
            return
        fi
    done
}

# Buscar un puerto libre si no está configurado en .env
if ! grep -q "PORT=" .env; then
    FREE_PORT=$(find_free_port)
    echo "Usando puerto libre: $FREE_PORT"
    echo "PORT=$FREE_PORT" >> .env
else
    FREE_PORT=$(grep "PORT=" .env | cut -d '=' -f2)
    echo "Usando puerto existente del archivo .env: $FREE_PORT"
fi

# Exportar el puerto como variable de entorno global
export PORT=$FREE_PORT

# Construir y ejecutar los servicios con docker-compose
docker-compose up --build -d

# Mostrar los servicios en ejecución y los puertos asignados
docker-compose ps