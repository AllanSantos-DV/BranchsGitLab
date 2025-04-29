"""
Classe para gerenciar a comunicação com a API do GitLab
"""
import gitlab
import time

class GitLabAPI:
    """
    Modelo responsável pela comunicação com a API do GitLab
    """
    
    def __init__(self, url=None, token=None):
        """
        Inicializa a API do GitLab
        
        Args:
            url (str): URL da instância do GitLab
            token (str): Token de acesso à API
        """
        self.url = url
        self.token = token
        self.gl = None
        
    def login(self, url=None, token=None):
        """
        Realiza a autenticação com o GitLab
        
        Args:
            url (str): URL da instância do GitLab (opcional se já definido no construtor)
            token (str): Token de acesso à API (opcional se já definido no construtor)
            
        Returns:
            tuple: (sucesso, mensagem)
        """
        if url:
            self.url = url
        if token:
            self.token = token
            
        if not self.url or not self.token:
            return False, "URL e token são obrigatórios"
        
        start_time = time.time()
        try:
            self.gl = gitlab.Gitlab(self.url, private_token=self.token)
            self.gl.auth()
            
            elapsed = time.time() - start_time
            
            # Verificar versão da API para garantir que está conectado
            try:
                version = self.gl.version()
            except Exception as e:
                pass
            
            return True, "Login realizado com sucesso"
        except gitlab.exceptions.GitlabAuthenticationError as e:
            elapsed = time.time() - start_time
            return False, f"Erro de autenticação: {str(e)}"
        except gitlab.exceptions.GitlabConnectionError as e:
            elapsed = time.time() - start_time
            return False, f"Erro de conexão com o GitLab: {str(e)}"
        except Exception as e:
            elapsed = time.time() - start_time
            return False, f"Erro ao autenticar: {str(e)}"
    
    def get_projects(self):
        """
        Retorna a lista de projetos disponíveis para o usuário
        
        Returns:
            tuple: (sucesso, projects ou mensagem de erro)
        """
        if not self.gl:
            return False, "Não autenticado no GitLab"
        
        start_time = time.time()
        try:
            # Obter apenas projetos que o usuário é membro
            # membership=True garante que apenas projetos onde o usuário é membro são incluídos
            # owned=True para obter projetos onde o usuário é dono
            # simple=True para dados básicos do projeto, melhorando a performance
            projects = self.gl.projects.list(
                membership=True,
                per_page=100,
                page=1,
                order_by='name',
                sort='asc',
                simple=True
            )
            
            # Remover projetos arquivados, se houver
            active_projects = [p for p in projects if not hasattr(p, 'archived') or not p.archived]
            
            elapsed = time.time() - start_time
            
            return True, active_projects
        except gitlab.exceptions.GitlabAuthenticationError as e:
            elapsed = time.time() - start_time
            return False, f"Erro de autenticação: {str(e)}"
        except gitlab.exceptions.GitlabConnectionError as e:
            elapsed = time.time() - start_time
            return False, f"Erro de conexão com o GitLab: {str(e)}"
        except Exception as e:
            elapsed = time.time() - start_time
            return False, f"Erro ao obter projetos: {str(e)}"
    
    def get_branches(self, project_id):
        """
        Retorna a lista de branches de um projeto específico
        
        Args:
            project_id (int): ID do projeto no GitLab
            
        Returns:
            tuple: (sucesso, branches ou mensagem de erro)
        """
        if not self.gl:
            return False, "Não autenticado no GitLab"
            
        start_time = time.time()
        try:
            project = self.gl.projects.get(project_id)
            branches = project.branches.list(all=True)
            
            elapsed = time.time() - start_time
            
            return True, branches
        except gitlab.exceptions.GitlabAuthenticationError as e:
            elapsed = time.time() - start_time
            return False, f"Erro de autenticação: {str(e)}"
        except gitlab.exceptions.GitlabConnectionError as e:
            elapsed = time.time() - start_time
            return False, f"Erro de conexão com o GitLab: {str(e)}"
        except Exception as e:
            elapsed = time.time() - start_time
            return False, f"Erro ao obter branches: {str(e)}"
    
    def delete_branch(self, project_id, branch_name):
        """
        Remove uma branch remota no GitLab
        
        Args:
            project_id (int): ID do projeto no GitLab
            branch_name (str): Nome da branch a ser removida
            
        Returns:
            tuple: (sucesso, mensagem)
        """
        if not self.gl:
            return False, "Não autenticado no GitLab"
        
        start_time = time.time()
        try:
            project = self.gl.projects.get(project_id)
            project.branches.delete(branch_name)
            
            elapsed = time.time() - start_time
            
            return True, f"Branch '{branch_name}' removida com sucesso"
        except gitlab.exceptions.GitlabAuthenticationError as e:
            elapsed = time.time() - start_time
            return False, f"Erro de autenticação: {str(e)}"
        except gitlab.exceptions.GitlabConnectionError as e:
            elapsed = time.time() - start_time
            return False, f"Erro de conexão com o GitLab: {str(e)}"
        except Exception as e:
            elapsed = time.time() - start_time
            return False, f"Erro ao remover branch: {str(e)}" 