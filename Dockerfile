# Imagen base con Python 3.10.11 (si no está, puedes usar 3.10-slim)
FROM python:3.10.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema requeridas por OpenCV
# libgl1-mesa-glx: para libGL.so.1
# libsm6 y libxrender1: otras dependencias comunes
# libglib2.0-0: para libgthread-2.0.so.0 (el nuevo error)
RUN apt-get update && \
    apt-get install -y \
    libgl1-mesa-glx \
    libsm6 \
    libxrender1 \
    libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/* # Limpia el cache de apt para reducir el tamaño de la imagen

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos de tu aplicación
COPY . .

# Exponer el puerto usado por Flask
EXPOSE 5000

# Ejecutar la aplicación
CMD ["python", "main.py"]