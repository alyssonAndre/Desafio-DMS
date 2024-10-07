# Desafio

## Descrição
Este projeto foi desenvolvido como parte de um desafio técnico da **DMS Logistics**, onde atuo como estagiário. O objetivo principal do projeto é facilitar a busca por campos de futebol para moradores e turistas que desejam se divertir com amigos e família.

A aplicação web é construída com **Django**, um framework que permite o desenvolvimento rápido e eficiente de aplicações. O **Celery** é utilizado para gerenciamento de tarefas em segundo plano, enquanto o **Redis** atua como broker de mensagens, garantindo comunicação eficiente. **Docker** simplifica a configuração do ambiente, e **PostgreSQL** serve como banco de dados relacional para a persistência dos dados. O **Nginx** é utilizado para gerenciar as requisições HTTP e registrar o HTTPS, proporcionando uma camada adicional de segurança para a aplicação.

## Tecnologias Utilizadas
Este projeto utiliza as seguintes tecnologias e ferramentas:
- **Python**: Linguagem principal utilizada no desenvolvimento da aplicação.
- **Django**: Framework web para desenvolvimento rápido e eficiente.
- **Docker** e **Docker Compose**: Para containerização e orquestração de serviços.
- **PostgreSQL/MySQL**: Banco de dados relacional.
- **Unittest/Pytest**: Frameworks de testes automatizados.
- **Nginx**: O Nginx é utilizado para gerenciar as requisições HTTP e o HTTPS, proporcionando uma camada adicional de segurança para a aplicação.
- **Celery**: Gerenciamento de tarefas assíncronas.
- **Redis**: Broker para filas de mensagens e backend do Celery.

## Índice
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
  - [Usando Docker](#usando-docker)
  - [Sem Docker](#sem-docker)
- [Configuração](#configuração)
- [Uso](#uso)
- [Tarefas com Celery](#tarefas-com-celery)
- [Testes](#testes)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Pré-requisitos
Antes de começar, certifique-se de ter os seguintes itens instalados:
- **Docker** e **Docker Compose** (para rodar com contêineres)
- **Python 3.x**
- **Redis** (se não estiver usando Docker)
- **Celery** (para o gerenciamento de tarefas)

## Configuração

Antes de rodar o projeto, copie o arquivo `.env-example` para criar seu próprio arquivo `.env`:

1. Duplique o arquivo `.env-example`:
   ```bash
   cp .env-example .env


### Dependências Python
- Instale as bibliotecas necessárias listadas no `requirements.txt`.

## Instalação
- Voce precisa ter o docker instalado localmente tanto windows quanto no linux instale aqui https://www.docker.com/

### Usando Docker

1. Clone o repositório:
   ```bash
   git clone https://github.com/maguslim/desafio.git
   cd desafio

2. Suba os contêineres Docker (aplicação, Redis e Celery):

    ```bash
    docker-compose up --build


### Sem Docker

1. Clone o repositório e entre na pasta:

    ```bash
    git clone https://github.com/maguslim/desafio.git
    cd desafio


2. Crie um ambiente virtual e ative-o:
    ```bash
    python3 -m venv venv
    source venv/bin/activate


3. Instale as dependências:
    ```bash
    pip install -r requirements.txt

4. Instale o Redis localmente, conforme a documentação oficial aqui. https://redis.io/


5. Execute o Redis em segundo plano:
    ```bash
    redis-server

6. Inicie o worker do Celery:
    ```bash
    celery -A seu_projeto worker --loglevel=info

7. Execute a aplicação:
    ```bash
    python3 manage.py runserver # para linux/mac
    python manage.py runserver # para windows

