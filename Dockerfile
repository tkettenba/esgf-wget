FROM debian:latest as builder

WORKDIR /wgetApi

RUN useradd -ms /bin/bash apache
RUN usermod -a -G apache apache

RUN apt-get -qq update
RUN apt-get install --yes apache2 apache2-dev

COPY esgf_wget esgf_wget
COPY requirements.txt .
COPY manage.py .

RUN apt-get -qq update
RUN apt-get install --yes wget
RUN apt-get install --yes locales

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.2-Linux-x86_64.sh -O /wgetApi/miniconda3.sh
RUN /bin/bash /wgetApi/miniconda3.sh -b -p /wgetApi/miniconda3 && \
    . /wgetApi/miniconda3/etc/profile.d/conda.sh && \
    conda activate base && \
    conda update -n base conda && \
    conda install -c conda-forge -y pip

SHELL ["/wgetApi/miniconda3/bin/conda", "run", "-n", "base", "/bin/bash", "-c"]

EXPOSE 8000

RUN pip install -r requirements.txt
RUN pip install 'mod_wsgi<4.6'


CMD mod_wsgi-express start-server /wgetApi/esgf_wget/wsgi.py --working-directory /wgetApi \
    --user apache --group apache --port 8000 --server-root=/etc/esgf-wget-wsgi-8000



