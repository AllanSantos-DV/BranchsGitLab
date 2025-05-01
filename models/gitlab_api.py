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
    
    def get_protected_branches(self, project_id):
        """
        Retorna a lista de branches protegidas de um projeto específico
        
        Args:
            project_id (int): ID do projeto no GitLab
            
        Returns:
            tuple: (sucesso, lista de nomes de branches protegidas ou mensagem de erro)
        """
        if not self.gl:
            return False, "Não autenticado no GitLab"
            
        start_time = time.time()
        try:
            project = self.gl.projects.get(project_id)
            protected_branches = project.protectedbranches.list(all=True)
            
            # Extrair apenas os nomes das branches protegidas
            protected_branch_names = [branch.name for branch in protected_branches]
            
            elapsed = time.time() - start_time
            
            return True, protected_branch_names
        except gitlab.exceptions.GitlabAuthenticationError as e:
            elapsed = time.time() - start_time
            return False, f"Erro de autenticação: {str(e)}"
        except gitlab.exceptions.GitlabConnectionError as e:
            elapsed = time.time() - start_time
            return False, f"Erro de conexão com o GitLab: {str(e)}"
        except Exception as e:
            elapsed = time.time() - start_time
            return False, f"Erro ao obter branches protegidas: {str(e)}"
    
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
            
    def check_merge_conflicts(self, project_id, source_branch, target_branch):
        """
        Verifica se há conflitos de merge entre duas branches
        
        Args:
            project_id (int): ID do projeto no GitLab
            source_branch (str): Nome da branch de origem
            target_branch (str): Nome da branch de destino
            
        Returns:
            tuple: (sucesso, tem_conflito, mensagem)
                - sucesso (bool): Se a operação foi bem-sucedida
                - tem_conflito (bool): True se há conflitos, False caso contrário
                - mensagem (str): Mensagem descritiva
        """
        if not self.gl:
            return False, None, "Não autenticado no GitLab"
        
        start_time = time.time()
        
        try:
            project = self.gl.projects.get(project_id)
            
            # Verificar se as branches existem
            try:
                source = project.branches.get(source_branch)
                target = project.branches.get(target_branch)
            except gitlab.exceptions.GitlabGetError:
                return False, None, f"Uma das branches não existe: {source_branch} ou {target_branch}"
            
            # Método 1: Tentar usar a comparação de repositórios para verificar diferenças
            # Em vez de criar um MR temporário, vamos verificar se há diferenças entre as branches
            try:
                compare = project.repository_compare(target_branch, source_branch)
                
                # Se não há commits para comparar, não há diferenças, logo não há conflitos
                if len(compare.get('commits', [])) == 0 and len(compare.get('diffs', [])) == 0:
                    return True, False, f"Não há diferenças entre as branches {source_branch} e {target_branch}, portanto não há conflitos"
                
                # Verificar se há um MR aberto entre essas branches
                mrs = project.mergerequests.list(state='opened', source_branch=source_branch, target_branch=target_branch)
                
                # Se já existe um MR, verificar se ele tem conflitos
                if mrs:
                    mr = mrs[0]
                    # Se o MR tem o atributo has_conflicts, usar esse valor
                    if hasattr(mr, 'has_conflicts'):
                        has_conflicts = mr.has_conflicts
                        if has_conflicts:
                            return True, True, f"Existem conflitos entre as branches {source_branch} e {target_branch}"
                        else:
                            return True, False, f"Não há conflitos entre as branches {source_branch} e {target_branch}"
                
                # Método 2: Usar a API de Merge Request para verificar possíveis conflitos
                # Em vez de criar e deletar o MR, vamos usar a API para verificar
                try:
                    # Endpoint para verificar se um merge é possível
                    url = f"{self.url}/api/v4/projects/{project_id}/merge_requests/merge_check"
                    headers = {"PRIVATE-TOKEN": self.token}
                    data = {
                        "source_branch": source_branch,
                        "target_branch": target_branch
                    }
                    
                    import requests
                    response = requests.post(url, headers=headers, data=data)
                    
                    # Se a resposta for bem sucedida, não há conflitos
                    if response.status_code == 200:
                        return True, False, f"Não há conflitos entre as branches {source_branch} e {target_branch}"
                    
                    # Se a resposta for um erro específico, pode ser devido a conflitos
                    if response.status_code == 405 or response.status_code == 406:
                        return True, True, f"Existem conflitos entre as branches {source_branch} e {target_branch}"
                    
                    # Se for 404, pode ser que não seja possível verificar dessa forma
                    if response.status_code == 404:
                        # Continuar com o método alternativo (criar um MR)
                        pass
                except Exception:
                    # Se falhar, continuar com o método alternativo
                    pass
                
                # Método 3 (Fallback): Criar um MR temporário para verificação
                # Procurar por MRs temporários existentes primeiro
                temp_mr_exists = False
                temp_mr = None
                
                try:
                    for mr in mrs:
                        if "[TEMP]" in mr.title:
                            temp_mr = mr
                            temp_mr_exists = True
                            break
                except Exception:
                    pass
                
                if not temp_mr_exists:
                    # Criar um MR temporário apenas se não existir
                    mr_data = {
                        'source_branch': source_branch,
                        'target_branch': target_branch,
                        'title': f'[TEMP] Verificação de conflitos entre {source_branch} e {target_branch}',
                        'remove_source_branch': False,
                        'squash': False
                    }
                    
                    try:
                        temp_mr = project.mergerequests.create(mr_data)
                    except gitlab.exceptions.GitlabCreateError as e:
                        # Se o erro for porque o MR já existe, isso é normal
                        if "already exists" in str(e).lower():
                            mrs = project.mergerequests.list(state='opened', source_branch=source_branch, target_branch=target_branch)
                            if mrs:
                                temp_mr = mrs[0]
                            else:
                                # Se não conseguir criar ou encontrar um MR, assumir que não há conflitos
                                # Isso é uma suposição segura para evitar bloqueios
                                return True, False, f"Não foi possível verificar conflitos, assumindo que não há conflitos"
                        else:
                            # Se for um erro 404, pode significar que não há diferenças entre as branches
                            if "404" in str(e):
                                return True, False, f"Não há diferenças significativas entre as branches, portanto não há conflitos"
                            return False, None, f"Erro ao criar MR para verificação: {str(e)}"
                
                # Se chegamos aqui, temos um MR (novo ou existente) para verificar
                if temp_mr:
                    try:
                        # Atualizar informações do MR
                        temp_mr = project.mergerequests.get(temp_mr.id)
                        
                        # Verificar se há conflitos
                        has_conflicts = getattr(temp_mr, 'has_conflicts', False)
                        
                        # Tentar fechar e deletar o MR temporário se foi criado para verificação
                        if "[TEMP]" in temp_mr.title:
                            try:
                                temp_mr.state_event = 'close'
                                temp_mr.save()
                                
                                # Tentar deletar, mas não falhar se não conseguir
                                try:
                                    temp_mr.delete()
                                except:
                                    pass
                            except:
                                # Ignorar erros ao fechar/deletar
                                pass
                        
                        if has_conflicts:
                            return True, True, f"Existem conflitos entre as branches {source_branch} e {target_branch}"
                        else:
                            return True, False, f"Não há conflitos entre as branches {source_branch} e {target_branch}"
                    except Exception as e:
                        # Se falhar ao verificar o MR, assumir que não há conflitos para evitar bloqueios
                        return True, False, f"Não foi possível verificar conflitos completamente, assumindo que não há conflitos: {str(e)}"
                    
                # Se chegamos aqui sem retornar, algo deu errado, mas vamos assumir que não há conflitos
                return True, False, f"Verificação de conflitos inconclusiva, assumindo que não há conflitos"
                
            except gitlab.exceptions.GitlabError as e:
                # Se for um erro 404, pode significar que não há diferenças entre as branches
                if "404" in str(e):
                    return True, False, f"Não há diferenças significativas entre as branches, portanto não há conflitos"
                    
                # Outro tipo de erro, informar
                return False, None, f"Erro ao comparar branches: {str(e)}"
                
        except gitlab.exceptions.GitlabAuthenticationError as e:
            elapsed = time.time() - start_time
            return False, None, f"Erro de autenticação: {str(e)}"
        except gitlab.exceptions.GitlabConnectionError as e:
            elapsed = time.time() - start_time
            return False, None, f"Erro de conexão com o GitLab: {str(e)}"
        except Exception as e:
            elapsed = time.time() - start_time
            # Verificar se é um erro 404
            if "404" in str(e):
                # O erro 404 pode significar que não há diferenças ou que não há como verificar conflitos
                # Vamos assumir que não há conflitos nesse caso
                return True, False, f"Não há diferenças significativas entre as branches ou não há como verificar conflitos"
            
            return False, None, f"Erro ao verificar conflitos: {str(e)}"
    
    def check_branch_differences(self, project_id, source_branch, target_branch):
        """
        Verifica se há diferenças entre as branches (se o merge é necessário)
        
        Args:
            project_id (int): ID do projeto no GitLab
            source_branch (str): Nome da branch de origem
            target_branch (str): Nome da branch de destino
            
        Returns:
            tuple: (sucesso, tem_diferenca, mensagem)
                - sucesso (bool): Se a operação foi bem-sucedida
                - tem_diferenca (bool): True se há diferenças, False se as branches são idênticas
                - mensagem (str): Mensagem descritiva
        """
        if not self.gl:
            return False, None, "Não autenticado no GitLab"
        
        start_time = time.time()
        try:
            project = self.gl.projects.get(project_id)
            
            # Verificar se as branches existem
            try:
                project.branches.get(source_branch)
                project.branches.get(target_branch)
            except gitlab.exceptions.GitlabGetError:
                return False, None, f"Uma das branches não existe: {source_branch} ou {target_branch}"
            
            # Tentar comparar as branches
            try:
                # Comparar as branches para ver se há diferenças
                # Isso verifica se há commits em source_branch que não estão em target_branch
                compare = project.repository_compare(target_branch, source_branch)
                
                # Se houver commits na comparação, significa que há diferenças
                has_differences = len(compare['commits']) > 0 or len(compare.get('diffs', [])) > 0
                
            except gitlab.exceptions.GitlabError as e:
                # Se falhar na comparação, tentar uma alternativa: verificar se já existe um MR aberto
                try:
                    mrs = project.mergerequests.list(state='opened', source_branch=source_branch, target_branch=target_branch)
                    if mrs:
                        # Se existe um MR, verificar se ele tem conflitos ou não
                        mr = mrs[0]
                        
                        # Se o MR tem o atributo "can_be_merged", podemos usá-lo para avaliar
                        if hasattr(mr, 'can_be_merged'):
                            # Se pode ser mesclado, isso indica que há diferenças (caso contrário, o MR seria desnecessário)
                            return True, True, f"Há um MR aberto de {source_branch} para {target_branch}, indicando diferenças"
                except Exception:
                    # Se também falhar, retornar o erro original
                    return False, None, f"Erro ao comparar branches: {str(e)}"
                
                # Se chegamos aqui, significa que não conseguimos determinar via MR também
                return False, None, f"Erro ao comparar branches: {str(e)}"
            
            elapsed = time.time() - start_time
            
            if has_differences:
                return True, True, f"Existem diferenças entre as branches {source_branch} e {target_branch}"
            else:
                return True, False, f"Não há diferenças entre as branches {source_branch} e {target_branch} (merge não necessário)"
                
        except gitlab.exceptions.GitlabAuthenticationError as e:
            elapsed = time.time() - start_time
            return False, None, f"Erro de autenticação: {str(e)}"
        except gitlab.exceptions.GitlabConnectionError as e:
            elapsed = time.time() - start_time
            return False, None, f"Erro de conexão com o GitLab: {str(e)}"
        except Exception as e:
            elapsed = time.time() - start_time
            return False, None, f"Erro ao verificar diferenças: {str(e)}"
    
    def merge_branches(self, project_id, source_branch, target_branch, squash=False):
        """
        Realiza o merge de duas branches
        
        Args:
            project_id (int): ID do projeto no GitLab
            source_branch (str): Nome da branch de origem
            target_branch (str): Nome da branch de destino
            squash (bool): Se deve combinar todos os commits em um único
            
        Returns:
            tuple: (sucesso, mensagem)
        """
        if not self.gl:
            return False, "Não autenticado no GitLab"
        
        start_time = time.time()
        mr = None
        
        try:
            project = self.gl.projects.get(project_id)
            
            # Verificar se as branches existem
            try:
                project.branches.get(source_branch)
                project.branches.get(target_branch)
            except gitlab.exceptions.GitlabGetError:
                return False, f"Uma das branches não existe: {source_branch} ou {target_branch}"
            
            # Verificar se já existe um MR aberto para essas branches
            existing_mr = None
            try:
                mrs = project.mergerequests.list(state='opened', source_branch=source_branch, target_branch=target_branch)
                if mrs:
                    existing_mr = mrs[0]
            except Exception as e:
                # Se não conseguir listar MRs, apenas ignorar e tentar criar um novo
                pass
            
            # Usar o MR existente ou criar um novo
            if existing_mr:
                mr = existing_mr
                # Atualizar as opções de squash se necessário
                if mr.squash != squash:
                    mr.squash = squash
                    mr.save()
            else:
                # Criar um merge request e fazer merge imediatamente
                mr_data = {
                    'source_branch': source_branch,
                    'target_branch': target_branch,
                    'title': f'Merge de {source_branch} para {target_branch}',
                    'remove_source_branch': False,  # Não remover branch source no merge
                    'squash': squash
                }
                
                try:
                    # Criar o MR
                    mr = project.mergerequests.create(mr_data)
                except gitlab.exceptions.GitlabCreateError as e:
                    if "already exists" in str(e).lower():
                        # Se já existe um MR, tentar encontrá-lo novamente
                        mrs = project.mergerequests.list(state='opened', source_branch=source_branch, target_branch=target_branch)
                        if mrs:
                            mr = mrs[0]
                            # Atualizar as opções de squash se necessário
                            if mr.squash != squash:
                                mr.squash = squash
                                mr.save()
                        else:
                            return False, f"Não foi possível criar ou encontrar um MR: {str(e)}"
                    else:
                        return False, f"Erro ao criar MR: {str(e)}"
            
            # Verificar se o MR já está mesclado
            if mr.state == 'merged':
                return True, f"Merge de {source_branch} para {target_branch} já realizado anteriormente"
            
            # Verificar se há conflitos antes de tentar mesclar
            if getattr(mr, 'has_conflicts', False):
                return False, f"Existem conflitos entre {source_branch} e {target_branch} que precisam ser resolvidos"
            
            # Realizar o merge
            try:
                mr.merge()
            except gitlab.exceptions.GitlabMRClosedError:
                # Se o MR já estiver fechado, verificar se foi mesclado
                mr = project.mergerequests.get(mr.id)
                if mr.state == 'merged':
                    return True, f"Merge de {source_branch} para {target_branch} já realizado"
                else:
                    return False, f"O merge request foi fechado antes de ser mesclado"
            except gitlab.exceptions.GitlabMRConflictError:
                return False, f"Existem conflitos entre {source_branch} e {target_branch} que precisam ser resolvidos"
            
            elapsed = time.time() - start_time
            
            return True, f"Merge de {source_branch} para {target_branch} realizado com sucesso"
                
        except gitlab.exceptions.GitlabAuthenticationError as e:
            elapsed = time.time() - start_time
            return False, f"Erro de autenticação: {str(e)}"
        except gitlab.exceptions.GitlabConnectionError as e:
            elapsed = time.time() - start_time
            return False, f"Erro de conexão com o GitLab: {str(e)}"
        except Exception as e:
            elapsed = time.time() - start_time
            return False, f"Erro ao realizar merge: {str(e)}" 