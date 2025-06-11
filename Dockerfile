# Imagen base con Python 3.10.11 (si no está, puedes usar 3.10-slim)
FROM python:3.10.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos
COPY . .

# Exponer el puerto usado por Flask
EXPOSE 5000

# Ejecutar la aplicación
CMD ["python", "main.py"]
