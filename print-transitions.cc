// bin/make-pdf-to-tid-transducer.cc
// Copyright 2009-2011 Microsoft Corporation

// See ../../COPYING for clarification regarding multiple authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//  http://www.apache.org/licenses/LICENSE-2.0
//
// THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
// WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
// MERCHANTABLITY OR NON-INFRINGEMENT.
// See the Apache 2 License for the specific language governing permissions and
// limitations under the License.

#include "hmm/transition-model.h"
#include "hmm/hmm-utils.h"
#include "util/common-utils.h"
#include "fst/fstlib.h"
#include "base/kaldi-common.h"
#include "gmm/am-diag-gmm.h"
#include "matrix/kaldi-matrix.cc"

int main(int argc, char *argv[]) {
#ifdef _MSC_VER
  if (0) {
    fst::VectorFst<fst::StdArc> *fst = NULL;
    fst->Write("");
  }
#endif
  try {
    using namespace kaldi;
    typedef kaldi::int32 int32;

    const char *usage =
        "Write out transition-ids, phones, pdf-class, transition-idx\n"
        "Usage:   write-logprobs model-filename\n"
        "e.g.: \n"
        " write-logprobs 1.mdl > out.txt\n";
    ParseOptions po(usage);

    po.Read(argc, argv);

    if (po.NumArgs() <1 || po.NumArgs() > 1) {
      po.PrintUsage();
      exit(1);
    }

	std::string trans_model_filename = po.GetArg(1);
	TransitionModel trans_model;
	ReadKaldiObject(trans_model_filename, &trans_model);

	for (int32 i = 1; i < trans_model.NumTransitionIds() + 1; i++)
		{
		std::cout << i << " " \
			<< trans_model.TransitionIdToPdf(i) << " " \
			<< trans_model.TransitionIdToPhone(i) << " " \
			<< trans_model.TransitionIdToHmmState(i) << " " \
			<< trans_model.TransitionIdToTransitionIndex(i) << " " \
			<< trans_model.TransitionIdToTransitionState(i) << " " \
			<< trans_model.GetTransitionProb(i) << " " \
			<< trans_model.IsSelfLoop(i) << " " \
			<< trans_model.IsFinal(i) << "\n";
		}

	// old debug code bellow
	/*
	for (int32 i = 1; i < trans_model.NumTransitionStates() + 1; i++)
		{
		std::cout << i << " " << trans_model.TransitionStateToPhone(i) << " " \
			<< trans_model.TransitionStateToPdf(i) << " " \
			<< trans_model.TransitionStateToHmmState(i) << " " \
			<< trans_model.GetNonSelfLoopLogProb(i) << "\n";
	}
	*/
	//std::cout << trans_model.Print();
	//std::cout << trans_model.TopologyForPhone(1)[0];
	/*
	int32 	TransitionIdToTransitionState (int32 trans_id) const
	int32 	TransitionIdToTransitionIndex (int32 trans_id) const
	int32 	TransitionIdToPdf (int32 trans_id) const
	int32 	TransitionIdToPhone (int32 trans_id) const
	int32 	TransitionIdToPdfClass (int32 trans_id) const
	int32 	TransitionIdToHmmState (int32 trans_id) const
	int32 	TransitionStateToPhone (int32 trans_state) const
	int32 	TransitionStateToHmmState (int32 trans_state) const
	int32 	TransitionStateToPdf (int32 trans_state) const
	int32 	SelfLoopOf (int32 trans_state) const
	*/

  } catch(const std::exception &e) {
    std::cerr << e.what();
    return -1;
  }
}

