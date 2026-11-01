# LuHm-OS art-only backend (DRAFT). Builds a Debian USERLAND; host keeps its kernel.
# The base tag must be digest-pinned and fully licensed/reviewed before promotion.
FROM debian:13-slim
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8
SHELL ["/bin/sh", "-eu", "-c"]
# Build-only distro package resolution; neither service startup nor local privileged writes.
RUN printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d && \
    chmod 0755 /usr/sbin/policy-rc.d && \
    apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates python3 git ffmpeg && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/luhm
# Explicit source allowlist. Do not COPY the entire repo, .git, videos or private art.
COPY doctrine/machineDebianFourLayerV1.json doctrine/machineDebianFourLayerV1.json
COPY doctrine/machineToHumanWizardV1.json doctrine/machineToHumanWizardV1.json
COPY doctrine/typedFourLaneSqlV1.json doctrine/typedFourLaneSqlV1.json
COPY doctrine/vendorReductionV1.json doctrine/vendorReductionV1.json
COPY doctrine/artistFirstArtToolCanonV1.json doctrine/artistFirstArtToolCanonV1.json
COPY .devcontainer/Dockerfile .devcontainer/Dockerfile
COPY host/ai-ffmpeg/ai-ffmpeg.py host/ai-ffmpeg/ai-ffmpeg.py
COPY tools/machineToHumanWizard.py tools/machineToHumanWizard.py
COPY tools/machineDebianSnapshot.py tools/machineDebianSnapshot.py
COPY tests/testMachineDebianSnapshot.py tests/testMachineDebianSnapshot.py
# No sudo, systemd, root script or HTTP daemon at runtime.
USER 65534:65534
ENTRYPOINT ["python3", "tools/machineDebianSnapshot.py"]
