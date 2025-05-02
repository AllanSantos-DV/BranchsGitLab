# Gerenciador de Branches GitLab

Aplicação desktop para gerenciar branches de projetos no GitLab, permitindo a proteção, mesclagem (merge) e remoção segura de branches, com foco na segurança e usabilidade.

## Funcionalidades

### Autenticação e Projetos
- Login no GitLab com URL da instância, nome de usuário e token de API
- Listagem de projetos disponíveis para o usuário autenticado
- Filtro de projetos para facilitar a localização
- Integração completa com a API do GitLab para operações de gerenciamento

### Gerenciamento de Branches
- Visualização hierárquica de branches em estrutura de árvore
- Branches recolhidas por padrão para facilitar a navegação
- Botões para expandir e recolher todas as branches da árvore
- Seleção múltipla de branches para remoção ou destino de merge
- Proteção de branches contra exclusão acidental e operações destrutivas
- Configuração personalizada de branches protegidas por projeto
- Suporte para branches protegidas pelo GitLab
- Ocultação opcional de branches protegidas na listagem
- Exclusão segura de branches não protegidas
- Opção para excluir branches locais e remotas simultaneamente
- Interface de abas para alternar entre gerenciamento e operações de merge

### Merge de Branches
- Interface dedicada para realizar merges entre branches de forma segura e eficiente
- Seleção de uma branch de origem (source) para o merge
- Seleção múltipla de branches de destino (targets) para o merge
- Verificação automática de conflitos antes do merge
- Detecção inteligente de merges já realizados para evitar operações desnecessárias
- Opção para combinar commits (squash) durante o merge
- Opção para deletar a branch de origem após merges bem-sucedidos
- Exibição detalhada do progresso dos merges
- Relatório final com status de cada operação (sucesso, pulado, erro)
- Atualização automática da lista de branches após operações de merge ou deleção

### Interface Amigável
- Interface gráfica moderna com PyQt6
- Sistema de abas intuitivo para separar funcionalidades de gerenciamento e merge
- Feedback visual durante operações de carregamento, merge e exclusão
- Barras de progresso para acompanhamento de operações em lote
- Filtros para facilitar a localização de branches específicas
- Botões de seleção rápida (selecionar/desmarcar todas)
- Alertas de segurança para operações destrutivas
- Atualização dinâmica das listas de branches em tempo real
- Suporte para temas consistentes entre plataformas (Windows, Linux, macOS)
- Componentes de UI específicos para cada tipo de operação (merge, deleção)

### Segurança
- Validação de conexão segura com o GitLab
- Confirmação de exclusão com listagem de branches afetadas
- Verificação de conflitos antes de operações de merge para evitar problemas
- Visualização aprimorada da lista de branches a serem excluídas com cores alternadas
- Confirmação de segurança que requer rolar a lista completa de branches
- Possibilidade de remover branches individuais da seleção antes da exclusão
- Proteção contra exclusão de branches importantes
- Verificação dupla de branches protegidas antes da exclusão
- Suporte a autenticação com token para maior segurança
- Prevenção automática contra mesclagem de branches protegidas em situações inadequadas

### Integração Local/Remota
- Sincronização com repositórios Git locais
- Verificação de status de branches locais e remotas
- Detecção automática de branches protegidas pelo GitLab
- Suporte a operações em lote tanto em repositórios locais quanto remotos
- Sincronização entre operações de merge no GitLab e status local

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
  │   ├── branches_view.py     # Tela de gerenciamento de branches
  │   ├── merge_branches_view.py  # Tela de merge de branches
  │   └── delete_confirmation_dialog.py # Diálogo de confirmação de exclusão
  │
  ├── controllers/             # Camada de controle e lógica da aplicação
  │   ├── app_controller.py    # Controller principal e coordenação
  │   ├── login_controller.py  # Controller de autenticação
  │   ├── project_controller.py  # Controller de seleção de projetos
  │   ├── branch_controller.py   # Controller de gerenciamento de branches
  │   └── merge_controller.py   # Controller de operações de merge
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

