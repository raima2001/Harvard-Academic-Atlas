FROM python:3.8-slim
RUN apt-get update && \
    apt-get install -y libxml2 libxslt1-dev libz-dev libjpeg-dev zlib1g-dev libssl-dev libffi-dev

RUN useradd -ms /bin/bash app
USER app
WORKDIR /app

USER root
RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY pdf_docx_to_vector.py /app/

RUN mkdir -p /app/data

ENV OPENAI_API_KEY=""
ENV PINECONE_API_KEY=""
ENV PINECONE_ENVIRONMENT=""

CMD ["python", "pdf_docx_to_vector.py"]
