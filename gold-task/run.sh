#!/bin/bash

rm -rf ./train_lmdb ./val_lmdb mean.binaryproto 
convert_imageset --shuffle ./ ./images/train.txt ./train_lmdb
convert_imageset --shuffle ./ ./images/val.txt ./val_lmdb

compute_image_mean train_lmdb/ mean.binaryproto
echo "now call: "
echo "caffe train --solver=model/solver.prototxt --snapshot=snapshot_iter_run.solverstate"

# $Id: $