A aplicação oferece dois fluxos principais de operação:

**Fluxo de Gerenciamento de Branches:**
1. **Autenticação (Login)**: O usuário se autentica com suas credenciais do GitLab
2. **Seleção de Projeto**: Lista de projetos disponíveis é carregada para seleção
3. **Configuração de Branches Protegidas**: O usuário configura quais branches devem ser protegidas
4. **Gerenciamento de Branches**: O usuário pode visualizar, filtrar e selecionar branches para diversas operações
5. **Exclusão Segura**: Confirmação e execução da remoção de branches selecionadas, com validação de segurança multi-estágio

**Fluxo de Merge de Branches:**
1. **Autenticação e Seleção de Projeto**: Mesmos passos iniciais do fluxo de gerenciamento
2. **Configuração de Branches Protegidas**: Define quais branches não podem ser modificadas
3. **Acesso à Interface de Merge**: Navegação para a aba de Merge de Branches
4. **Seleção de Branches**: Escolha da branch origem e branches destino para o merge
5. **Configuração de Opções**: Definição de opções como squash e deleção da branch origem
6. **Execução e Monitoramento**: Acompanhamento do processo de merge com feedback detalhado

### Tecnologias Utilizadas

- **Python 3.8+**: Linguagem de programação base
- **PyQt6**: Framework para interface gráfica
- **python-gitlab**: API para comunicação com o GitLab
- **GitPython**: Biblioteca para manipulação de repositórios Git locais
- **Threading**: Processamento assíncrono para operações em lote sem bloquear a interface
- **Signals/Slots**: Comunicação entre componentes da interface
- **Processamento Paralelo**: Execução de múltiplos merges com relatório consolidado

## Requisitos

- Python 3.8 ou superior
- Conexão com internet para acesso ao GitLab
- Credenciais de acesso válidas ao GitLab (com permissão para gerenciar branches)
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

### Gerenciamento Básico

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

4. **Interface Principal**:
   - A interface principal apresenta duas abas: "Gerenciar Branches" e "Merge de Branches"
   - Por padrão, a aba "Gerenciar Branches" é exibida inicialmente

### Gerenciamento de Branches

5. **Visualização e Seleção**:
   - Navegue pela estrutura de árvore de branches (inicialmente recolhida)
   - Use os botões de expandir/recolher para controlar a visualização
   - Selecione as branches que deseja remover
   - Use os filtros para encontrar branches específicas
   - Clique em "Remover Branches Selecionadas"

6. **Confirmação e Exclusão**:
   - Revise a lista de branches a serem removidas
   - Role até o final da lista para habilitar a opção de confirmação
   - Marque a caixa de confirmação indicando que compreende a irreversibilidade da ação
   - Confirme a ação para proceder com a exclusão
   - Acompanhe o progresso da operação

### Merge de Branches

7. **Acesso à Funcionalidade**:
   - Na interface principal, clique na aba "Merge de Branches"

8. **Seleção de Branches**:
   - Selecione a branch de origem (source) no menu suspenso
   - Observe que a branch selecionada como origem é automaticamente removida da lista de destinos
   - Selecione uma ou mais branches de destino (targets) na lista (permite seleção múltipla)

9. **Configuração de Opções**:
   - Opcional: marque "Combinar commits (squash)" para unificar os commits em cada merge
   - Opcional: marque "Deletar branch de origem após merge bem-sucedido" se desejar remover a branch source

10. **Execução e Acompanhamento**:
    - Clique em "Realizar Merge" e confirme a operação na caixa de diálogo
    - Acompanhe o progresso de cada merge na barra de status
    - Visualize o relatório detalhado ao final da operação
    - Se houver branches puladas ou com erro, os detalhes serão exibidos
    - Caso tenha selecionado para deletar a branch source, confirme a exclusão na tela padrão de remoção

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