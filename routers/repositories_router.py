from typing import List
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, APIRouter, Path, Query
from fastapi.responses import HTMLResponse, JSONResponse
from github import Github
from token_1 import my_git
from datetime import datetime, timedelta
from models.repository_model import (
                                         Repositories,
                                         RepositoriesStats,
                                         Repository,
                                         RepositoryStats,)
                                        #  RepositoryDetail,
                                        #  RepositoryDetailStats,
                                        # Stats)


repository_router = APIRouter()


user = my_git.get_user()
repos = user.get_repos()
owner = user.login


# MEJORAR LAS 2 FUNCIONES: 
def get_last_commit_date(repository):
    commits = repository.get_commits()
    if commits.totalCount > 0:
        last_commit = commits[0]
        return last_commit.commit.committer.date
    else:
        return None

def get_repository_state(repository):
    fecha_actual = datetime.now()
    date_last_commit = get_last_commit_date(repository)
    if date_last_commit:
        diferencia_meses = (
            fecha_actual.year - date_last_commit.year
        ) * 12 + fecha_actual.month - date_last_commit.month
        if diferencia_meses >= 5:
            return "Inactivo"
        else:
            return "Activo"
    else:
        return "No hay commits"
    
def count_state_repositories(repos):
    active_count = 0
    inactive_count = 0

    for repository in repos:
        state = get_repository_state(repository)
        if state == "Activo":
            active_count += 1
        elif state == "Inactivo":
            inactive_count += 1
    return active_count, inactive_count


# TRAER TODOS LOS REPOSITORIOS DEL GITHUB (FUNCIONA CORRECTAMENTE):
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
                # MODIFICAR EL ESTADO DE UN REPOSITORIO DE GITHUB SEGUN SU ULTIMO COMMIT:
                state = get_repository_state(repository)                         
            ))
        return repositories
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener repositorios: {e}")
    

# ESTADISTICAS DE LOS REPOSITORIOS:
@repository_router.get("/repositories/statistics/", response_model=RepositoriesStats)
def get_statistics_of_repositories():
    try:
        total_bytes_by_language = {}
        states = []
        prs_open_count = []
        prs_closed_count = []
        collaborators_count = []
        issues_list = []
        for repository in repos:
            
            # Problemas
            issues = repository.get_issues()
            for iss in issues:
                issues_list.append(iss.title)

            # Total de pulls request abiertos:
            for prs_o in repository.get_pulls(state="open"):
                prs_open_count.append(prs_o)

            # Total de pulls requesto cerrados
            for prs_c in repository.get_pulls(state="closed"):
                prs_closed_count.append(prs_c)

            # Total de collaboradores de todos los repositorios:
            for collaborator in repository.get_collaborators():
                collaborators_count.append(collaborator.login)

            # Total de pulls requests del dependabot:
            pull_requests = repository.get_pulls(state="all")
            dependabot_prs = [pr for pr in pull_requests if pr.user.login.startswith("dependabot")]
            dependabot_pr_count = len(dependabot_prs)

            # Porcentajes de todos los lenguajes de todos los repositorios:
            langs = repository.get_languages() # TRAE TODOS LOS LENGUAJES
            for lang, bytes_count in langs.items(): # ITERA GUARDANDO
                if lang in total_bytes_by_language:
                    total_bytes_by_language[lang] += bytes_count
                else:
                    total_bytes_by_language[lang] = bytes_count
            total_bytes = sum(total_bytes_by_language.values())
            languages_percentages = {lang: (bytes_count / total_bytes) * 100 for lang, bytes_count in total_bytes_by_language.items()}
            percentages = [f"{lang}: {percentage:.2f}%" for lang, percentage in languages_percentages.items()]

        # Numero de repositorios activos e inactivos
        active_count = count_state_repositories(repos)
        inactive_count = count_state_repositories(repos)
        # states.append(f"Activos: {active_count[0]} --- Inactivos: {inactive_count[1]}")

        # Numero de colaboradores:
        set_collaborators = set(collaborators_count)    


        return RepositoriesStats(
            repositories=repos.totalCount,
            repositoriesActives=active_count[0],
            repositoriesInactives=active_count[1],
            prsOpen=len(prs_open_count),
            prsClosed=len(prs_closed_count),
            prsDependabot=dependabot_pr_count,  
            collaborators=len(set_collaborators),
            issues=len(issues_list),
            percentages_languages=percentages,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas del repositorio: {e}")



# TRAER DETALLES DEL REPOSITORIO: (Funciona correctamente)
@repository_router.get("/repositories/{repo_name}/detail", response_model=List[Repository])
def get_repository_detail(repo_name: str):
    try:
        details = []

        total_bytes_by_language = {}
        prs_open_list = []
        prs_closed_list = []
        prs_dependabot = {}
        branches_details = []
        collaborators_list = []
        issues_list = []
        for repository in repos:
            if repository.name == repo_name:


                # Colaboradores lista:
                collaborators = repository.get_collaborators()
                for collaborator in collaborators:
                    collaborators_list.append(collaborator.login)


                # Lista de pulls request creados por dependabot filtrados por lenguajes aaaa:
                prs_open = repository.get_pulls(state="open")
                for pr in prs_open:
                    if pr.user.login.startswith("dependabot"):
                        labels = [label.name for label in pr.labels]
                        language = "Others"
                        for label in labels:
                            if label.lower() in repository.get_languages():
                                language = label.lower()
                                break
                        if language not in prs_dependabot:
                            prs_dependabot[language] = []
                        prs_dependabot[language].append({
                            "number": pr.number,
                            "title": pr.title,
                            "state": pr.state,
                            "url": pr.html_url
                })
                

                # Lista de prs abiertos:
                for prs_o in prs_open:
                    prs_open_list.append(f"El pull #{prs_o.number}: {prs_o.title}. Asignado a: {prs_o.assignee}, fue creado el: {prs_o.created_at}")
                

                # Lista de prs cerrados:
                prs_closed = repository.get_pulls(state="closed")
                for prs_c in prs_closed:
                    prs_closed_list.append(f"El pull #{prs_c.number}: {prs_c.title}. Asignado a: {prs_c.assignee}, fue creado el: {prs_c.created_at}")

        
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
                    prsDependabot=prs_dependabot,
                    issuesDetails=issues_list,
                    branchesDetails=branches_details       
                ))
                break

        if not details:
            raise HTTPException(status_code=404, detail=f"El repositorio '{repo_name}', no existe")
        return details
           
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalles del repositorio: {e}")
    




# TRAER ESTADISTICAS DE LOS DETALLES DEL REPOSITORIO: 
@repository_router.get("/repositories/{repo_name}/detail/statistics/", response_model=RepositoryStats)
def get_statistics_by_detail(repo_name: str):
    try:
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
            # falta los teams una lista
            prsOpen=prs_open_total,
            prsClosed=prs_closed_total,
            prsDependabot=dependabot_pr_count,
            issues=issues_total,
            branches=branches_total,
            percentagesLanguages=percentages,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas del repositorio: {e}")
