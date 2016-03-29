# Simple Kaldi to HTK GMM/HMM model converting script

## Requirements

1. Compiled Kaldi
2. python

## Installation

1. Check your KALDI path in Makefile
2. make binaries with ```make```
3. run :)

## Usage

```
python kaldi2HTKmodel.py <model.mdl> <phones.txt> <tree> <outputHTKmodel> <outputTiedlist>
```

Known limitations:
* Currently supports only 3-state HMMs

## Licence

Implemented by Daniel Soutner, NTIS - New Technologie for the Information Society,
University of West Bohemia, Plzen, Czech rep. dsoutner@kky.zcu.cz, 2016.

Licensed under the 3-clause BSD.