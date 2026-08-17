FROM spark:3.5.1-scala2.12-java17-python3-ubuntu AS base
USER root
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt
COPY src/ /opt/app/
# Zero-trust runtime: non-root, read-only rootfs (enforced by Kyverno too)
USER 185
ENTRYPOINT ["/opt/entrypoint.sh"]
