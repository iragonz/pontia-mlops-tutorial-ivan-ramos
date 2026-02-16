# Proyecto MLOps - Adult Income Prediction

**Autor:** Iván Ramos González

## Descripción del Proyecto

Este proyecto implementa un pipeline completo de MLOps para entrenar, registrar y desplegar un modelo de Machine Learning que predice si una persona gana más de $50K anuales basándose en datos del censo (Adult Income Dataset de UCI).

## Tecnologías Utilizadas

- **Python 3.10** - Lenguaje de programación
- **MLflow** - Tracking de experimentos y registro de modelos
- **FastAPI** - Framework para la API REST
- **Docker** - Containerización de la aplicación
- **GitHub Actions** - CI/CD pipelines
- **Azure Container Instances** - Despliegue en la nube
- **Scikit-learn** - Entrenamiento de modelos ML
- **Prometheus** - Métricas de monitoreo

## Pipelines Implementadas

### 1. Integration Pipeline (`integration.yml`)

**Trigger:** Pull requests a main, workflow_dispatch manual

**Función:** Validación continua del código

**Pasos:**
1. Checkout del código
2. Configuración de Python 3.10
3. Instalación de dependencias desde requirements.txt
4. Ejecución de tests (con continue-on-error)

**Propósito:** Asegurar que los cambios no rompan los tests existentes antes de hacer merge.

### 2. Build Pipeline (`build.yml`)

**Trigger:** Push a main, workflow_dispatch manual

**Función:** Entrenamiento y registro de modelos

**Pasos:**
1. Checkout del código
2. Generación de nombre único para la ejecución
3. Configuración de Python 3.10
4. Instalación de dependencias
5. Descarga del dataset Adult Income desde UCI
6. Entrenamiento del modelo con MLflow tracking
7. Guardado del run_id
8. Ejecución de tests de integración y performance
9. Registro del modelo en MLflow con alias "champion"

**Variables de entorno utilizadas:**
- `MLFLOW_TRACKING_URI` - URL del servidor MLflow
- `AZURE_STORAGE_CONNECTION_STRING` - Conexión a Azure Storage
- `EXPERIMENT_NAME` - Nombre del experimento en MLflow
- `MODEL_NAME` - Nombre del modelo a registrar

**Propósito:** Automatizar el entrenamiento y versionado de modelos.

### 3. Deploy Pipeline (`deploy.yml`)

**Trigger:** workflow_dispatch manual

**Función:** Despliegue de la API en Azure

**Pasos:**
1. Checkout del código
2. Configuración de Docker Buildx
3. Login en Azure Container Registry (ACR)
4. Construcción de imagen Docker con el modelo
5. Push de la imagen a ACR
6. Login en Azure
7. Despliegue en Azure Container Instances
8. Verificación del estado del contenedor
9. Tests de health check y predicción

**Variables y secretos utilizados:**
- Variables: `MODEL_NAME`, `MLFLOW_URL`
- Secretos: `ACR_NAME`, `ACR_USERNAME`, `ACR_PASSWORD`, `AZURE_CREDENTIALS`, `AZURE_RESOURCE_GROUP`

**Propósito:** Desplegar automáticamente la API containerizada en la nube.

## API REST

La API proporciona los siguientes endpoints:

### `GET /`
Health check básico que retorna el estado de la API y si el modelo está cargado.

### `GET /health`
Health check detallado con información del modelo y configuración de MLflow.

### `POST /predict`
Endpoint de predicción que acepta datos de entrada y retorna la predicción del modelo.

**Ejemplo de request:**
```json
{
  "age": 39,
  "workclass": "State-gov",
  "fnlwgt": 77516,
  "education": "Bachelors",
  "education_num": 13,
  "marital_status": "Never-married",
  "occupation": "Adm-clerical",
  "relationship": "Not-in-family",
  "race": "White",
  "sex": "Male",
  "capital_gain": 2174,
  "capital_loss": 0,
  "hours_per_week": 40,
  "native_country": "United-States"
}
```

**Ejemplo de response:**
```json
{
  "prediction": 0,
  "prediction_label": "<=50K",
  "latency_seconds": 0.0234
}
```

