#
# BUILD APPLICATION
#
FROM mambaorg/micromamba:2.0.5-alpine3.20 AS build

# necessary to display the image on Github
LABEL org.opencontainers.image.source="https://github.com/molinfo-vienna/cypstrate"

# using the root user during the build stage
USER root

# keep Docker from buffering the output so we can see the output of the application in real-time
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# copy package files first (for caching docker layers)
COPY environment.yml requirements.txt ./

# install conda and pip dependencies
# use mount caches to speed up the build
# RUN --mount=type=cache,uid=57439,gid=57439,target=/home/mambauser/.cache/pip \
#     --mount=type=cache,uid=57439,gid=57439,target=/home/mambauser/.mamba/pkgs \
# create environment
# -p /env forces the environment to be created in /env so we don't have to know the env name
RUN micromamba env create --copy -p /env -f environment.yml && \
    # fix a problem with the RDKit installation (keeping pip from seeing the conda-installed RDKit)
    wget https://gist.githubusercontent.com/shirte/e1734e51dbc72984b2d918a71b68c25b/raw/ae4afece11980f5d7da9e7668a651abe349c357a/rdkit_installation_fix.sh && \
    chmod +x rdkit_installation_fix.sh && \
    ./rdkit_installation_fix.sh /env && \
    # install the pip dependencies
    micromamba run -p /env pip install -r requirements.txt

# copy the rest of the source code directory and install the main package
COPY . .
RUN micromamba run -p /env pip install --no-deps .

#
# RUN APPLICATION
#
FROM gcr.io/distroless/base-debian12

# copy the environment from the build stage
COPY --from=build /env /env

ENTRYPOINT ["/env/bin/cypstrate"]