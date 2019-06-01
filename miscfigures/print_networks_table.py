#!/usr/bin/env python3

import yaml
import simexpal
import os

cfg = simexpal.config_for_dir('../experiments/')

networks_dict_path = './networks_size.yml'
sizes = {}
def create_dict():
	for inst in cfg.all_instances():
		if inst.shortname in sizes:
			continue
		print("Processing {}".format(inst.shortname))
		if not os.path.isfile(inst.fullpath):
			print("Error: network ", inst.shortname, " not found, download it before.")
			continue
		from networkit import readGraph, Graph, Format, distance
		g = readGraph(
				inst.fullpath,
				Format.EdgeList,
				commentPrefix='%',
				separator=' ',
				firstNode=0,
				continuous=False,
				directed=False)
		g.removeSelfLoops()
		try:
			diam = distance.Diameter(g, 1).run().getDiameter()[0]
		except:
			diam = -1
		sizes[inst.shortname] = {
					'n' : g.numberOfNodes(),
					'm' : g.numberOfEdges(),
					'diam' : diam
				}
	with open(networks_dict_path, 'w') as f:
		yaml.dump(sizes, f, default_flow_style=False)

if os.path.isfile(networks_dict_path):
	with open(networks_dict_path, 'r') as f:
		sizes = yaml.load(f)
create_dict()

sorting_criteria = 'n'  # n or m
network_classes = {}
with open('./network_classes.yml', 'r') as f:
	network_classes = yaml.load(f)

sizes = sorted(sizes.items(), key=lambda x: x[1][sorting_criteria])
out = '\\begin{tabular}{lrrrr}\n'
out += '\\toprule\n'
out += 'Network name & \# of nodes & \# of edges & Diameter & Class\\\\\n'
out += '\\midrule\n\\midrule\n'
for s in sizes:
		name = s[0]
		name = name.replace('_', '\_')
		n = s[1]['n']
		m = s[1]['m']
		diam = s[1]['diam']
		net_class = network_classes[s[0]]
		out += '''{:s} & \\numprint{{{:d}}} &
			\\numprint{{{:d}}} &
			\\numprint{{{:d}}} &
			{:s} \\\\\n'''.format(
				name, n, m, diam, net_class)
out += '\\midrule\n\\midrule\n'
out += '\\end{tabular}\n'
with open('inst_list.tex', 'w') as f:
	f.write(out)

out = ''
for s in sizes:
	inst = cfg.get_instance(s[0])
	if 'evaluation' not in inst.instsets:
		continue
	name = s[0].replace('_', '\_')
	n = s[1]['n']
	m = s[1]['m']
	out += '''{:s} & \\numprint{{{:d}}} &
		\\numprint{{{:d}}}
		\\\\\n'''.format(
			name, n, m)
with open('evaluation_list.tex', 'w') as f:
	f.write(out)

out = ''
for s in sizes:
	inst = cfg.get_instance(s[0])
	if 'tuning' not in inst.instsets:
		continue
	name = s[0].replace('_', '\_')
	n = s[1]['n']
	m = s[1]['m']
	out += '''{:s} & \\numprint{{{:d}}} &
		\\numprint{{{:d}}}
		\\\\\n'''.format(
			name, n, m)
with open('tuning_list.tex', 'w') as f:
	f.write(out)

