# Gerenciador de Branches GitLab

Aplicação para gerenciar branches de múltiplos projetos no GitLab, permitindo a remoção segura de branches não utilizadas.

## Funcionalidades

- Login no GitLab com usuário e token
- Listagem de projetos disponíveis
- Listagem e seleção de branches para remoção
- Proteção para branches especiais (master, staging, integrations, uat, developer)
- Remoção de branches remotas e locais
- Interface moderna e intuitiva

## Estrutura do Projeto

A aplicação segue o padrão de arquitetura MVC (Model-View-Controller):

```
projeto/
  ├── models/               # Camada de dados e lógica de negócio
  │   ├── __init__.py       # Inicialização do pacote
  │   ├── gitlab_api.py     # Comunicação com a API do GitLab
  │   └── git_repo.py       # Operações com repositório Git local
  │
  ├── views/                # Camada de interface gráfica
  │   ├── __init__.py       # Inicialização do pacote
  │   ├── login_view.py     # Tela de login
  │   ├── projects_view.py  # Tela de listagem de projetos
  │   └── branches_view.py  # Tela de gerenciamento de branches
  │
  ├── controllers/          # Camada de controle e lógica da aplicação
  │   ├── __init__.py       # Inicialização do pacote
  │   ├── app_controller.py # Controller principal
  │   ├── login_controller.py    # Controller de login
  │   ├── project_controller.py  # Controller de projetos
  │   └── branch_controller.py   # Controller de branches
  │
  ├── utils/                # Utilitários e constantes
  │   ├── __init__.py       # Inicialização do pacote
  │   └── constants.py      # Constantes da aplicação (branches protegidas, estilos)
  │
  ├── main.py               # Ponto de entrada da aplicação
  └── requirements.txt      # Dependências do projeto
```

### Padrão MVC

- **Models**: Encapsulam a lógica de negócio e o acesso a dados (GitLab API e Git)
- **Views**: Responsáveis apenas pela interface do usuário
- **Controllers**: Conectam os models e views, gerenciando o fluxo da aplicação

## Benefícios da Estrutura

- **Manutenibilidade**: Cada componente tem responsabilidade única
- **Testabilidade**: Componentes podem ser testados isoladamente
- **Extensibilidade**: Facilidade para adicionar novas funcionalidades
- **Legibilidade**: Código organizado e fácil de entender

## Requisitos

- Python 3.8+
- GitPython
- python-gitlab
- PyQt6
- keyring

## Instalação

1. Clone o repositório
2. Instale as dependências:
```
pip install -r requirements.txt
```

## Uso

Execute o arquivo principal:
```
python main.py
```

## Fluxo de Uso

1. Faça login no GitLab usando sua URL, nome de usuário e token de acesso
2. Selecione um projeto da lista de projetos disponíveis
3. Opcionalmente, selecione um repositório Git local
4. Visualize e selecione as branches para remover
5. Confirme a remoção das branches selecionadas

## Notas

As branches protegidas (master, staging, integrations, uat, developer) não podem ser removidas para garantir a segurança do repositório. 