# Professor's headless remote workshop, not a public server or privileged VM.
# Ubuntu 26.04 LTS (Resolute Raccoon); Codespaces provides the host kernel.
FROM ubuntu:26.04
ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Never auto-start services during image creation. All server daemons are opt-in.
RUN set -eux; \
    printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d; chmod 0755 /usr/sbin/policy-rc.d; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      ca-certificates curl wget unzip zip git git-lfs sudo jq ripgrep file procps \
      build-essential pkg-config python3 python3-dev python3-pip python3-venv \
      nodejs npm ffmpeg blender gimp xvfb \
      nginx mariadb-server mariadb-client certbot \
      libgl1 libfontconfig1 libasound2t64 fonts-dejavu-core \
      bash-completion openssh-client; \
    rm -rf /var/lib/apt/lists/*

# Hard-stop outbound SQL sockets, including accidental mariadbd service launches.
RUN set -eux; \
    printf '[mysqld]\nskip-networking=1\nsocket=/run/mysqld/mysqld.sock\n' \
      > /etc/mysql/mariadb.conf.d/99-luhm-private.cnf

# Godot 4 is NOT the Ubuntu godot3 package. Use the hash already recorded in
# the canonical Godot CI workflow to detect corrupt or replaced downloads.
ARG TARGETARCH
RUN set -eux; \
    test "${TARGETARCH:-amd64}" = amd64; \
    curl --fail --location --retry 3 --connect-timeout 20 \
      -o /tmp/godot.zip \
      https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64.zip; \
    echo 'cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4  /tmp/godot.zip' | sha256sum --check -; \
    mkdir -p /tmp/godot; unzip -q /tmp/godot.zip -d /tmp/godot; \
    install -m 0755 /tmp/godot/Godot_v4.7.2-stable_linux.x86_64 /usr/local/bin/godot; \
    rm -rf /tmp/godot /tmp/godot.zip; \
    godot --headless --version

# Normal Codespaces user; sudo is available only inside this dev container.
RUN set -eux; \
    useradd -m -s /bin/bash codespace; \
    echo 'codespace ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/90-codespace; \
    chmod 0440 /etc/sudoers.d/90-codespace
USER codespace
WORKDIR /home/codespace
CMD ["sleep", "infinity"]
