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
from starlette.exceptions import HTTPException as StarletteHTTPException


repository_router = APIRouter()

# Función para obtener los repositorios desde GitHub
def get_repositories_from_github():
    try:
        user = my_git.get_user()
        return user.get_repos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los repositorios: {e}")

# Calcula la última fecha de commit en un repositorio
def get_last_commit_date(repository):
    try:
        commits = repository.get_commits()
        return commits[0].commit.committer.date if commits else None
    except Exception as e:
        print(f"Error al obtener commits del repositorio: {str(e)}")
        return None

# Determina el estado del repositorio basado en la fecha del último commit
def get_repository_state(repository):
    try:
        fecha_actual = datetime.now()
        date_last_commit = get_last_commit_date(repository)
        if date_last_commit:
            diferencia_meses = (fecha_actual.year - date_last_commit.year) * 12 + fecha_actual.month - date_last_commit.month
            return "Inactivo" if diferencia_meses >= 5 else "Activo"
        return "No hay commits"
    except Exception as e:
        print(f"Error al obtener estado del repositorio: {str(e)}")
        return "No hay commits"

# Cuenta los repositorios activos e inactivos
def count_state_repositories(repos):
    active_count = inactive_count = 0
    for repository in repos:
        state = get_repository_state(repository)
        if state == "Activo":
            active_count += 1
        elif state == "Inactivo":
            inactive_count += 1
    return active_count, inactive_count

# Endpoint para obtener los repositorios
@repository_router.get("/repositories", response_model=List[Repositories])
def get_repositories():
    try:
        print("Obteniendo repositorios")  # Depuración
        repos = get_repositories_from_github()  # Obtener repositorios dinámicamente
        repositories = []
        for repository in repos:
            repositories.append(Repositories(
                owner=repository.owner.login,
                name=repository.name,
                createDate=repository.created_at,
                lastUseDate=get_last_commit_date(repository),
                state=get_repository_state(repository)
            ))
        return repositories
    except Exception as e:
        print("Entrando al bloque de excepción")  # Depuración
        raise HTTPException(status_code=500, detail=f"Error al obtener los repositorios: {e}")

@repository_router.get("/repositories/statistics/", response_model=RepositoriesStats)
def get_statistics_of_repositories():
    try:
        print("Obteniendo repositorios desde GitHub")  # Depuración
        repos = get_repositories_from_github()

        total_bytes_by_language = {}
        prs_open_count = []
        prs_closed_count = []
        collaborators_count = set()
        issues_list = []
        dependabot_pr_count = 0
        total_repos = repos.totalCount

        for repository in repos:
            issues = repository.get_issues()
            for issue in issues:
                issues_list.append(issue.title)

            prs_open = repository.get_pulls(state="open")
            prs_open_count.extend(prs_open)

            prs_closed = repository.get_pulls(state="closed")
            prs_closed_count.extend(prs_closed)

            collaborators = repository.get_collaborators()
            for collaborator in collaborators:
                collaborators_count.add(collaborator.login)

            pull_requests = repository.get_pulls(state="all")
            dependabot_prs = [pr for pr in pull_requests if pr.user.login.startswith("dependabot")]
            dependabot_pr_count += len(dependabot_prs)

            langs = repository.get_languages()
            for lang, bytes_count in langs.items():
                if lang in total_bytes_by_language:
                    total_bytes_by_language[lang] += bytes_count
                else:
                    total_bytes_by_language[lang] = bytes_count

        total_bytes = sum(total_bytes_by_language.values())
        languages_percentages = {lang: (bytes_count / total_bytes) * 100 for lang, bytes_count in total_bytes_by_language.items()}
        percentages = [f"{lang}: {percentage:.2f}%" for lang, percentage in languages_percentages.items()]

        active_e_inactive_count = count_state_repositories(repos)

        return RepositoriesStats(
            repositories=total_repos,
            repositoriesActives=active_e_inactive_count[0],
            repositoriesInactives=active_e_inactive_count[1],
            prsOpen=len(prs_open_count),
            prsClosed=len(prs_closed_count),
            prsDependabot=dependabot_pr_count,
            collaborators=len(collaborators_count),
            issues=len(issues_list),
            percentages_languages=percentages,
        )
    except Exception as e:
        print(f"Error en get_statistics_of_repositories: {str(e)}")  # Depuración
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas del repositorio: {e}")

