# UniTasker 🎓

> 🚀 Plataforma web de freelance e voluntariado exclusiva para estudantes da Uniso. Um ecossistema para ganhar experiência, construir portfólio e colaborar.

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0-black?logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue?logo=postgresql)

---

### Tabela de Conteúdos
1. [Sobre o Projeto](#-sobre-o-projeto)
2. [Features](#-features)
3. [Tecnologias Utilizadas](#-tecnologias-utilizadas)
4. [Arquitetura](#️-arquitetura)
5. [Estrutura de Dados](#-estrutura-de-dados)
6. [Telas e Protótipos](#-telas-e-protótipos)
7. [Começando](#-começando)
8. [Autores](#-autores)

---

## 📜 Sobre o Projeto

O **UniTasker** nasceu da observação de que, dentro da Universidade de Sorocaba, existe um vasto potencial de colaboração inexplorado. O projeto visa resolver a dificuldade de conexão entre alunos de diferentes cursos, criando um ecossistema exclusivo onde estudantes podem:

* **Solicitar serviços** para seus projetos acadêmicos e pessoais.
* **Oferecer suas habilidades**, ganhando experiência prática e construindo um portfólio.
* **Promover o networking** e a troca de conhecimentos de forma simples e segura.

O foco principal do projeto é atuar como uma ferramenta para a **coleta e análise de dados** sobre as dinâmicas de colaboração na comunidade, alinhado aos **Objetivos de Desenvolvimento Sustentável (ODS)** 4 (Educação de Qualidade) e 8 (Trabalho Decente e Crescimento Econômico).

## ✨ Features

-   **👤 Conta de Usuário Unificada:** Um único perfil para atuar como cliente ou prestador de serviço.
-   **🎨 Perfil e Portfólio:** Área personalizável com descrição, habilidades e galeria de trabalhos anteriores.
-   **🔐 Segurança:** Senhas armazenadas com criptografia (Hashing com Bcrypt) para garantir a segurança dos dados.
-   **📢 Cadastro de Serviços:** Ferramenta para prestadores criarem e gerenciarem anúncios.
-   **💬 Chat Integrado:** Canal de comunicação direta entre os usuários.
-   **⭐ Sistema de Avaliação Mútua:** Clientes e prestadores podem deixar avaliações públicas após a conclusão de um trabalho.
-   **📊 Dashboard Administrativo:** Painel para administradores acompanharem as métricas de uso da plataforma.

## 🚀 Tecnologias Utilizadas

| Tecnologia | Finalidade |
| :--- | :--- |
| **Python (Flask)** | Backend e lógica da aplicação|
| **PostgreSQL** | Banco de dados relacional |
| **SQLAlchemy** | ORM para interação com o banco de dados |
| **HTML, CSS, JS** | Frontend e interface do usuário |
| **Jinja2** | Renderização de templates no servidor |
| **Figma** | Design e prototipagem das telas |
| **Git/GitHub** | Controle de versão |
| **Power BI / Excel** | Análise de dados e visualização no Dashboard |

## 🏛️ Arquitetura

A aplicação adota o padrão de arquitetura **MVC (Model-View-Controller)** para garantir um código organizado, manutenível e escalável.

-   **Model:** Camada de dados, gerenciada pelo SQLAlchemy, que mapeia as tabelas do PostgreSQL para objetos Python.
-   **View:** Camada de apresentação, composta por templates HTML renderizados pelo Jinja2.
-   **Controller:** O Flask gerencia as requisições HTTP, orquestrando a lógica e a interação entre o Model e a View.

A estrutura de pastas do projeto reflete essa separação:

UNITASKER/

├── controllers/      # Lógica e rotas (Controller)

├── models/           # Definição dos dados (Model)

├── views/            # Templates HTML (View)

├── static/           # Arquivos CSS, JS e imagens

├── .env              # Variáveis de ambiente (credenciais)

├── app.py            # Ponto de entrada da aplicação

├── config.py         # Configurações

└── requirements.txt  # Dependências do projeto

## 📊 Estrutura de Dados

A modelagem dos dados foi definida em um Diagrama de Entidade-Relacionamento (DER), com as entidades centrais **Usuario**, **Serviço** e **Avaliação**.

![Diagrama de Entidade-Relacionamento](static/Diagrama%20Estrutura%20de%20dados.png)

## 🎨 Telas e Protótipos

As telas essenciais da plataforma foram prototipadas no Figma, estabelecendo a identidade visual e a experiência do usuário.

![Protótipo das Telas de Registro e Login](static/Registro%20e%20Login%20-%20Prototipo.png)
![Protótipo da Tela Inicial](static/Tela%20inicial%20-%20Prototipo.png)
![Área do usuário](static/Área%20do%20usuário%20-%20Prototipo.png)

## 🏁 Começando

Siga estas instruções para configurar o ambiente de desenvolvimento localmente.

### Pré-requisitos

-   Python 3.9+
-   pip
-   Git
-   PostgreSQL

### Instalação

1.  **Clone o repositório:**
    ```sh
    git clone [https://github.com/seu-usuario/unitasker.git](https://github.com/seu-usuario/unitasker.git)
    cd unitasker
    ```

2.  **Crie e ative um ambiente virtual:**
    ```sh
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    -   Renomeie o arquivo `.env.example` para `.env`.
    -   Preencha as variáveis com suas credenciais do banco de dados e outras chaves.

5.  **Inicialize o banco de dados:**
    *(Adicione aqui o comando para criar as tabelas, ex: `flask db init` se estiver usando Flask-Migrate)*

### Rodando a Aplicação

Para iniciar o servidor de desenvolvimento, execute:
```sh
flask run
