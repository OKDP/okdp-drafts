ARG EG_VERSION=3.2.2

FROM elyra/enterprise-gateway:${EG_VERSION} as kernels

FROM alpine:3.19.0

COPY --from=kernels /usr/local/share/jupyter/kernels /kernels/
# Overwrite the existing kernel by the new settings
COPY kernels/spark_python_kubernetes.json /kernels/spark_python_kubernetes/kernel.json


