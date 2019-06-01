import aextl
import os
import yaml

INSTANCES={ 'advogato':'adv', 'dblp-cite':'dblp', 'edit-frwikinews': 'wkne' , \
			'foldoc': 'fold' , 'opsahl-powergrid': 'opsa', 'p2p-Gnutella24': 'Gn24' , \
			'ego-twitter': 'twit' , 'ego-facebook': 'egfb' , 'ego-gplus': 'egpl' ,\
			'petster-hamster': 'pets' , 'loc-brightkite_edges': 'locb', 'openflights': 'open',\
			'cfinder-google': 'cfin',  'moreno_blogs':'mrnb' , 'ca-AstroPh': 'caAs', \
			'ca-cit-HepTh': 'caTh', 'ca-cit-HepPh': 'caPh', 'subelj_cora': 'subc',\
			'cit-HepPh': 'ciPh', 'edit-frwikibooks': 'wkbo','facebook-wosn-wall': 'fbwo', \
			'wiki-Vote': 'wkVo','p2p-Gnutella05':'Gn05', 'p2p-Gnutella08': 'Gn08', \
			'p2p-Gnutella04': 'Gn04', 'twin':'twin','dimacs9-COL': 'dCOL', \
			'dimacs9-BAY':'dBAY' ,'roadNet-PA': 'rdPA', 'roadNet-TX':'rdTX' }

# load all successful runs in one object

def collectAllRuns( configFile ):

	def load_file(run, f):
		if os.stat(f.name).st_size == 0:
		    print("File " + f + " appears to be epty")
		    
		data = yaml.load(f)
		#print("Adding experiment " + run.experiment.name + " for instance " + run.instance.shortname)
		
		#print( len(run.experiment.variation) )
		#print( run.instance.instsets )
		
		#initialize some values with  0 and fix later
		return {
		    'experiment': run.experiment.name,
		    'instance': run.instance.shortname,
			'fullpath': run.instance.fullpath,
		    'run_time': data['run_time'],
		    'set': run.instance.instsets,
		    'variation': len(run.experiment.variation),
		    'parameters' : data['parameters'],
		    'n' : 0,  #number of nodes
		    'm' : 0,   #number of edges
		    'diam': 0   #diameter 
		}

	cfg = aextl.config_for_dir(configFile)
	# the object where all runs are stored
	allRuns = cfg.collect_successful_results( load_file )

	return allRuns, cfg

#------------------------------------------------------------------------------

#TODO: this is not very efficient, every time we have to read all graphs.
#      maybe write them in a file or adapt the output files contain this
#      information so it is extracted by 'collect_succesful_results().

#TODO: here, we could also add other attributes like the diameter 
# or max/average degree if they are of interest

#TODO: if a subset of graphs is stored in the file, it will read only from the file 
# and ignore the new graphs

# reads the graph files found in allRuns.instance and adds the number of node, edges and diameter

def addAttributes( allRuns, fileToRead='./instancesData.yml' ):

	#if the file exists, read from there #TODO: but the file may contain a subset of the graphs...
	if os.path.exists(fileToRead):
		print("Found file "+ fileToRead + ". Will read graph attributes from there and NOT read the actual files.")
		print("If you think that insances are old or corrupted comment out this line.")
		allRuns = addInstancesAttrFromFile( allRuns, fileToRead )
		return allRuns
	else:
		print("File was not given or not found. Will iterate through all runs and read every graph")

	#extract the instances names
	#if allRuns are sorted, instances should be sorted by size #TODO: we do not care so much here
	fullPaths = list( dict.fromkeys([ r['fullpath'] for r in allRuns]) ) #remove duplicates
	
	#read all input graphs and store their size
	for inst_path in fullPaths:
		
		from networkit import readGraph, centrality, Graph, Format, distance
		g = readGraph(
		    inst_path,
		    Format.EdgeList,
		    commentPrefix='%',
		    separator=' ',
		    firstNode=0,
		    continuous=False,
		    directed=False)
		g.removeSelfLoops()
		
		n = g.numberOfNodes()
		m = g.numberOfEdges()
		
		diam = distance.Diameter(g, algo=distance.DiameterAlgo.EstimatedRange, error=0.0 ).run().getDiameter()

		#find the runs that this instance is used
		for run in allRuns:
		    if run['fullpath']==inst_path:
		        run['n'] = n
		        run['m'] = m
		        run['diam'] = diam[0] #in most cases there is no difference between [0] and [1]
		        # TODO: what to do if they are different? if error is 0 they should be equal
		
		inst_name = os.path.basename( inst_path)
		print( inst_name , "n= "+str(n) + ", m= " + str(m) + ", diam= ", diam )
	
	fileToWrite = 'instancesData.yml'
	print("Will also write the data in file " + fileToWrite + " for future use")
	#storeInstToFile( allRuns, fileToWrite )
	
	return allRuns
		
#------------------------------------------------------------------------------

#extract the info for the instances and store them to a file 

def storeInstToFile( allRuns, fileToWrite ):

	fullPaths = list( dict.fromkeys([ r['fullpath'] for r in allRuns]) ) #remove duplicates
	
	#store data here and write them all together in the end
	instData = list()

	for inst_path in fullPaths:
		#search all runs to find one entry for this file
		for run in allRuns:
			if run['fullpath']==inst_path:
				n = run['n']
				m = run['m']
				diam = run['diam']
				break

		instD = {'fullpath': inst_path, 'n':n, 'm':m, 'diam':diam}
		instData.append( instD )

	with open(fileToWrite, 'w') as outfile:
	    yaml.dump(instData, outfile, default_flow_style=False)

#------------------------------------------------------------------------------

#TODO: add assertion to verify that everything is done properly and checks for cases where
#something is wrong

# read a file that stores the attributes of the isntances and store them to a allRuns object

def addInstancesAttrFromFile( allRuns, fileToRead ):

	if not os.path.exists(fileToRead):
		print("Provided file " + fileToRead + " to read the instances attributes does not exist");
		return Null

	with open( fileToRead, 'r') as stream:
		instData = yaml.load(stream)

	for inst in instData:
		inst_path = inst['fullpath']

		# find all entries with this instance path
		for run in allRuns:
			if run['fullpath']==inst_path:
				run['n'] = inst['n']
				run['m'] = inst['m']
				run['diam'] = inst['diam']

	return allRuns

#------------------------------------------------------------------------------

def abbreviate_Old( instances ):
	abbrvInst = list()
	for inst in instances:
		tokens = (inst.replace('_','-')).split('-')
		if len(tokens)==1:
			abbr = tokens[0][:3]
		elif len(tokens)==2:
			abbr = tokens[0][:1]+tokens[1][:1]+tokens[1][-1]
		else:
			abbr = tokens[0][:1]+tokens[1][:1]+tokens[2][:1]
		
		abbrvInst.append( abbr )
	
	return abbrvInst

def abbreviate( instances ):
	return [ INSTANCES[inst] for inst in instances]












