FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    zeek \
    python3 \
    python3-pip \
    tcpdump \
    iproute2 \
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
# Monitor docker network interface\n\
zeek -i eth0 local &\n\
# Keep container running\n\
tail -f /dev/null\n\
' > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]
