# wholeskim dockerfile, start from kmindex image
FROM tlemane/kmindex:latest

RUN apt-get update && apt-get install -y python3 parallel

# Copy NCBI taxonomy files
WORKDIR /usr/share
COPY intermediate/names.dmp intermediate/nodes.dmp intermediate/merged.dmp ./

# Copy scripts
WORKDIR /usr/local/bin
COPY code/prep_indices.sh code/parse_kmindex.py code/vis_assigment.py  ./
WORKDIR /usr/share
COPY intermediate/ntCard ./ntCard
WORKDIR /opt
COPY intermediate/kmtricks-v1.4.0-sources.tar.gz ./kmtricks/

# Install ntcard
WORKDIR /usr/share/ntCard
RUN ./autogen.sh
RUN ./configure
RUN make
RUN make install

# Install kmtricks
WORKDIR /opt/kmtricks
RUN tar -zxvf kmtricks-v1.4.0-sources.tar.gz
RUN mkdir build && cd build \
    && cmake .. -DKMER_LIST="32 64 96 128" -DWITH_MODULES=ON -DWITH_HOWDE=ON -DWITH_SOCKS=ON -DNATIVE=OFF \
    && make -j8

RUN cd /opt \
    && cd kmtricks/build \
    && cmake .. -DWITH_PLUGIN=ON \
    && make -j8

#RUN rm -rf /opt/kmtricks

WORKDIR /root
ENTRYPOINT /bin/bash
