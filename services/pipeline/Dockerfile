FROM python:3.12-slim
WORKDIR /workspace
COPY services/pipeline/pyproject.toml /tmp/pyproject.toml
RUN pip install --no-cache-dir PyYAML jsonschema
COPY services/pipeline/nspo /workspace/nspo
COPY data /workspace/data
COPY rules /workspace/rules
COPY configs /workspace/configs
COPY schema /workspace/schema
ENV PYTHONPATH=/workspace
CMD ["python", "-m", "nspo.engine.cli", "--input", "/workspace/data/synthetic/observations.json", "--rules", "/workspace/rules/patterns.yaml", "--output", "/workspace/data/derived/findings.json"]
