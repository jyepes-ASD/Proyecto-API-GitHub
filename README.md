# GESTIÓN de la API de GitHub

Este proyecto es para explotar la información de la empresa Grupo ASD junto con la API que proporciona GitHub. Este proyecto tendrá funciones y automatización de tareas para la empresa.

## Tabla de contenido
1. [Descripción](#descripción)
2. [Uso](#uso)
3. [Instalación](#instalación)
4. [Probleas_Comunes](#Probleas_Comunes)

## Descripción

Este proyecto es para hacer funcionalidades y automatizaciones que no tenga el propio GitHub, como por ejemplo:

- Avisar sobre PR abiertos
- Métricas de Commits
- Estadísticas de Repositorios
- Dependabot

## Uso

Primero debeos hacer un fichero llamado token_1.py en la carpeta PROYECTO y copia esta sintaxis

```bash

from github import Github

mytoken="TU_TOKEN_VA_AQUI"

my_git = Github(mytoken)

```

Luego crea otro ficherro llamado .env en la carpeta PROYECTO
```bash

GITHUB_CLIENT_ID=Ov23li3cAP3apdW0y0qy
GITHUB_CLIENT_SECRET=d73e1932b2f104d07e9f26ec1672076ebcfbdbdf
SECRET_KEY=Colombia2024*

```

## Instalación

Instrucciones paso a paso para configurar y ejecutar el proyecto en un entorno local.

# Clonar el repositorio
```bash
git clone https://github.com/jyepes-ASD/Proyecto-API-GitHub.git
```

# Navegar al directorio del proyecto

```bash
cd Proyecto-API-GitHub
```

# Instalar el entorno virtual
```bash
python -m venv env
```

# Activar el entorno virtual
```bash
.\env\Scripts\activate  # Windows
```

# Instalar dependencias
```bash
pip install -r requirements.txt
```

# Ejecutar la aplicación
```bash
uvicorn main:app --reload
```

## Probleas_Comunes

Si al momento de activar el entorno virtual te sale erro prubea este comado primero y depues ejecuta la activacion 

° Windows

```bash
Set-ExecutionPolicy RemoteSigned -Scope Process
.\env\Scripts\activate 
```
y si no te deja instalar las dependecias puedes usar esto 

```bash
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
```