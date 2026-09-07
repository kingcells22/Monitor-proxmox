# Usa una imagen oficial de Python
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia solo los archivos de dependencias primero
COPY requirements.txt ./

# Instala las dependencias
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Ahora copia el resto del código
COPY . .

# Expone el puerto de la API
EXPOSE 8000

# Comando para iniciar la API
CMD ["uvicorn", "monitor:app", "--host", "0.0.0.0", "--port", "8000"]
