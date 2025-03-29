#!/bin/bash

# Construir y ejecutar los contenedores
docker-compose up --build -d

# Mostrar los puertos asignados
echo "Puertos asignados:"
docker-compose ps