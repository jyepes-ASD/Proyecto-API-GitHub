from typing import List
from datetime import datetime
from fastapi import HTTPException, APIRouter
from github import Github
from token_1 import my_git
from models.repository_model import (
    Repositories,
    RepositoriesStats,
    Repository,
    RepositoryStats
)

repository_router = APIRouter()

user = my_git.get_user()
repos = user.get_repos()
owner = user.login

# Mejorar las 2 funciones:
def get_last_commit_date(repository):
    try:
        commits = repository.get_commits()
        if commits:
            last_commit = commits[0]
            return last_commit.commit.committer.date
        return None
    except Exception as e:
        print(f"Error al obtener commits del repositorio: {str(e)}")
        return None

def get_repository_state(repository):
    try:
        fecha_actual = datetime.now()
        date_last_commit = get_last_commit_date(repository)
        if date_last_commit:
            diferencia_meses = (fecha_actual.year - date_last_commit.year) * 12 + fecha_actual.month - date_last_commit.month
            if diferencia_meses >= 5:
                return "Inactivo"
            return "Activo"
        return "No hay commits"
    except Exception as e:
        print(f"Error al obtener estado del repositorio: {str(e)}")
        return "No hay commits"

def count_state_repositories(repos):
    try:
        active_count = 0
        inactive_count = 0
        for repository in repos:
            state = get_repository_state(repository)
            if state == "Activo":
                active_count += 1
            elif state == "Inactivo":
                inactive_count += 1
            else:
                state == "No hay commits"
        return active_count, inactive_count
    except Exception as e:
        print(f"Error al obtener commits del repositorio: {str(e)}")

# Traer todos los repositorios del GitHub (funciona correctamente):
@repository_router.get("/repositories", response_model=List[Repositories])
def get_repositories():
    try:
        repositories = []
        for repository in repos:
            create_date = repository.created_at
            owner = repository.owner
            last_use_date = get_last_commit_date(repository)

            repositories.append(Repositories(
                owner=owner.login,
                name=repository.name,
                createDate=create_date,
                lastUseDate=last_use_date,
                state=get_repository_state(repository)  # Modificar el estado de un repositorio de GitHub según su último commit
            ))
        return repositories

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener commits del repositorio: {e}")

