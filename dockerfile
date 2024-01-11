# wholeskim dockerfile, start from kmindex image
FROM tlemane/kmindex:latest

RUN apt-get install python3

# Copy NCBI taxonomy files
WORKDIR /usr/share
COPY intermediate/names.dmp intermediate/nodes.dmp intermediate/merged.dmp ./

# Copy scripts
WORKDIR /usr/app/src
COPY code/prep_indices.sh code/parse_kmindex.py code/vis_assigment.py  ./

ENTRYPOINT /bin/bash
