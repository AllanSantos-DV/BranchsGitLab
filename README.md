# Gerenciador de Branches GitLab

Aplicação desktop para gerenciar branches de projetos no GitLab, permitindo a proteção e remoção segura de branches, com foco na segurança e usabilidade.

## Funcionalidades

### Autenticação e Projetos
- Login no GitLab com URL da instância, nome de usuário e token de API
- Listagem de projetos disponíveis para o usuário autenticado
- Filtro de projetos para facilitar a localização

### Gerenciamento de Branches
- Visualização hierárquica de branches em estrutura de árvore
- Seleção múltipla de branches para remoção
- Proteção de branches contra exclusão acidental
- Configuração personalizada de branches protegidas por projeto
- Suporte para branches protegidas pelo GitLab
- Ocultação opcional de branches protegidas na listagem
- Exclusão segura de branches não protegidas
- Opção para excluir branches locais e remotas simultaneamente

### Interface Amigável
- Interface gráfica moderna com PyQt6
- Feedback visual durante operações de carregamento e exclusão
- Barra de progresso para acompanhamento de operações em lote
- Filtros para facilitar a localização de branches específicas
- Botões de seleção rápida (selecionar/desmarcar todas)
- Alertas de segurança para operações destrutivas
- Suporte para temas consistentes entre plataformas (Windows, Linux, macOS)

### Segurança
- Validação de conexão segura com o GitLab
- Confirmação de exclusão com listagem de branches afetadas
- Proteção contra exclusão de branches importantes
- Verificação dupla de branches protegidas antes da exclusão
- Suporte a autenticação com token para maior segurança

### Integração Local/Remota
- Sincronização com repositórios Git locais
- Verificação de status de branches locais e remotas
- Detecção automática de branches protegidas pelo GitLab

## Arquitetura e Estrutura do Projeto

A aplicação segue o padrão de arquitetura MVC (Model-View-Controller) para separação clara de responsabilidades:

```
projeto/
  ├── models/                  # Camada de dados e comunicação externa
  │   ├── gitlab_api.py        # Comunicação com a API do GitLab
  │   └── git_repo.py          # Operações com repositório Git local
  │
  ├── views/                   # Camada de interface gráfica
  │   ├── login_view.py        # Tela de login
  │   ├── projects_view.py     # Tela de seleção de projetos
  │   ├── protected_branches_view.py  # Tela de configuração de branches protegidas
  │   └── branches_view.py     # Tela de gerenciamento de branches
  │
  ├── controllers/             # Camada de controle e lógica da aplicação
  │   ├── app_controller.py    # Controller principal e coordenação
  │   ├── login_controller.py  # Controller de autenticação
  │   ├── project_controller.py  # Controller de seleção de projetos
  │   └── branch_controller.py   # Controller de gerenciamento de branches
  │
  ├── utils/                   # Utilitários e constantes
  │   └── constants.py         # Estilos e configurações da aplicação
  │
  ├── resources/               # Recursos da aplicação (imagens, ícones)
  │
  ├── main.py                  # Ponto de entrada da aplicação
  └── requirements.txt         # Dependências do projeto
```

### Fluxo de Operação

1. **Autenticação (Login)**: O usuário se autentica com suas credenciais do GitLab
2. **Seleção de Projeto**: Lista de projetos disponíveis é carregada para seleção
3. **Configuração de Branches Protegidas**: O usuário configura quais branches devem ser protegidas
4. **Gerenciamento de Branches**: Visualização e seleção de branches para possível remoção
5. **Exclusão Segura**: Confirmação e execução da remoção de branches selecionadas

### Tecnologias Utilizadas

- **Python 3.8+**: Linguagem de programação base
- **PyQt6**: Framework para interface gráfica
- **python-gitlab**: API para comunicação com o GitLab
- **GitPython**: Biblioteca para manipulação de repositórios Git locais
- **Threading**: Processamento assíncrono para não bloquear a interface
- **Signals/Slots**: Comunicação entre componentes da interface

## Requisitos

- Python 3.8 ou superior
- Conexão com internet para acesso ao GitLab
- Credenciais de acesso válidas ao GitLab (com permissão para apagar branches)
- Pacotes Python listados em `requirements.txt`

## Instalação

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/gerenciador-branches-gitlab.git
cd gerenciador-branches-gitlab
```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):
```
python -m venv .venv
# No Windows:
.venv\Scripts\activate
# No Linux/MacOS:
source .venv/bin/activate
```

3. Instale as dependências:
```
pip install -r requirements.txt
```

## Execução

Execute o arquivo principal:
```
python main.py
```

## Uso Passo a Passo

1. **Login**:
   - Informe a URL da instância do GitLab (ex: https://gitlab.com)
   - Forneça seu token de acesso pessoal do GitLab (com escopo `api`)
   - Clique em "Conectar"

2. **Seleção de Projeto**:
   - Na lista de projetos, selecione o projeto desejado
   - Opcionalmente, indique o caminho do repositório local
   - Clique em "Gerenciar Branches"

3. **Configuração de Branches Protegidas**:
   - Visualize as branches já protegidas pelo GitLab (não podem ser desprotegidas)
   - Selecione quais branches adicionais deseja proteger
   - Configure se deseja ocultar branches protegidas da visualização
   - Clique em "Confirmar e Continuar"

4. **Gerenciamento de Branches**:
   - Navegue pela estrutura de árvore de branches
   - Selecione as branches que deseja remover
   - Use os filtros para encontrar branches específicas
   - Clique em "Remover Branches Selecionadas"

5. **Confirmação e Exclusão**:
   - Revise a lista de branches a serem removidas
   - Confirme a ação para proceder com a exclusão
   - Acompanhe o progresso da operação

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Enviar pull requests

## Licença

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. 