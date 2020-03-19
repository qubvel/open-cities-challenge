python -m src.predict \
    --configs $(ls configs/stage1*) \
    --test_dir data/processed/test/ \
    --test_csv data/preocessed/test_mosaic.csv \
    --dst_dir data/interim/stage1/ \
    --batch_size 8 \
    --gpu '0'