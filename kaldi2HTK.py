#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Daniel Soutner, University of West Bohemia, Czechia
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted
# provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions
# and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
# and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

import re
import numpy as np
import subprocess
import sys
import os
import argparse

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

# Path to bin
print_transitions_bin = "print-transitions"
context_to_pdf_bin = "context-to-pdf"
gmm_copy_bin = "gmm-copy"


def mat2str(mat):
	"""Convert numpy matrix to string"""
	s = ""
	for i in range(mat.shape[0]):
		for j in range(mat.shape[1]):
			s += "%.6e" % mat[i,j]
			if j < mat.shape[1] - 1:
				s += " "
		if i < mat.shape[0] - 1:
			s += "\n"
	return s


def list2str(l):
	"""Convert list to matrix-string"""
	s = ""
	for i in range(len(l)):
		s += "%.6e" % l[i]
		if i < len(l) -1:
			s += " "
	return s


def shell(cmd):
	subprocess.call(cmd, shell=True)


def load_kaldi_gmms(fmdl):
	"""Load Kaldi GMM model, from text .mdl file"""
	mdl = {
	"vecSize" : None,
	"states" : None,
	}
	inTag = ""
	pTag = {}
	states = {}
	st_no = -1

	# Load model tags
	for raw_line in open(fmdl):
		line = raw_line.strip()

		if line.startswith("</"):
			inTag = ""
		elif line.startswith("<"):
			all_tags_in_line = re.findall("<([a-zA-Z_]+?)>", line)

			if len(all_tags_in_line) == 1:
				inTag = all_tags_in_line[0]
				pTag[all_tags_in_line[0]] = True
			else:
				for i in all_tags_in_line:
					inTag = i
					pTag[i] = True

		# Get DIMs
		if line.startswith("<DIMENSION>"):
			mdl["vecSize"] = int(line.split()[1])

		if inTag == "GCONSTS":
			data = [float(i) for i in line.split()[2:-1]]
			states[st_no]["GConsts"] = np.array(data)

		elif inTag == "WEIGHTS":
			data = [float(i) for i in line.split()[2:-1]]
			states[st_no]["Weights"] = np.array(data)

		elif inTag == "MEANS_INVVARS" and not line.startswith("<MEANS_INVVARS>"):
			data = [float(i) for i in line.replace("]", "").split()]
			try:
				states[st_no]["MeansInvVars"].append(data)
			except KeyError:
				states[st_no]["MeansInvVars"] = [data]

		elif inTag == "INV_VARS" and not line.startswith("<INV_VARS>"):
			data = [float(i) for i in line.replace("]", "").split()]
			try:
				states[st_no]["InvVars"].append(data)
			except KeyError:
				states[st_no]["InvVars"] = [data]

		elif inTag == "DiagGMM":
			st_no += 1
			states[st_no] = {}

	mdl["states"] = states
	return mdl


def load_kaldi_transitions(ftrans):
	"""Load Kaldi transition model"""

	probs = {}

	for line in open(ftrans):
		lx = line.strip().split()
		pdf = int(lx[1])
		# phone = int(lx[2])
		a = int(lx[3])
		b = int(lx[4])
		prob = float(lx[6])
		# probs[(pdf, phone, a, b)] = prob
		# if (pdf, a, b) in probs1:
		# 	print "ERROR: Bad transitions read at", (pdf, a, b)
		probs[(pdf, a, b)] = prob

	return probs


def load_kaldi_hmms(fctx):
	"""Load HMMs from text output of context to pdf binary"""
	hmms ={}

	hmm = []
	for line in open(fctx):
		lx = line.strip().split()
		if len(lx) == 5:
			ctx = (lx[0], lx[1], lx[2])
			n = int(lx[3])
			pdf = int(lx[4])
		elif len(lx) == 3:
			ctx = (lx[0],)
			n = int(lx[1])
			pdf = int(lx[2])
		else:
			raise ValueError("Data not understood.")

		# we do not need disambig phones
		if len(ctx) == 3 and ("#" in ctx[0] or "#" in ctx[1] or "#" in ctx[2]):
			continue

		# we do not need <eps>
		if len(ctx) == 3 and ("<eps>" in ctx[0] or "<eps>" in ctx[1] or "<eps>" in ctx[2]):
			continue

		if n == 0:  # first state, start new HMM
			if len(hmm) > 0:
				if not tuple(hmm) in hmms:
					hmms[tuple(hmm)] = [ctx_last]
				else:
					hmms[tuple(hmm)] += [ctx_last]
			hmm = [pdf]
		else:
			hmm.append(pdf)
			ctx_last = ctx

	# and the last one :)
	if not tuple(hmm) in hmms:
		hmms[tuple(hmm)] = [ctx_last]
	else:
		hmms[tuple(hmm)] += [ctx_last]
	return hmms


