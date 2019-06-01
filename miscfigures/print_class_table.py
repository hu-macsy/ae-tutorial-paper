#!/usr/bin/env python3

import os
import yaml

classes = {}
with open('./network_classes.yml', 'r') as f:
	classes = yaml.load(f, Loader=yaml.BaseLoader)

class_fq = {}
n_instances = 0
for _, cl in classes.items():
	if cl not in class_fq:
		class_fq[cl] = 1
	else:
		class_fq[cl] += 1
	n_instances += 1

for cl in class_fq.keys():
	class_fq[cl] *= 100.0/n_instances

class_fq = sorted(class_fq.items(), key=lambda x: x[1], reverse=True)
out = '\\begin{tabular}{lr}\n'
out += '\\toprule\n'
out += 'Class & Frequency\\\\\n'
out += '\\midrule\n\\midrule\n'
for cl, fq in class_fq:
	out += '{:s} & \\numprint{{{:.2f}}} \%\\\\\n'.format(cl, fq)
out += '\\midrule\n\\midrule\n'
out += '\\end{tabular}\n'
with open('class_fq.tex', 'w') as f:
	f.write(out)
