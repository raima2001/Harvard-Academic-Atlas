FROM python:3.8-slim

RUN apt-get update && apt-get install -y git

RUN useradd -ms /bin/bash app
USER app
WORKDIR /app
RUN pip install dvc[all]

COPY ../../ /app
CMD ["/bin/bash","-c", "pipenv shell && exec /bin/bash"]