def load_kaldi_phones(fphones):
	"""Load Kaldi phones table"""
	phones2int = {}
	int2phones = {}

	for line in open(fphones):
		lx = line.strip().split()
		ph = lx[0]
		i = int(lx[1])
		phones2int[ph] = i
		int2phones[i] = ph

	return phones2int, int2phones


def to_htk_name(lst):
	# original names
	if len(lst) == 3:
		return lst[0]+"-"+lst[1]+"+"+lst[2]
	elif len(lst) == 1:
		return lst[0]
	else:
		raise ValueError("Only monophone/triphone models allowed.")


def convert(fmdl, fphones, ftree, foutname, ftiedname, vecSize=39, silphones="", GMM=False, sil_pdf_classes=3):

	# print all transitions
	shell("./%s %s > %s" % (print_transitions_bin, fmdl, ".transitions"))
	trans = load_kaldi_transitions(".transitions")

	# print all triphones
	shell("./%s --sil-pdf-classes=%d --sil-phones='%s' %s %s > %s" % (context_to_pdf_bin, sil_pdf_classes, silphones, fphones, ftree, ".ctx"))
	hmms = load_kaldi_hmms(".ctx")

	# phones
	phones2int, int2phones = load_kaldi_phones(fphones)

	if GMM:
		shell("%s --binary=false %s %s" % (gmm_copy_bin, fmdl, ".gmm"))
		gmms = load_kaldi_gmms(".gmm")
		vecSize = gmms["vecSize"]

	# Write HTK models
	with open(foutname, "w") as fw:
		print >> fw, "~o"
		print >> fw, "<STREAMINFO> 1 %d" % vecSize
		print >> fw, "<VECSIZE> %d<NULLD><USER><DIAGC>" % vecSize

		# Write transitions
		states = []
		for hmm in hmms.keys():
			trans_name = "_".join([str(x) for x in hmm])

			trans_mat = np.zeros((len(hmm)+2, len(hmm)+2))
			trans_mat[0, 1] = 1.
			for i, state in enumerate(hmm):
				states.append(state)
				for b in range(0, 2):
					if len(hmms[hmm][0]) == 3:
						ph = phones2int[hmms[hmm][0][1]]
					elif len(hmms[hmm][0]) == 1:
						ph = phones2int[hmms[hmm][0][0]]
					else:
						raise ValueError("Only mohophone/triphone models allowed.")
					try:
						# p = trans[state, ph, i, b]
						p = trans[state, i, b]
					except KeyError:
						if "#" in int2phones[ph]:
							print "INFO: Not found transition for pdf %d with phone %d at %d %d" % (state, ph, i, b)
						else:
							print "ERROR: Not found transition for pdf %d with phone %d at %d %d" % (state, ph, i, b)
							print "This could be bad error, probably some mistake in conversion?"
					trans_mat[i + 1, b + i + 1] = p

			# Print out transitions for this HMM
			print >> fw, '~t "T_%s"' % trans_name
			print >> fw, "<TRANSP> %d" % (len(hmm) + 2)
			print >> fw, mat2str(trans_mat)

		if GMM:
			# Write GMMs
			for s in gmms["states"].keys():
				print >> fw, '~s "state_%d"' % s
				num_mixes = len(gmms["states"][s]["GConsts"])
				print >> fw, "<NUMMIXES> %d" % num_mixes
				for gmm in range(num_mixes):
					print >> fw, "<MIXTURE> %d %e" % (gmm + 1, gmms["states"][s]["Weights"][gmm])
					print >> fw, "<MEAN> %d" % len(gmms["states"][s]["MeansInvVars"][gmm])
					print >> fw, list2str([i / j for i, j in zip(gmms["states"][s]["MeansInvVars"][gmm], gmms["states"][s]["InvVars"][gmm])])
					print >> fw, "<VARIANCE> %d" % len(gmms["states"][s]["InvVars"][gmm])
					print >> fw, list2str([1.0 / i for i in gmms["states"][s]["InvVars"][gmm]])
					gconst = np.log(2 * np.pi) * vecSize + np.sum(np.log(np.array([1.0 / i for i in gmms["states"][s]["InvVars"][gmm]])))
					print >> fw, "<GCONST> %e" % gconst

		else:
			# Write fake GMMs
			for s in set(states):
				print >> fw, '~s "state_%d"' % s
				num_mixes = 1
				print >> fw, "<NUMMIXES> %d" % num_mixes
				for gmm in range(num_mixes):
					print >> fw, "<MIXTURE> %d %e" % (gmm + 1, 1.0)
					print >> fw, "<MEAN> %d" % vecSize
					print >> fw, mat2str(np.zeros((1, vecSize)))
					print >> fw, "<VARIANCE> %d" % vecSize
					print >> fw, mat2str(np.ones((1, vecSize)))
					print >> fw, "<GCONST> %e" % 1.0

		# Write HMMs
		for hmm in hmms.keys():
			trans_name = "_".join([str(x) for x in hmm])
			hmm_name = to_htk_name(hmms[hmm][0])

			print >> fw, '~h "%s"' % hmm_name
			print >> fw, "<BEGINHMM>"
			print >> fw, "<NUMSTATES> %d" % (len(hmm) + 2)
			for idx, s in enumerate(hmm):
				print >> fw, "<STATE> %d" % (idx + 2)
				print >> fw, '~s "state_%d"' % s
			print >> fw, '~t "T_%s"' % trans_name
			print >> fw, "<ENDHMM>"

		os.fsync(fw)
		fw.flush()

	# Write HTK tiedlist
	written = set()  # just in case, we are writing something second time
	with open(ftiedname, "w") as fw:
		for hmm in hmms.keys():
			if len(hmms[hmm]) > 1:
				print >> fw, to_htk_name(hmms[hmm][0])
				for i in range(1, len(hmms[hmm])):
						if (to_htk_name(hmms[hmm][i]), to_htk_name(hmms[hmm][0])) not in written \
							and to_htk_name(hmms[hmm][i]) != to_htk_name(hmms[hmm][0]):

							print >> fw, to_htk_name(hmms[hmm][i]), to_htk_name(hmms[hmm][0])
							written.add((to_htk_name(hmms[hmm][i]), to_htk_name(hmms[hmm][0])))
			else:
				print >> fw, to_htk_name(hmms[hmm][0])


