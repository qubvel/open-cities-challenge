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
$ make build && make start && make install
```

**Step 2. Starting pipelines inside container**

Start inference (`models/` dir should be provided with pretrained models)
```bash
$ make inference
```

Start training and inference
```bash
$ make train-inference
```

After pipeline execution final prediction will appear in `data/predictions/stage3/sliced/` directory.

**Step 3. Stop service**

After everything is done stop docker container
```bash
$ make clean
```

### In depth view

Before start please make sure:  
1. You clone the repo and have specified [requirements](#requirements)
2. Put data (`train_tier_1.tgz` and `test.tgz`) in `data/raw/` folder
3. Optionally downoad and extract pretrained models (`models/`)
4. Start service (see above instructions) 

The whole pipeline consist of 4 stages stages 1 to 3 steps each.
The whole structure is as follows:

 - Stage 0
   - Step 0 - preparing test data
 - Stage 1
   - Step 1 - prepraring train data (`train_tier_1`)
   - Step 2 - training 10 Unet models on that data
   - Step 3 - make prediction with ensemble of 10 models
 - Stage 2
   - Step 1 - take prediction from `stage 1` and prepare as train data (pseudolabels)
   - Step 2 - train 10 Unet models with `train_tier_1` and `stage_2` data (pseudolabels) 
   - Step 3 - make predictions with new models
 - Stage 3
   - Step 1 - take prediction from `stage 2` and prepare as train data (pseudolabels round 2)
   - Step 2 - train 5 Unet models with `train_tier_1` and `stage_3` data (pseudolabels round 2)
   - Step 3 - make prediction with new models

After whole pipeline execution final prediction will appear in `data/predictions/stage3/sliced/` directory. In case you have pretrained models you can run just `stage 0 step 0` and `stage 3 step 3` blocks.

#### Stage 0.

Command to run:  
```bash
$ make stage0
```

Consist of one step - prepraing `test.tgz` data. 
We will extract data and create mosaic from test tiles (it is better to stitch separate tiles into one big image, so prediction network will have more context). CSV file with data about mosaic is located in `data/processed/test_mosaic.csv` and created by jyputer notebook (`notebooks/mosaic.ipynb`). You dont need to generate it again, it is already exist.


#### Stage 1.

Train data preparation, models training and prediction with ensemble of models (consist of three steps).     


Command to run:  
```bash
$ make stage1
```

##### Step 1.

Prepraing data:

 - Extract `train_tier_1` data 
 - Resample data to 0.1 meters per pixel resolution
 - Generate raster masks from provided geojson files
 - Slice masks to small tiles with shape `1024 x 1024` (more convinient for training the models)

##### Step 2.

On this step 10 `Unet` models are going to be trained on data. 5 Unet models for `eficientnet-b1` encoder and 5 for `se_resnext_32x4d` encoder (all encoders are pretrained on Imagenet). We train 5 models for each encoder because of 5 folds validation scheme. Models trained with hard augmentations using `albumetations` library and random data sampling. Training last 50 epochs with couninious leraining rate decay from 0.0001 to 0.

##### Step 3.

Pretrained models aggregeated to `EnsembleModel` with test time augmentation (flip, rotate90) - all predicitons averaged by simple mean and thresholded by 0.5 value.  
First, prediction is made for stitched test images, than for others (which not present on mosaic).


#### Stage 2.

Train data preparation (add pseudolabels), models training and prediction with ensemble of models (consist of three steps).     


Command to run:  
```bash
$ make stage2
```