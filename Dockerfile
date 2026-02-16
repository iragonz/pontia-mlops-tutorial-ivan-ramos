FROM python:3.10-slim

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/

# Exponer puerto
EXPOSE 8000

# Variables de entorno por defecto
ENV MODEL_NAME="adult-income"
ENV MODEL_ALIAS="champion"
ENV MLFLOW_TRACKING_URI="http://localhost:5000"

# Comando para ejecutar la API
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]