if __name__ == "__main__":

	DESCRIPTION = "Script for converting Kaldi GMM to HTK model"

	parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	#parser.add_argument('--config', default=None,
	#                    help='Config file, other keys will be set to default')
	parser.add_argument('--silphones', default="1,2,3", type=str,
	                    help='Numbers of silence phones, split by comma')
	parser.add_argument('--vec-size', default=39, type=int,
	                    help='Size of input vectors if you fake GMM model')
	parser.add_argument('--sil-pdf-classes', default=3, type=int,
	                    help='Silphones pdf classes, HTK default is 3, Kaldi default is 5')
	parser.add_argument('--sil', type=str, default="SIL,SPN,NSN",
	                    help='Sil phones names, split by comma', )
	parser.add_argument("kaldi_model")
	parser.add_argument("kaldi_phones")
	parser.add_argument("kaldi_tree")
	parser.add_argument("htk_output_model")
	parser.add_argument("htk_output_tiedlist")
	args = parser.parse_args()

	SIL = args.sil.split(",")

	convert(args.kaldi_model, args.kaldi_phones,args.kaldi_tree,
			args.htk_output_model, args.htk_output_tiedlist,
			vecSize=args.vec_size, silphones=args.silphones,
			GMM=True, sil_pdf_classes=args.sil_pdf_classes)
