# GESTIÓN de la API de GitHub

Este proyecto es para explotar la información de la empresa Grupo ASD junto con la API que proporciona GitHub. Este proyecto tendrá funciones y automatización de tareas para la empresa.

## Tabla de contenido
1. [Descripción](#descripción)
2. [Instalación](#instalación)

## Descripción

Este proyecto es para hacer funcionalidades y automatizaciones que no tenga el propio GitHub, como por ejemplo:

- Avisar sobre PR abiertos
- Métricas de Commits
- Estadísticas de Repositorios
- Dependabot

## Instalación

Instrucciones paso a paso para configurar y ejecutar el proyecto en un entorno local.

```bash
# Clonar el repositorio
git clone https://github.com/jyepes-ASD/Proyecto-API-GitHub.git

# Navegar al directorio del proyecto
cd Proyecto-API-GitHub

# Instalar el entorno virtual
python -m venv env

# Activar el entorno virtual
.\env\Scripts\activate  # Windows


# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
uvicorn main:app --reload
