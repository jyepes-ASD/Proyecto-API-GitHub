from typing import List, Tuple
from datetime import datetime
from fastapi import HTTPException, APIRouter
from github import Github
from token_1 import my_git
from app.models.repository_model import (
    Repositories,
    RepositoriesStats,
    Repository,
    RepositoryStats
)
from starlette.exceptions import HTTPException as StarletteHTTPException

repository_router = APIRouter()

class RepositoryService:
    def __init__(self):
        self.github_client = my_git

    def get_repositories_from_github(self) -> List:
        '''
        Obtiene los repositorios mediante la api de Github.

        Returns:
            List: Una lista de diccionarios, donde cada diccionario contiene la información de un repositorio.
        '''
        try:
            user = self.github_client.get_user()
            return user.get_repos()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener los repositorios: {e}")

    def get_last_commit_date(self, repository) -> datetime:
        '''
        Obtiene la fecha del ultimo commit realizado en un repositorio.

        Args:
            "repository": Necesita tener un repositorio para obtener la fecha de su ultimo commit.

        Returns:
            Datetime: La fecha del ultimo commit.
        '''
        try:
            commits = repository.get_commits()
            return commits[0].commit.committer.date if commits else None
        except Exception as e:
            print(f"Error al obtener commits del repositorio: {str(e)}")
            return None

    def get_repository_state(self, repository) -> str:
        '''
        Obtiene el estado de un repositorio en base a su ultimo commit.

        Args:
            "repository": Necesita tener un repositorio para obtener el estado del repositorio.
            
        Returns:
            String: El estado de un repositorio (solo en el proyecto).
        '''
        try:
            fecha_actual = datetime.now()
            date_last_commit = self.get_last_commit_date(repository)
            if date_last_commit:
                diferencia_meses = (fecha_actual.year - date_last_commit.year) * 12 + fecha_actual.month - date_last_commit.month
                return "Inactivo" if diferencia_meses >= 5 else "Activo"
            return "No hay commits"
        except Exception as e:
            print(f"Error al obtener estado del repositorio: {str(e)}")
            return "No hay commits"

    def count_state_repositories(self, repos) -> Tuple[int, int]:
        '''
        Cuenta el total de los repositorios con su respectivo estado.

        Args:
            "repos": Necesita tener una lista de repositorios para contar.
            
        Returns:
            Tuple: Una tupla con el conteo de los repositorios.
        '''
        active_count = inactive_count = 0
        for repository in repos:
            state = self.get_repository_state(repository)
            if state == "Activo":
                active_count += 1
            elif state == "Inactivo":
                inactive_count += 1
        return active_count, inactive_count

    def get_repositories(self) -> List[Repositories]:
        '''
        Obtiene todos los repositorios.
            
        Returns:
            List: Retornara una lista de repositorios y a su vez cada repositorio
            mostrara una lista con sus detalles.
        '''
        try:
            repos = self.get_repositories_from_github()
            repositories = []
            for repository in repos:
                repositories.append(Repositories(
                    owner=repository.owner.login,
                    name=repository.name,
                    createDate=repository.created_at,
                    lastUseDate=self.get_last_commit_date(repository),
                    state=self.get_repository_state(repository)
                ))
            return repositories
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener los repositorios: {e}")

    def get_statistics_of_repositories(self) -> RepositoriesStats:
        '''
        Obtiene las estadisticas o conteos totales de todos los repositorios.

        Returns:
            RepositoriesStats: Un modelo que contiene los conteos de los detalles de un repositorio.
        '''
        try:
            repos = self.get_repositories_from_github()
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
                try:
                    collaborators = repository.get_collaborators()
                    for collaborator in collaborators:
                        collaborators_count.add(collaborator.login)
                except Exception as e:
                    print(f"error: {e}")
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

            active_e_inactive_count = self.count_state_repositories(repos)

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
            print(f"Error en get_statistics_of_repositories: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas del repositorio: {e}")

    def get_repository_detail(self, repo_name: str) -> Repository:
        '''
        Muestra los detalles del repositorio.

        Args:
            "repo_name": Necesita tener el nombre del repositorio para acceder a sus detalles.
            
        Returns:
            Repository: Un modelo que contiene los atributos del repositorio.
        '''
        try:
            repos = self.get_repositories_from_github()
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

                issues_list = []
                for iss in repository.get_issues():
                    labels = [label.name for label in iss.labels]
                    issues_list.append(
                        f"El problema #{iss.number} Titulo: {iss.title} --- Descripción: {iss.body} --- Tipo: {', '.join(labels)}"
                    )

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

    def get_statistics_by_detail(self, repo_name: str) -> RepositoryStats:
        '''
        Muestra las estadisticas o conteos de los detalles del repositorio.

        Args:
            "repo_name": Necesita tener el nombre del repositorio, 
            para obtener las estadisticas del repositorio.
            
        Returns:
            RepositoryStats: Un modelo que contiene los atributos del repositorio.
        '''
        try:
            repos = self.get_repositories_from_github()
            found_repo = next((repo for repo in repos if repo.name == repo_name), None)
            if not found_repo:
                raise HTTPException(status_code=404, detail=f"El repositorio '{repo_name}' no existe")

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
        except StarletteHTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas detalladas del repositorio: {e}")


repository_service = RepositoryService()
