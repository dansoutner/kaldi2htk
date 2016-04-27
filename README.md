# Simple Kaldi to HTK GMM/HMM model converting script

## Requirements

1. Compiled Kaldi (kaldi-asr.org)
2. python

## Compilation

1. Check your KALDI path in Makefile
2. make binaries with ```make```

## Usage

```
python kaldi2HTKmodel.py <model.mdl> <phones.txt> <tree> <outputHTKmodel> <outputTiedlist>
```

Note: script kaldi2AP.py is modification of kaldi2HTK.py suited for our decoder

## Licence

Implemented by Daniel Soutner, NTIS - New Technologie for the Information Society,
University of West Bohemia, Plzen, Czech rep. dsoutner@kky.zcu.cz, 2016.

Licensed under the 3-clause BSD.
