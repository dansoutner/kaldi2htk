// allTriphonesToPdf.cc

// Copyright 2016 Daniel Soutner

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


#include "tree/tree-renderer.h"
#include "tree/context-dep.h"

int main(int argc, char **argv) {
  using namespace kaldi;
  try {
	std::string qry;

	const char *usage =
		"Outputs Pdf for all possible triphones\n"
		"Usage: context-to-pdf <phone-symbols> <tree>\n"
		"e.g.: context-to-pdf phones.txt tree \n";
	
    std::string silphones = "1,2,3";
    int32 silpdfclasses = 5;
    int32 nonsilpdfclasses = 3;

	ParseOptions po(usage);

	po.Register("sil-phones", &silphones,
                "Comma separated list of silence phones");
    po.Register("sil-pdf-classes", &silpdfclasses,
                "Number of pdf-classes for silence phones");
    po.Register("non-sil-pdf-classes", &nonsilpdfclasses,
                "Number of pdf-classes for non-silence phones");
	po.Read(argc, argv);

	if (po.NumArgs() != 2) {
	  po.PrintUsage();
	  return -1;
	}
	std::string phnfile = po.GetArg(1);
	std::string treefile = po.GetArg(2);

	//read phones
	fst::SymbolTable *phones_symtab = NULL;
	{
		std::ifstream is(phnfile.c_str());
		phones_symtab = ::fst::SymbolTable::ReadText(is, phnfile);
		if (!phones_symtab)
			KALDI_ERR << "Could not read phones symbol table file "<< phnfile;
	}

	/*
      if (phones_symtab != NULL) {
        size_t ns = phones_symtab->NumSymbols();
        if (maxs != (int32) (ns-1)) {
          KALDI_WARN << "specified highest symbol (" << maxs
            << ") not equal to size of symtab (" << (ns-1) << "), adjusting ";
          maxs = (ns-1);
        }
      }
	*/

	//read tree object
	ContextDependency ctx_dep;
	ReadKaldiObject(po.GetArg(2), &ctx_dep);


      // parse silphones
      std::set<int32> silset;
      
      std::string::size_type i1 = 0, i2;
      do {
        i2 = silphones.find(',', i1);
        silset.insert(atoi(silphones.substr(i1, i2 - i1).c_str()));
        KALDI_LOG << "silphone: " << silphones.substr(i1, i2 - i1);
        if (i2 == std::string::npos)
          break;
        i1 = i2 + 1;
      } while (true);

	KALDI_LOG << "Context width:" << ctx_dep.ContextWidth();
	KALDI_LOG << "Central position:" << ctx_dep.CentralPosition();

	// triphones
	if((ctx_dep.ContextWidth() == 3) && (ctx_dep.CentralPosition() == 1)){
		// iter over all possible triphones
		size_t nphones = phones_symtab->NumSymbols();
		for (int32 l_ctx = 0; l_ctx < nphones; ++l_ctx) {
			for (int32 ph = 1; ph < nphones; ++ph) { // not <eps>
				for (int32 p_ctx = 0; p_ctx < nphones; ++p_ctx) {

					int32 pdf_id;

					//KALDI_LOG << "OK";

					// triphone context vector
					std::vector<int32> triphone;
					triphone.push_back(l_ctx);
					triphone.push_back(ph);
					triphone.push_back(p_ctx);

					//KALDI_LOG << "OK";

					//In the normal case the pdf-class is the same as the HMM state index (e.g. 0, 1 or 2), but pdf classes provide a way for the user to enforce sharing. 
					// pdf-classes http://kaldi.sourceforge.net/hmm.html
					int32 mpdf = (silset.find(ph) == silset.end() ?
													nonsilpdfclasses :
													silpdfclasses);

					//KALDI_LOG << mpdf;
					for (int32 pdf_class=0; pdf_class < mpdf; ++pdf_class) {
						//bool ContextDependency::Compute(const std::vector<int32> &phoneseq, int32 pdf_class, int32 *pdf_id)
						ctx_dep.Compute(triphone, pdf_class, &pdf_id);
						std::cout << phones_symtab->Find(l_ctx) << " " << phones_symtab->Find(ph) << " " << phones_symtab->Find(p_ctx) << " " << pdf_class << " " << pdf_id << "\n";
					}
				}
			}
		}
	}
	// mono
	if((ctx_dep.ContextWidth() == 1) && (ctx_dep.CentralPosition() == 0)){
		// iter over all possible monophones
		size_t nphones = phones_symtab->NumSymbols();
		for (int32 ph = 1; ph < nphones; ++ph) { // not <eps>
			int32 pdf_id;

			// mono context vector
			std::vector<int32> triphone;
			triphone.push_back(ph);

			//In the normal case the pdf-class is the same as the HMM state index (e.g. 0, 1 or 2), but pdf classes provide a way for the user to enforce sharing. 
			// pdf-classes http://kaldi.sourceforge.net/hmm.html
			int32 mpdf = (silset.find(ph) == silset.end() ?
											nonsilpdfclasses :
											silpdfclasses);

			for (int32 pdf_class=0; pdf_class < mpdf; ++pdf_class) {
				//bool ContextDependency::Compute(const std::vector<int32> &phoneseq, int32 pdf_class, int32 *pdf_id)
				ctx_dep.Compute(triphone, pdf_class, &pdf_id);
				std::cout << phones_symtab->Find(ph) << " " << pdf_class << " " << pdf_id << "\n";
			}
		}
	}


 	} catch (const std::exception &e) {
		std::cerr << e.what();
	return -1;
  }
}
