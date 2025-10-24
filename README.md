# Projeto: Sistema de Gestão Acadêmica (FastAPI + MySQL)

Este é um sistema web simples construído com FastAPI (Python) e MySQL para gerenciar alunos, professores, disciplinas e notas de uma escola.

O sistema implementa autenticação de administrador (login/logout) e relatórios protegidos.

**Aviso:** O sistema de autenticação usa MD5 para fins de teste e aprendizado, conforme solicitado. **Não use MD5 em produção.**

## Funcionalidades

- **Autenticação:** Sistema de Login e Logout para administradores.
- **Relatório 1:** Listagem de todos os alunos cadastrados.
- **Relatório 2:** Listagem de todos os professores cadastrados.
- **Relatório 3:** Emissão de Diário de Disciplinas (disciplina, professor, alunos e notas).
- **Relatório 4:** Emissão de Atestado de Matrícula (dados do aluno, disciplinas, notas, média e situação).

## Como Executar o Projeto

### 1. Pré-requisitos

- Python 3.7+
- Um servidor MySQL (como XAMPP, WAMP, MAMP ou Docker)

### 2. Instalação

1.  **Clone o Repositório** (ou crie os arquivos manualmente)

    ```bash
    git clone https://[SEU-LINK-DO-GITHUB-AQUI]
    cd seu_projeto
    ```

2.  **Crie um Ambiente Virtual** (Recomendado)

    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```

3.  **Instale as Dependências**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o Banco de Dados**
    - Abra o seu administrador MySQL (phpMyAdmin, DBeaver, etc.).
    - Execute o script `escola_db.sql` contido neste projeto. Isso criará o banco `escola_db` e todas as tabelas e dados de exemplo.
    - Verifique se as credenciais em `app.py` (DB_CONFIG) batem com as do seu servidor MySQL (usuário `root` e senha em branco, por padrão).

### 3. Executando a Aplicação

Com o ambiente virtual ativado, rode o servidor Uvicorn:

```bash
uvicorn app:app --reload
```
