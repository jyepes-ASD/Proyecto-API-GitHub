from http.client import HTTPException
from typing import List

from fastapi import APIRouter
from token_1 import my_git
from models.user_model import Users
from github import Github

user_router = APIRouter()

user = my_git.get_user()
org = user.get_orgs()

repos = user.get_repos()
owner = user.login


@user_router.get("/usuarios", response_model=List[Users])
def get_users():
    try:
        collaborators_set = set()

        for repository in repos:
            for collaborator in repository.get_collaborators():
                collaborators_set.add(collaborator)


        return Users(
            usernames=collaborators_set
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {e}")



# @user_router.get("/usuarios", response_model=List[Users])
# def get_users():
#     try:
#         accounts = []

#         collaborators_set = set()
#         reposbyuser = []
#         for repository in repos:    
#             for collaborator in repository.get_collaborators():
#                 collaborators_set.add(collaborator)
#             if user.login in repository:
#                 reposbyuser.append(user.get_repos())
#             # for repo in repos:
#             #     if user in repo:
#             #         reposbyuser.append(user.get_repos().totalCount)

#         for collaborator in collaborators_set:
#             accounts.append(Users(
#                 username=collaborator.login,
#                 repositories=reposbyuser
#             ))
        
#         return accounts
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error al obtener repositorios: {e}")