@repository_router.get("/repositories/{repo_name}/detail", response_model=Repository)
def get_repository_detail(repo_name: str):
    try:
        repos = get_repositories_from_github()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los detalles del repositorio: {e}")

    for repository in repos:
        if repository.name == repo_name:
            collaborators_list = [collaborator.login for collaborator in repository.get_collaborators()]

            prs_open_list = [
                f"El pull #{pr.number}: {pr.title}. Asignado a: {pr.assignee.login if pr.assignee else 'N/A'}, fue creado el: {pr.created_at}"
                for pr in repository.get_pulls(state="open")
            ]

            prs_closed_list = [
                f"El pull #{pr.number}: {pr.title}. Asignado a: {pr.assignee.login if pr.assignee else 'N/A'}, fue creado el: {pr.created_at}"
                for pr in repository.get_pulls(state="closed")
            ]

            branches_details = [
                f"Nombre de rama: {br.name} --- Propietario: {repository.owner.login}"
                for br in repository.get_branches()
            ]

            issues_list = [
                f"El problema #{iss.number} Titulo: {iss.title} --- Descripción: {iss.body} --- Tipo: {', '.join([label.name for label in iss.labels])}"
                for iss in repository.get_issues()
            ]

            langs = repository.get_languages()
            total_bytes = sum(langs.values())
            languages_percentages = {lang: (bytes_count / total_bytes) * 100 for lang, bytes_count in langs.items()}
            percentages = [f"{lang}: {percentage:.2f}%" for lang, percentage in languages_percentages.items()]

            return Repository(
                name=repository.name,
                description=repository.description,
                collaborators=collaborators_list,
                prsOpen=prs_open_list,
                prsClosed=prs_closed_list,
                prsDependabot=[],  # No se usa Dependabot
                issuesDetails=issues_list,
                branchesDetails=branches_details,
                languagesPercentage=percentages
            )

    raise HTTPException(status_code=404, detail=f"El repositorio '{repo_name}' no existe")


@repository_router.get("/repositories/{repo_name}/detail/statistics/", response_model=RepositoryStats)
def get_statistics_by_detail(repo_name: str) -> RepositoryStats:
    try:
        repos = get_repositories_from_github()

        found_repo = next((repo for repo in repos if repo.name == repo_name), None)
        if not found_repo:
            raise HTTPException(status_code=404, detail=f"El repositorio '{repo_name}' no existe")
        
        # Procesar el repositorio encontrado (lógica existente para calcular estadísticas)
        total_bytes_by_language = {}
        percentages = []
        dependabot_pr_count = 0
        collaborators_total = found_repo.get_collaborators().totalCount
        prs_open_total = found_repo.get_pulls(state="open").totalCount
        prs_closed_total = found_repo.get_pulls(state="closed").totalCount
        issues_total = found_repo.get_issues().totalCount
        branches_total = found_repo.get_branches().totalCount
        pull_requests = found_repo.get_pulls(state="all")
        dependabot_prs = [pr for pr in pull_requests if pr.user.login.startswith("dependabot")]
        dependabot_pr_count = len(dependabot_prs)

        langs = found_repo.get_languages()
        for lang, bytes_count in langs.items():
            total_bytes_by_language[lang] = total_bytes_by_language.get(lang, 0) + bytes_count

        total_bytes = sum(total_bytes_by_language.values())
        languages_percentages = {lang: (bytes_count / total_bytes) * 100 for lang, bytes_count in total_bytes_by_language.items()}
        percentages = [f"{lang}: {percentage:.2f}%" for lang, percentage in languages_percentages.items()]

        return RepositoryStats(
            collaborators=collaborators_total,
            prsOpen=prs_open_total,
            prsClosed=prs_closed_total,
            prsDependabot=dependabot_pr_count,
            issues=issues_total,
            branches=branches_total,
            percentagesLanguages=percentages,
        )
    except StarletteHTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas detalladas del repositorio: {e}")