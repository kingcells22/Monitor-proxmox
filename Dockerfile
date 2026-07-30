# Usa una imagen base de Python
FROM python:3.9-slim-buster

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos al contenedor
COPY requirements.txt .

# Instala las dependencias
RUN pip install -r requirements.txt

# Copia el resto del código fuente al contenedor
COPY . .

# Define el comando para ejecutar la aplicación
CMD ["python", "monitor.py"]