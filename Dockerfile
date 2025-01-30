FROM mambaorg/micromamba:2.0.5-alpine3.20

# necessary to display the image on Github
LABEL org.opencontainers.image.source="https://github.com/shirte/nerdd"

USER root

# rdkit requires libxrender, libxext-dev and libxau
# wget is used to download the RDKit installation fix script
# entr is used for live reloading the application
RUN apk update && apk add git libxrender libxext-dev libxau wget entr

# Necessary, so Docker doesn't buffer the output and that we can see the output 
# of the application in real-time.
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy only the environment file first, so that we can cache the dependencies
COPY environment.yml .
RUN micromamba env create -f environment.yml

# Fix a problem with the RDKit installation
RUN wget https://gist.githubusercontent.com/shirte/e1734e51dbc72984b2d918a71b68c25b/raw/4a419e6e2b9019e2d6d7d1fa0f9c2a4708c0fc53/rdkit_installation_fix.sh \
    && chmod +x rdkit_installation_fix.sh \
    && ./rdkit_installation_fix.sh cypstrate

# Copy the rest of the source code directory and install the main package
COPY . .
RUN --mount=type=cache,target=/root/.cache/pip \
    micromamba run -n cypstrate pip install .

RUN --mount=type=cache,target=/root/.cache/pip \
    micromamba run -n cypstrate pip install nerdd-link==0.2.13

# Note: PYTHONUNBUFFERED is not enough, because it only affects the Python
# standard output, not the output of the application.
ENTRYPOINT micromamba run -n cypstrate \
    nerdd_prediction_server cypstrate.CypstrateModel \
    --broker-url $KAFKA_BROKER_URL \
    --data-dir /data
