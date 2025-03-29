# filepath: /Users/hexome/Documents/GitHub/proyectosGitPy/app.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Hexome Systems

import os
import jwt
from flask import Flask, request, jsonify
from flasgger import Swagger
from flasgger.utils import swag_from
from dotenv import load_dotenv
from lib import get_directory_structure, create_directories, initialize_git_repository


# Cargar variables de entorno
load_dotenv()

APP_KEY = os.getenv("APP_KEY")

app = Flask(__name__)

# Configuración de Swagger
swagger = Swagger(app)

# Base path for projects
BASE_PATH = "/opt/hexome-systems/projects"

def token_required(f):
    """Decorator para validar el token JWT."""
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return jsonify({"error": "Token JWT requerido."}), 401
        try:
            token = token.split(" ")[1]
            jwt.decode(token, APP_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "El token ha expirado."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido."}), 401
        return f(*args, **kwargs)
    return wrapper

@app.route('/api/structure', methods=['GET'])
@swag_from('swagger/query_together.yml', endpoint='/structure', methods=['GET'])
@token_required
def get_structure():
    """Gets the directory structure."""
    structure = get_directory_structure(BASE_PATH)
    return jsonify(structure)

@app.route('/api/project', methods=['POST'])
@swag_from('swagger/query_together.yml', endpoint='/project', methods=['POST'])
@token_required
def create_project():
    """Creates a new project."""
    data = request.json
    client = data.get('client')
    project = data.get('project')
    repo_type = data.get('repo_type', 'default')  # Default repository type
    branch = data.get('branch', 'main')  # Default branch

    if not client or not project:
        return jsonify({"error": "Client and project are required."}), 400

    project_path = create_directories(client, project, repo_type, branch)
    if project_path:
        initialize_git_repository(project_path)
        return jsonify({"message": "Project created successfully.", "path": project_path}), 201
    else:
        return jsonify({"error": "Failed to create the project."}), 500

@app.route('/api/client/<client>', methods=['GET'])
@swag_from('swagger/query_together.yml', endpoint='/client/{client}', methods=['GET'])
@token_required
def get_client(client):
    """Gets the projects of a specific client."""
    structure = get_directory_structure(BASE_PATH)
    if client in structure:
        return jsonify({client: structure[client]})
    else:
        return jsonify({"error": f"The client '{client}' does not exist."}), 404

@app.route('/api/project/<client>/<project>', methods=['GET'])
@swag_from('swagger/query_together.yml', endpoint='/project/{client}/{project}', methods=['GET'])
@token_required
def get_project(client, project):
    """Gets the details of a specific project."""
    structure = get_directory_structure(BASE_PATH)
    if client in structure and project in structure[client]:
        return jsonify({project: structure[client][project]})
    else:
        return jsonify({"error": f"The project '{project}' does not exist for the client '{client}'."}), 404

if __name__ == '__main__':
    app.run(debug=True)