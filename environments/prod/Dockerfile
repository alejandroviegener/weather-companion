# 3.8 python image 
FROM python:3.8 

# port to expose
EXPOSE 8000

# Set the working directory to /app
WORKDIR /app

# update pip
RUN pip install --upgrade pip

# Install poetry 1.1.5
RUN pip install poetry==1.1.5

# Copy all files to workdir
COPY . .

# Install dependencies
RUN poetry install

# CMD start fastapi api
CMD ["poetry", "run", "uvicorn", "src.app.api:app", "--host", "0.0.0.0", "--port", "8000"]