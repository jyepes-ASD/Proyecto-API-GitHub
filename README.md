# GESTIÓN de la API de GitHub

Este proyecto es para explotar la información de la empresa Grupo ASD junto con la API que proporciona GitHub. Este proyecto tendrá funciones y automatización de tareas para la empresa.

## Tabla de contenido
1. [Descripción](#descripción)
2. [Instalación](#instalación)
3. [Probleas_Comunes](#Probleas_Comunes)

## Descripción

Este proyecto es para hacer funcionalidades y automatizaciones que no tenga el propio GitHub, como por ejemplo:

- Avisar sobre PR abiertos
- Métricas de Commits
- Estadísticas de Repositorios
- Dependabot



## Instalación

Instrucciones paso a paso para configurar y ejecutar el proyecto en un entorno local.

# Clonar el repositorio
```bash
git clone https://github.com/jyepes-ASD/Proyecto-API-GitHub.git
```

Ahora debemos hacer un fichero llamado __token_1.py__ en la carpeta __Proyecto-API-GitHub__ y copia esta sintaxis

```bash

from github import Github

mytoken="TU_TOKEN_VA_AQUI"

my_git = Github(mytoken)

```

Luego crea otro ficherro llamado __.env__ en la carpeta __Proyecto-API-GitHub__ 
```bash

GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
SECRET_KEY=
ORG_NAME=Grupo-ASD
```

# Navegar al directorio del proyecto

En Visual Studio Code dale el comando de __control + ñ__ y ahi te enviara a la consola con la ruta del proyecto 

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
uvicorn app.main:app --reload
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