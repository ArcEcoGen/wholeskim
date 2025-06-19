FROM debian:bookworm-slim AS builder

RUN apt-get update \
    && apt-get install -y  \
               bash build-essential automake autoconf cmake curl libssl-dev libbz2-dev libreadline-dev zlib1g-dev liblzma-dev libboost-all-dev git 

RUN mkdir -p /src
WORKDIR /src 

RUN curl -L https://github.com/bcgsc/ntCard/archive/refs/tags/1.2.2.tar.gz \
    | tar -xzf - \
    && cd ntCard-1.2.2 \
    && ./autogen.sh \
    && ./configure --prefix /usr/local \
    && sed -i '1i#include <sys/types.h>' Common/Uncompress.cpp \
    && sed -i 's/-Werror//g' Makefile */Makefile \
    && make install

RUN git clone https://github.com/DLTcollab/sse2neon \
    && cp sse2neon/*.h /usr/local/include/

RUN mkdir -p kmtricks-v1.4.0 \
    && curl -L https://github.com/tlemane/kmtricks/releases/download/v1.4.0/kmtricks-v1.4.0-sources.tar.gz \
    | tar -C kmtricks-v1.4.0 -xzf - \
    && cd kmtricks-v1.4.0 \
    && find . -type f \( -name "*.cpp" -o -name "*.c" -o -name "*.h" -o -name "*.hpp" \) \
              -exec grep -q '#include\s*<emmintrin\.h>' {} \; \
              -exec sh -c 'echo "Patching {}" && sed -i "s|#include\s*<emmintrin\.h>|#if defined(__aarch64__)\n#include <sse2neon.h>\n#else\n#include <emmintrin.h>\n#endif|" {}' \; \
    && mkdir -p build \
    && cd build \
    && cmake .. -DKMER_LIST="32 64 96 128" \
                -DWITH_MODULES=ON \
                -DWITH_HOWDE=ON \
                -DWITH_SOCKS=OFF \
                -DNATIVE=OFF \
                -DENABLE_ROARING_TESTS=OFF \
                -DSTATIC=ON \
    && make -j $(nproc) \
    && cd .. \
    && cp bin/* /usr/local/bin

RUN mkdir -p kmindex-v0.5.3 \
    && curl -L https://github.com/tlemane/kmindex/releases/download/v0.5.3/kmindex-v0.5.3-sources.tar.gz \
    | tar -C kmindex-v0.5.3 -xzf - \
    && cd kmindex-v0.5.3 \
    && find . -type f \( -name "*.cpp" -o -name "*.c" -o -name "*.h" -o -name "*.hpp" \) \
              -exec grep -q '#include\s*<emmintrin\.h>' {} \; \
              -exec sh -c 'echo "Patching {}" && sed -i "s|#include\s*<emmintrin\.h>|#if defined(__aarch64__)\n#include <sse2neon.h>\n#else\n#include <emmintrin.h>\n#endif|" {}' \; \
    && sed -i 's|^ *asm volatile("pause"); *$|#ifdef __aarch64__\nasm volatile("yield");\n#else\nasm volatile("pause");\n#endif|' lib/include/kmindex/spinlock.hpp \
    && cd build \
    && cmake .. -DCMAKE_BUILD_TYPE=Release \
           -DWITH_TESTS=OFF \
           -DPORTABLE_BUILD=OFF \
           -DCMAKE_INSTALL_PREFIX=/src/kmindex-v0.5.3 \
           -DMAX_KMER_SIZE=64 \
           -DWITH_SERVER=OFF \
           -DSTATIC_BUILD=ON \
    && make -j $(nproc) \
    && cp app/kmindex/kmindex /usr/local/bin

FROM debian:bookworm-slim AS wholeskim
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/local/bin
COPY code/prep_indices.sh code/parse_kmindex.py code/vis_assigment.py  ./

COPY --from=builder /usr/local/bin /usr/local/bin

RUN mkdir -p /data /references /genbank /cleanref

WORKDIR /data

ENTRYPOINT ["/bin/bash"]