### `GET /metrics`
Endpoint de métricas de Prometheus para monitoreo.

## Configuración Local

### Prerrequisitos

- Python 3.10
- Git
- Docker Desktop (opcional)

### Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/iragonz/pontia-mlops-tutorial-ivan-ramos.git
cd pontia-mlops-tutorial-ivan-ramos
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:

Crear archivo `.env` en la raíz:
```
MLFLOW_TRACKING_URI=http://57.151.65.76:5000
AZURE_STORAGE_CONNECTION_STRING=<tu_connection_string>
EXPERIMENT_NAME=ivan-ramos-adult-income
MODEL_NAME=ivan-ramos-adult-income
```

### Ejecutar Entrenamiento Local
```bash
# Descargar datos
python scripts/download_data.py

# Entrenar modelo
python src/main.py

# Registrar modelo
python scripts/register_model.py
```

### Ejecutar API Local
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Acceder a la documentación interactiva en: `http://localhost:8000/docs`

### Ejecutar Tests
```bash
pytest tests/ -v
```

## Configuración de GitHub

### Secrets Configurados

- `AZURE_STORAGE_CONNECTION_STRING` - Conexión a Azure Storage para MLflow
- `AZURE_CREDENTIALS` - Credenciales de Azure para despliegue
- `ACR_USERNAME` - Usuario del Azure Container Registry
- `ACR_PASSWORD` - Password del Azure Container Registry
- `ACR_NAME` - Nombre del Azure Container Registry
- `AZURE_RESOURCE_GROUP` - Grupo de recursos de Azure

### Variables Configuradas

- `MLFLOW_URL` - URL del servidor MLflow
- `EXPERIMENT_NAME` - Nombre del experimento
- `MODEL_NAME` - Nombre del modelo

### Protecciones de Rama (Ruleset)

La rama `main` está protegida con:
- ✅ Restricción de eliminación
- ✅ Bloqueo de force push
- ✅ Requiere que los checks de status pasen
- ✅ Requiere que las ramas estén actualizadas antes del merge

## Flujo de Trabajo

1. **Desarrollo Local**
   - Crear feature branch
   - Desarrollar cambios
   - Ejecutar tests localmente

2. **Pull Request**
   - Crear PR hacia main
   - La pipeline de integración se ejecuta automáticamente
   - Code review (simulado con "Looks good to me")
   - Merge solo si los checks pasan

3. **Build Automático**
   - Al hacer merge a main, se ejecuta build pipeline
   - Descarga datos, entrena modelo, ejecuta tests
   - Registra modelo en MLflow

4. **Deploy Manual**
   - Ejecutar deploy pipeline manualmente desde GitHub Actions
   - Construye imagen Docker
   - Despliega a Azure Container Instances
   - Ejecuta health checks

## Despliegue en Azure

El contenedor se despliega con:
- **CPU:** 1 core
- **Memoria:** 2GB
- **Puerto:** 8000
- **Política de reinicio:** Always
- **DNS:** `model-api-ivan-ramos.eastus.azurecontainer.io`

## Monitoreo

La API expone métricas de Prometheus en `/metrics`:
- `api_requests_total` - Total de requests por método, endpoint y status
- `api_request_latency_seconds` - Latencia de requests
- `predictions_total` - Total de predicciones realizadas

## Dataset

**Fuente:** UCI Machine Learning Repository - Adult Income Dataset

**Descripción:** Datos del censo para predecir si una persona gana más de $50K anuales.

**Features:**
- Demográficos: edad, raza, sexo, país de origen
- Educación: nivel educativo
- Trabajo: clase de trabajo, ocupación, horas semanales
- Económicos: ganancias/pérdidas de capital

**Target:** Binario (<=50K, >50K)

## Modelo

- **Algoritmo:** Random Forest Classifier (Scikit-learn)
- **Métricas evaluadas:** Accuracy, Precision, Recall, F1-Score
- **Tracking:** MLflow para versionado y tracking de experimentos
- **Registro:** Modelo registrado con alias "champion"