# wholeskim dockerfile, start from kmindex image
FROM tlemane/kmindex:latest

RUN apt-get update && apt-get install -y python3 parallel

# Copy NCBI taxonomy files
WORKDIR /usr/share
COPY intermediate/names.dmp intermediate/nodes.dmp intermediate/merged.dmp ./

# Copy scripts
WORKDIR /usr/app/src
COPY code/prep_indices.sh code/parse_kmindex.py code/vis_assigment.py  ./
COPY intermediate/ntCard ./ntCard

# Install ntcard
WORKDIR /usr/app/src/ntCard
RUN ./autogen.sh
RUN ./configure
RUN make
RUN make install

WORKDIR ~
ENTRYPOINT /bin/bash
