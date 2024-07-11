from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel





# CLASES PARA TODOS LOS REPOSITORIOS Y SUS ESTADISTICAS:
class Repositories(BaseModel):
    name: str
    owner: str
    state: str
    createDate: Optional[datetime]
    lastUseDate: Optional[datetime]

    
class RepositoriesStats(BaseModel):
    repositories: Optional[int]
    repositoriesActives: Optional[int]
    repositoriesInactives: Optional[int]
    prsOpen: Optional[int]
    prsClosed: Optional[int]
    prsDependabot: Optional[int]
    collaborators: Optional[int]
    issues: Optional[int]
    percentages_languages: Optional[list]
            

# CLASES PARA LOS DETALLES DEL REPOSITORIO Y SUS RESPECTIVAS ESTADISTICAS:
class Repository(BaseModel):
    name: str
    description: Optional[str]
    collaborators: Optional[list]
    prsOpen: Optional[list]
    prsClosed: Optional[list]
    prsDependabot: Optional[dict[str, list[dict[str, str]]]]
    issuesDetails: Optional[list]
    branchesDetails: Optional[list]


class RepositoryStats(BaseModel):
    collaborators: Optional[int]
    prsOpen: Optional[int]
    prsClosed: Optional[int]
    prsDependabot: Optional[int]
    issues: Optional[int]
    branches: Optional[int]
    percentagesLanguages: Optional[list]


