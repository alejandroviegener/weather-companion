# 3.8 python image 
FROM python:3.8 

# Set the working directory to /app
WORKDIR /app

# update pip
RUN pip install --upgrade pip

# Install poetry 1.1.5
RUN pip install poetry==1.1.5

# Copy lock and pyproject to workdir
COPY pyproject.toml poetry.lock Makefile ./

# Install dependencies
RUN poetry install

# Entrypoint is "poetry run make"
ENTRYPOINT ["make"]
#CMD while true; do sleep 30; done;