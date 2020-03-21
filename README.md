# Open Cities

Description

## Table of content

## Requirements

#### Software:

- Docker (19.03.6, build 369ce74a3c)
- Docker-Compose (1.24.0-rc1, build 0f3d4dda)
- Nvidia-Docker (Nvidia Driver Version: 396.44)

 All other packages and software specified in `Dockerfile` and `requirements.txt`

#### Hardware

Recommended minimal configuration:

  - Nvidia GPU with at least 16GB Memory *
  - Disk space 256 GB (free)
  - 64GB RAM

\* - during inference it is possible to reduce batch size to reduce memory consumption, however training configuration need at least 16GB.

---

## Instructions

### Short summary

**Step1. Starting service**

Building docker image, start docker-compose service in daemon mode and install requirements inside container.

```bash
make build && make start && make install
```

**Step 2. Starting pipelines inside container**

Start inference (`models/` dir should be provided with pretrained models)
```bash
make inference
```

Start training and inference
```bash
make train-inference
```

**Step 3. Stop service**

After everything is done stop docker container
```bash
make clean
```

### In depth view

