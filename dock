# Imagem base leve com Python 3.11
FROM python:3.11-slim

# Evitar prompts interativos e reduzir logs
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:${PATH}"

# Instalar dependências do sistema mínimas necessárias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        iputils-ping \
        traceroute \
        git \
        openssh-client \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código da aplicação
COPY . .

RUN useradd -m appuser
USER appuser

# Expor a porta usada pela aplicação
EXPOSE 8080

# Comando padrão
CMD ["python", "app.py"]
