# Imagem base Ubuntu
FROM ubuntu:22.04

# Evitar prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Atualizar e instalar dependências básicas + Python + pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        iputils-ping \
        traceroute \
        git \
        openssh-client \
        && apt-get clean && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements.txt e instalar dependências Python
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar o restante do código
COPY . .

# Definir usuário não-root (obrigatório para OpenShift)
RUN useradd -m appuser
USER appuser

# Expor a porta
EXPOSE 8080

# Comando para iniciar o MCP
CMD ["python3", "app.py"]
