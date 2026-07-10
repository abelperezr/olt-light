# Customization overlay for the prebuilt Light OLT runtime.
#
# The base image already ships everything heavy: sysrepo repos, YANG schema,
# seeds, device extensions, startup supervision and the NETCONF stack. This
# build just drops the editable layer on top, so a rebuild after touching
# anything under src/ takes a couple of seconds.
ARG OLT_BASE_IMAGE=ghcr.io/abelperezr/olt-ls:0.0.1
FROM ${OLT_BASE_IMAGE}

USER root

COPY src/light_olt/ /opt/light-olt/light_olt/
COPY src/ecli /usr/local/bin/ecli

# These paths are hardwired in the base image's startup supervisor -- keep
# them as-is or the daemons simply won't be launched. ipfix_exporter and
# onu_optics live twice on purpose: once as an executable, once as an
# importable module (the optics daemon imports the exporter).
COPY src/daemons/ipfix_exporter.py /usr/local/bin/ipfix_exporter
COPY src/daemons/ipfix_exporter.py /usr/local/lib/olt/ipfix_exporter.py
COPY src/daemons/onu_optics.py /usr/local/bin/onu_optics.py
COPY src/daemons/onu_optics.py /usr/local/lib/olt/onu_optics.py
COPY src/daemons/onu_dhcp.py /usr/local/bin/onu_dhcp.py

ENV PYTHONPATH=/opt/light-olt:/usr/local/lib/olt

# compileall doubles as a syntax gate: a typo in any module fails the build
# here instead of at runtime inside the container.
RUN chmod 0755 \
      /usr/local/bin/ecli \
      /usr/local/bin/ipfix_exporter \
      /usr/local/bin/onu_optics.py \
      /usr/local/bin/onu_dhcp.py && \
    python3 -m compileall -q /opt/light-olt /usr/local/lib/olt

LABEL org.opencontainers.image.title="light-olt-custom" \
      org.opencontainers.image.description="User-customizable eCLI, ONU DHCP, optics, and IPFIX overlay" \
      org.opencontainers.image.source="https://github.com/abelperezr/olt-light"

# CMD, ENTRYPOINT, exposed ports and health behavior are inherited from the base.
