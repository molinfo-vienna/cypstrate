FROM mambaorg/micromamba:2.0.5-alpine3.20

ENV ENV_NAME cypstrate

# necessary to display the image on Github
LABEL org.opencontainers.image.source="https://github.com/shirte/nerdd"

# keep Docker from buffering the output so we can see the output of the application in real-time
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# copy package files first (for caching docker layers)
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml requirements.txt ./

# install conda and pip dependencies
# use mount caches to speed up the build
# Note: uid=57439 is the user id of the mambauser in the micromamba image
# RUN --mount=type=cache,uid=57439,gid=57439,target=/home/mambauser/.cache/pip \
#     --mount=type=cache,uid=57439,gid=57439,target=/home/mambauser/.mamba/pkgs \
# create environment
RUN micromamba env create -f environment.yml && \
    # fix a problem with the RDKit installation (keeping pip from seeing the conda-installed RDKit)
    wget https://gist.githubusercontent.com/shirte/e1734e51dbc72984b2d918a71b68c25b/raw/4a419e6e2b9019e2d6d7d1fa0f9c2a4708c0fc53/rdkit_installation_fix.sh && \
    chmod +x rdkit_installation_fix.sh && \
    ./rdkit_installation_fix.sh $ENV_NAME && \
    # install the pip dependencies
    micromamba run -n $ENV_NAME pip install -r requirements.txt

# Copy the rest of the source code directory and install the main package.
COPY --chown=$MAMBA_USER:$MAMBA_USER . .
RUN micromamba run -n $ENV_NAME pip install --no-deps . && \
    # Save space by deleting the pip cache.
    rm -rf /home/mambauser/.cache/pip && \
    # Save space by deleting micromamba's cache and tarballs.
    micromamba clean --all --yes

ENTRYPOINT micromamba run -n $ENV_NAME \
    nerdd_prediction_server cypstrate.CypstrateModel \
    --broker-url $KAFKA_BROKER_URL \
    --data-dir /data
