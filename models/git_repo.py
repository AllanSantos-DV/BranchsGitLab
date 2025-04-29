"""
Classe para gerenciar operações com o repositório Git local
"""
import git

class GitRepo:
    """
    Modelo responsável por operações com o repositório Git local
    """
    
    def __init__(self, repo_path=None):
        """
        Inicializa o gerenciador de repositório Git
        
        Args:
            repo_path (str): Caminho para o repositório Git local
        """
        self.repo_path = repo_path
        self.repo = None
        
        if repo_path:
            self.open(repo_path)
    
    def open(self, repo_path):
        """
        Abre um repositório Git local
        
        Args:
            repo_path (str): Caminho para o repositório Git local
            
        Returns:
            bool: True se o repositório foi aberto com sucesso, False caso contrário
        """
        self.repo_path = repo_path
        
        try:
            self.repo = git.Repo(repo_path)
            return True
        except Exception:
            self.repo = None
            return False
            
    def is_valid(self):
        """
        Verifica se o repositório é válido
        
        Returns:
            bool: True se o repositório é válido, False caso contrário
        """
        return self.repo is not None
        
    def is_initialized(self):
        """
        Verifica se o repositório foi inicializado corretamente
        
        Returns:
            bool: True se o repositório foi inicializado, False caso contrário
        """
        return self.repo is not None
        
    def get_branches(self):
        """
        Retorna a lista de branches locais
        
        Returns:
            tuple: (sucesso, branches ou mensagem de erro)
        """
        if not self.is_valid():
            return False, "Repositório Git inválido"
            
        try:
            branches = []
            for ref in self.repo.refs:
                if isinstance(ref, git.refs.head.Head):
                    branches.append(ref.name)
            return True, branches
        except Exception as e:
            return False, f"Erro ao obter branches locais: {str(e)}"
            
    def delete_branch(self, branch_name):
        """
        Remove uma branch local
        
        Args:
            branch_name (str): Nome da branch a ser removida
            
        Returns:
            tuple: (sucesso, mensagem)
        """
        if not self.is_valid():
            return False, "Repositório Git inválido"
            
        try:
            # Não permitir remover a branch atual
            if self.repo.active_branch.name == branch_name:
                return False, f"Não é possível remover a branch ativa ({branch_name})"
                
            # Encontrar a branch pelo nome
            branch = None
            for ref in self.repo.refs:
                if isinstance(ref, git.refs.head.Head) and ref.name == branch_name:
                    branch = ref
                    break
                    
            if branch is None:
                return False, f"Branch '{branch_name}' não encontrada localmente"
                
            # Remover branch
            self.repo.delete_head(branch, force=True)
            return True, f"Branch local '{branch_name}' removida com sucesso"
        except Exception as e:
            return False, f"Erro ao remover branch local: {str(e)}"
            
    def get_active_branch(self):
        """
        Retorna o nome da branch ativa
        
        Returns:
            str ou None: Nome da branch ativa ou None se não for possível determinar
        """
        if not self.is_valid():
            return None
            
        try:
            return self.repo.active_branch.name
        except Exception:
            return None 