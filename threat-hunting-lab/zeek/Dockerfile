FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install prerequisites and add Zeek repository
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    curl \
    python3 \
    python3-pip \
    tcpdump \
    iproute2 \
    && echo 'deb http://download.opensuse.org/repositories/security:/zeek/xUbuntu_22.04/ /' | tee /etc/apt/sources.list.d/security:zeek.list \
    && curl -fsSL https://download.opensuse.org/repositories/security:zeek/xUbuntu_22.04/Release.key | gpg --dearmor | tee /etc/apt/trusted.gpg.d/security_zeek.gpg > /dev/null \
    && apt-get update \
    && apt-get install -y zeek \
    && rm -rf /var/lib/apt/lists/*

# Add Zeek to PATH
ENV PATH="/opt/zeek/bin:${PATH}"

# Create log directory
RUN mkdir -p /zeek-logs

# Copy custom Zeek configuration
COPY local.zeek /opt/zeek/share/zeek/site/local.zeek

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Zeek Network Monitor..."\n\
cd /zeek-logs\n\
# Detect available network interface\n\
IFACE=$(ip -o link show | grep -v "lo:" | head -n 1 | awk -F": " "{print \\$2}")\n\
echo "Monitoring interface: $IFACE"\n\
# Start Zeek in background\n\
zeek -i $IFACE local > /zeek-logs/zeek-startup.log 2>&1 &\n\
# Keep container running\n\
tail -f /dev/null\n\
' > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]