@repository_router.get("/repositories/statistics/", response_model=RepositoriesStats)
def get_statistics_of_repositories():
    try:
        total_bytes_by_language = {}
        prs_open_count = []
        prs_closed_count = []
        collaborators_count = set()  # Usamos un set para evitar duplicados
        issues_list = []
        dependabot_pr_count = 0  # Inicialización aquí

        total_repos = 0

        for repository in repos:
            total_repos += 1
            # Problemas
            issues = repository.get_issues()
            for iss in issues:
                issues_list.append(iss.title)

            # Total de pulls request abiertos:
            for prs_o in repository.get_pulls(state="open"):
                prs_open_count.append(prs_o)

            # Total de pulls request cerrados
            for prs_c in repository.get_pulls(state="closed"):
                prs_closed_count.append(prs_c)

            # Total de colaboradores de todos los repositorios:
            for collaborator in repository.get_collaborators():
                collaborators_count.add(collaborator.login)  # Usamos un set para contar colaboradores únicos

            # Total de pulls requests del dependabot:
            pull_requests = repository.get_pulls(state="all")
            dependabot_prs = [pr for pr in pull_requests if pr.user.login.startswith("dependabot")]
            dependabot_pr_count += len(dependabot_prs)  # Acumular el conteo

            # Porcentajes de todos los lenguajes de todos los repositorios:
            langs = repository.get_languages()  # Trae todos los lenguajes
            for lang, bytes_count in langs.items():  # Itera guardando
                if lang in total_bytes_by_language:
                    total_bytes_by_language[lang] += bytes_count
                else:
                    total_bytes_by_language[lang] = bytes_count
        total_bytes = sum(total_bytes_by_language.values())
        languages_percentages = {lang: (bytes_count / total_bytes) * 100 for lang, bytes_count in total_bytes_by_language.items()}
        percentages = [f"{lang}: {percentage:.2f}%" for lang, percentage in languages_percentages.items()]

        # Número de repositorios activos e inactivos
        active_e_inactive_count = count_state_repositories(repos)

        return RepositoriesStats(
            repositories=total_repos,
            repositoriesActives=active_e_inactive_count[0],
            repositoriesInactives=active_e_inactive_count[1],
            prsOpen=len(prs_open_count),
            prsClosed=len(prs_closed_count),
            prsDependabot=dependabot_pr_count,
            collaborators=len(collaborators_count),  # Convertimos el set a su tamaño para obtener el número de colaboradores únicos
            issues=len(issues_list),
            percentages_languages=percentages,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas del repositorio: {e}")


@repository_router.get("/repositories/{repo_name}/detail", response_model=List[Repository])
def get_repository_detail(repo_name: str):
    details = []

    total_bytes_by_language = {}
    prs_open_list = []
    prs_closed_list = []
    branches_details = []
    collaborators_list = []
    issues_list = []

    for repository in repos:
        if repository.name == repo_name:
            # Colaboradores lista:
            collaborators = repository.get_collaborators()
            for collaborator in collaborators:
                collaborators_list.append(collaborator.login)

            # Lista de pulls request abiertos y cerrados:
            prs_open = repository.get_pulls(state="open")
            prs_closed = repository.get_pulls(state="closed")

            for pr in prs_open:
                prs_open_list.append(f"El pull #{pr.number}: {pr.title}. Asignado a: {pr.assignee}, fue creado el: {pr.created_at}")

            for pr in prs_closed:
                prs_closed_list.append(f"El pull #{pr.number}: {pr.title}. Asignado a: {pr.assignee}, fue creado el: {pr.created_at}")

            # Ramas
            branches = repository.get_branches()
            for br in branches:
                branches_details.append(f"Nombre de rama: {br.name} --- Propietario: {repository.owner.login}")

            # Problemas
            issues = repository.get_issues()
            for iss in issues:
                name_label_list = []
                for name_label in iss.labels:
                    name_label_list.append(name_label.name)
                issues_details = (f"El problema #{iss.number} Titulo: {iss.title} --- Descripción: {iss.body} --- Tipo: {','.join(name_label_list)}")
                issues_list.append(issues_details)

            # Porcentajes de todos los lenguajes de todos los repositorios:
            langs = repository.get_languages()
            for lang, bytes_count in langs.items():
                if lang in total_bytes_by_language:
                    total_bytes_by_language[lang] += bytes_count
                else:
                    total_bytes_by_language[lang] = bytes_count
            total_bytes = sum(total_bytes_by_language.values())
            languages_percentages = {lang: (bytes_count / total_bytes) * 100 for lang, bytes_count in total_bytes_by_language.items()}
            percentages = [f"{lang}: {percentage:.2f}%" for lang, percentage in languages_percentages.items()]

            details.append(Repository(
                name=repository.name,
                description=repository.description,
                collaborators=collaborators_list,
                prsOpen=prs_open_list,
                prsClosed=prs_closed_list,
                prsDependabot={},  # No se usa Dependabot
                issuesDetails=issues_list,
                branchesDetails=branches_details
            ))
            break

    if not details:
        raise HTTPException(status_code=404, detail=f"El repositorio '{repo_name}', no existe")
    return details

@repository_router.get("/repositories/{repo_name}/detail/statistics/", response_model=RepositoryStats)
def get_statistics_by_detail(repo_name: str):
    total_bytes_by_language = {}
    percentages = []
    dependabot_pr_count = 0
    collaborators_total = 0
    prs_open_total = 0
    prs_closed_total = 0
    issues_total = 0
    branches_total = 0

    for repository in repos:
        if repository.name == repo_name:
            # Total de colaboradores
            collaborators_total = repository.get_collaborators().totalCount

            # Total de pulls request abiertos
            prs_open_total = repository.get_pulls(state="open").totalCount

            # Total de pulls request cerrados
            prs_closed_total = repository.get_pulls(state="closed").totalCount

            # Total de problemas
            issues_total = repository.get_issues().totalCount

            # Total de ramas
            branches_total = repository.get_branches().totalCount

            # Total de pulls requests de dependabot
            pull_requests = repository.get_pulls(state="all")
            dependabot_prs = [pr for pr in pull_requests if pr.user.login.startswith("dependabot")]
            dependabot_pr_count = len(dependabot_prs)

            # Porcentajes de todos los lenguajes del repositorio
            langs = repository.get_languages()
            for lang, bytes_count in langs.items():
                if lang in total_bytes_by_language:
                    total_bytes_by_language[lang] += bytes_count
                else:
                    total_bytes_by_language[lang] = bytes_count
            total_bytes = sum(total_bytes_by_language.values())
            languages_percentages = {lang: (bytes_count / total_bytes) * 100 for lang, bytes_count in total_bytes_by_language.items()}
            percentages = [f"{lang}: {percentage:.2f}%" for lang, percentage in languages_percentages.items()]

            break  # No es necesario seguir iterando si encontramos el repositorio

    return RepositoryStats(
        collaborators=collaborators_total,
        prsOpen=prs_open_total,
        prsClosed=prs_closed_total,
        prsDependabot=dependabot_pr_count,
        issues=issues_total,
        branches=branches_total,
        percentagesLanguages=percentages,
    )
