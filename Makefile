KALDI = /home/dan/kky/kaldi/src/


all:

EXTRA_CXXFLAGS = -Wno-sign-compare -I${KALDI}

include ${KALDI}/kaldi.mk

BINFILES = make-pdf-to-tid-transducer print-transitions context-to-pdf # gmm-copy - is in $kaldipath/src/gmmbin

OBJFILES =

         
ADDLIBS = ${KALDI}lm/kaldi-lm.a ${KALDI}decoder/kaldi-decoder.a ${KALDI}lat/kaldi-lat.a \
          ${KALDI}hmm/kaldi-hmm.a ${KALDI}transform/kaldi-transform.a ${KALDI}gmm/kaldi-gmm.a \
          ${KALDI}tree/kaldi-tree.a ${KALDI}matrix/kaldi-matrix.a  ${KALDI}util/kaldi-util.a \
          ${KALDI}base/kaldi-base.a  ${KALDI}thread/kaldi-thread.a ${KALDI}hmm/kaldi-hmm.a \
          ${KALDI}fstext/kaldi-fstext.a

TESTFILES =

include ${KALDI}/makefiles/default_rules.mk

