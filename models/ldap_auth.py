"""
Classe para gerenciar a autenticação LDAP/Active Directory
"""
import ldap3
import ssl
import time
from ldap3 import Server, Connection, ALL, NTLM, SIMPLE, SASL, GSSAPI
from ldap3.core.exceptions import LDAPException, LDAPBindError, LDAPSocketOpenError

class LDAPAuth:
    """
    Modelo responsável pela autenticação LDAP/AD e integração com GitLab
    """
    
    def __init__(self, gitlab_api=None):
        """
        Inicializa o autenticador LDAP
        
        Args:
            gitlab_api: Instância do GitLabAPI para integração após autenticação LDAP
        """
        self.gitlab_api = gitlab_api
        self.server = None
        self.connection = None
        self.user_data = None
    
    def authenticate(self, server_url, domain, username, password, use_ssl=True, auth_method='SIMPLE'):
        """
        Autentica o usuário via LDAP/AD
        
        Args:
            server_url (str): URL ou IP do servidor LDAP/AD (ex: ldap.example.com)
            domain (str): Domínio LDAP/AD (ex: example.com)
            username (str): Nome de usuário LDAP
            password (str): Senha LDAP
            use_ssl (bool): Se True, usa SSL para conexão
            auth_method (str): Método de autenticação ('SIMPLE', 'NTLM', 'GSSAPI')
            
        Returns:
            tuple: (sucesso, mensagem)
        """
        start_time = time.time()
        
        # Validação básica dos campos
        if not server_url or not username or not password:
            return False, "Servidor, nome de usuário e senha são obrigatórios"
            
        try:
            # Determinar o método de autenticação
            if auth_method == 'NTLM':
                authentication = NTLM
                user_dn = f"{domain}\\{username}"
            elif auth_method == 'GSSAPI':
                authentication = GSSAPI
                user_dn = username
            else:  # SIMPLE é o padrão
                authentication = SIMPLE
                # Formatar corretamente o DN do usuário
                user_dn = f"uid={username},cn=users,dc={domain.replace('.', ',dc=')}"
            
            # Configurar servidor
            if use_ssl:
                tls_config = ldap3.Tls(validate=ssl.CERT_NONE)
                self.server = Server(server_url, get_info=ALL, use_ssl=True, tls=tls_config)
            else:
                self.server = Server(server_url, get_info=ALL)
            
            # Tentar conexão
            self.connection = Connection(
                self.server,
                user=user_dn,
                password=password,
                authentication=authentication,
                auto_bind=True
            )
            
            # Verificar se autenticou com sucesso
            if self.connection.bound:
                # Buscar informações do usuário
                self._fetch_user_info(username, domain)
                elapsed = time.time() - start_time
                return True, "Autenticação LDAP bem-sucedida"
            else:
                elapsed = time.time() - start_time
                return False, "Falha na autenticação LDAP"
                
        except LDAPBindError as e:
            elapsed = time.time() - start_time
            return False, f"Erro de autenticação LDAP: {str(e)}"
        except LDAPSocketOpenError as e:
            elapsed = time.time() - start_time
            return False, f"Erro de conexão com servidor LDAP: {str(e)}"
        except LDAPException as e:
            elapsed = time.time() - start_time
            return False, f"Erro LDAP: {str(e)}"
        except Exception as e:
            elapsed = time.time() - start_time
            return False, f"Erro ao autenticar via LDAP: {str(e)}"
    
    def _fetch_user_info(self, username, domain):
        """
        Busca informações do usuário após autenticação bem-sucedida
        
        Args:
            username (str): Nome de usuário
            domain (str): Domínio
        """
        if not self.connection or not self.connection.bound:
            return
            
        base_dn = f"dc={domain.replace('.', ',dc=')}"
        search_filter = f"(sAMAccountName={username})"
        
        try:
            # Buscar DN completo e outras informações do usuário
            self.connection.search(
                search_base=base_dn,
                search_filter=search_filter,
                attributes=['cn', 'mail', 'displayName', 'sAMAccountName']
            )
            
            if self.connection.entries:
                self.user_data = self.connection.entries[0]
        except:
            # Se falhar a busca de informações, continuamos com a autenticação básica
            pass
    
    def integrate_with_gitlab(self, gitlab_url):
        """
        Após autenticação LDAP bem-sucedida, integra com o GitLab
        
        Args:
            gitlab_url (str): URL da instância do GitLab
            
        Returns:
            tuple: (sucesso, mensagem)
        """
        if not self.connection or not self.connection.bound:
            return False, "Não autenticado via LDAP"
            
        if not self.gitlab_api:
            return False, "API do GitLab não configurada"
            
        # Tentar obter email do usuário do LDAP, se disponível
        username = ""
        
        if self.user_data and hasattr(self.user_data, 'sAMAccountName'):
            username = self.user_data.sAMAccountName.value
        elif self.user_data and hasattr(self.user_data, 'cn'):
            username = self.user_data.cn.value
            
        # Obter token de acesso do GitLab via LDAP
        # Geralmente isto exige configuração específica no GitLab
        # e potencialmente um endpoint OAuth ou API customizada
        
        # Como isso depende da configuração específica do GitLab,
        # aqui estamos apenas simulando a integração:
        # (Na implementação real, você precisa obter o token corretamente)
        
        # Exemplo simples usando apenas um método customizado que seria implementado:
        # token = self._get_gitlab_token_from_ldap()
        # success, message = self.gitlab_api.login(gitlab_url, token)
        
        # Por enquanto, retornaremos sucesso simulado para desenvolvimento
        return True, f"Integração LDAP-GitLab simulada para usuário {username}"
    
    def close(self):
        """
        Fecha a conexão LDAP
        """
        if self.connection and self.connection.bound:
            self.connection.unbind() 