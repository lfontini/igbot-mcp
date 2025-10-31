# Imagem base leve com Python
FROM python:3.12-slim

# Evitar perguntas interativas
ENV DEBIAN_FRONTEND=noninteractive
# Instalar ferramentas de rede e git
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        iputils-ping \
        traceroute \
        git \
        openssh-client \
        && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements.txt e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código da aplicação
COPY . .

# Porta que o MCP irá rodar
EXPOSE 8080

# Comando para iniciar o MCP
CMD ["python", "app.py"]
