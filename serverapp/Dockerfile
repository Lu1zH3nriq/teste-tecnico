FROM python:3.11-slim

# Variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        sqlite3 \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . /app/

# Criar diretórios necessários
RUN mkdir -p /app/data
RUN mkdir -p /app/staticfiles
RUN mkdir -p /app/media

# Coletar arquivos estáticos (incluindo Swagger)
RUN python manage.py collectstatic --noinput --clear

# Tornar o script executável
RUN chmod +x /app/docker-entrypoint.sh

# Expor porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["bash", "/app/docker-entrypoint.sh"]
