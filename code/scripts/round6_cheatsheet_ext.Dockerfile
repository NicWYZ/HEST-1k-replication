# Round 6 extension, cheatsheet track: the Linux image the trials run in
# (instruction section 6.5). Debian with bubblewrap, socat, Node, Claude Code at
# a recorded version, and Python 3 with the six libraries a trial may use.
# The harness's own extra library (pyarrow) lives in /opt/harness, which no
# trial's confinement binds.
#
#   docker build --build-arg CLAUDE_CODE_VERSION=2.1.295 \
#       -f code/scripts/round6_cheatsheet_ext.Dockerfile -t r6ext:1 code/scripts
FROM node:22-trixie-slim
ARG CLAUDE_CODE_VERSION=2.1.295
RUN apt-get update && apt-get install -y --no-install-recommends \
        bubblewrap socat python3 python3-pip python3-venv ca-certificates procps \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir --break-system-packages \
        numpy==2.5.3 pandas==3.0.5 scipy==1.18.1 Pillow==12.3.0 \
        scikit-image==0.26.0 scikit-learn==1.9.1
RUN python3 -m venv --system-site-packages /opt/harness \
    && /opt/harness/bin/pip install --no-cache-dir pyarrow
RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION} && npm cache clean --force
RUN mkdir -p /srv/r6_proxy && chown node:node /srv/r6_proxy
CMD ["sleep", "infinity"]
