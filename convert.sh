#!/usr/bin/env bash

DIR=$1

gmm-copy --binary=false $DIR/final.mdl $DIR/final.mdl.txt
python kaldi2AP.py $DIR/final.mdl.txt $DIR/phones.txt $DIR/tree $DIR/HTKmodels $DIR/tiedlist

for nnet in $1/*.nnet
do
	nnet-copy --binary=false $nnet $nnet.txt
	python kaldi2NNEris.py $DIR/HTKmodels $nnet.txt $DIR/final.feature_transform $DIR/ali_train_pdf.counts $nnet.NNimage $nnet.stateOrder
done
