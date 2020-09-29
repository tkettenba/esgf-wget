ARG CONDA_VERSION=4.8.2

FROM continuumio/miniconda3:${CONDA_VERSION} as builder

RUN conda update -n base conda && \
    conda install -c conda-forge -y pip

WORKDIR /wget_api

COPY esgf_wget esgf_wget
COPY requirements.txt .
COPY manage.py .

SHELL ["conda", "run", "-n", "base", "/bin/bash", "-c"]

EXPOSE 8000

RUN pip install -r requirements.txt

ENTRYPOINT ["conda", "run", "-n", "base", "python", "manage.py", "runserver", "0.0.0.0:8000"]
