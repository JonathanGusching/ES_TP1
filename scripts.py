import os
import subprocess as sp
import matplotlib.pyplot as plt
import re #RegEx
import numpy as np

def sim_instructions(file_path, arguments='', options=''):
	sp.run('sim-profile ' + options  + ' ' + file_path + ' ' + arguments , shell=True)

def blowfish(size, key, options):
	if(size==1):
		sp.run('sim-profile ' + options + ' blowfish/blowfish/bf.ss e input_small.asc output_small.out ' + str(key) , shell=True)
	elif(size==2):
		sp.run('sim-profile ' + options + ' blowfish/blowfish/bf.ss e input_medium.asc output_medium.out ' + str(key) , shell=True)
	elif(size==3):
		sp.run('sim-profile ' + options +' blowfish/blowfish/bf.ss e input_large.asc output_large.out ' + str(key) , shell=True)

def export_arguments(file_path, export_path, argument):
	sp.run('grep ' + argument + ' ' + file_path + '>>' + export_path, shell=True)

def export_all_instructions(file_path, export_path):
	sp.run('grep ' + '\"load   \"' + ' ' + file_path + '>>' + export_path, shell=True)
	sp.run('grep ' + '\"store   \"' + ' ' + file_path + '>>' + export_path, shell=True)
	#uncond est inclu dans cond
	#sp.run('grep ' + '\"uncond branch   \"' + ' ' + file_path + '>>' + export_path, shell=True)
	sp.run('grep ' + '\"cond branch   \"' + ' ' + file_path + '>>' + export_path, shell=True)
	sp.run('grep ' + '\"int computation   \"' + ' ' + file_path + '>>' + export_path, shell=True)
	sp.run('grep ' + '\"fp computation   \"' + ' ' + file_path + '>>' + export_path, shell=True)
	sp.run('grep ' + '\"trap   \"' + ' ' + file_path + '>>' + export_path, shell=True)

def clean_file(file_path):
	if(os.path.exists(file_path)):
		f = open(file_path, 'w')
		f.truncate(0)
		f.close()

def append_to_file(file_path, to_write):
	with open(file_path, 'a') as f:
		f.write(to_write + '\n')

def file_to_list(file_path):
	file=open(file_path, 'r')
	lines=file.read().splitlines()
	final_res=[]
	result=[]
	cpt=0
	for line in lines:
		new_line=line.split("#", -1)[0]
		if(line.isnumeric()):
			cpt=cpt+1
			final_res.append(result)
			result=[]
		else:
			result.append(re.split(r" {2,}", new_line))
	file.close()
	return final_res

def sim_outorder(program_path, export_path, args):
	sp.run('sim-outorder ' + args + ' -redir:sim ' + export_path + ' ' + program_path, shell=True)

def sim_cache(program_path, export_path, nsets, bsize, assoc, cache, options):
	'''
	nsets=nombre d'ensembles du cache
	bsize=taille du bloc
	assoc=associativité
	cache = dl1 ou il1
	'''
	sp.run('sim-outorder ' + ' -cache:'+ cache +' ' + cache + ':' + str(nsets) + ':' + str(bsize) + ':' + str(assoc) + ':l ' + options + ' -redir:sim ' 
		+ export_path + ' ' + program_path, shell=True)

def sim_cpu(cpu_name, program_to_execute='dijkstra'):
	if(program_to_execute=='dijkstra'):
		program_to_execute_with_args='dijkstra/dijkstra_small.ss input_dat'
	elif(program_to_execute=='blowfish'):
		program_to_execute_with_args='blowfish/blowfish/bf.ss e input_small.asc output_small.out 1234567890123456789'
	else:
		print('Wrong program sim_cpu')
		return
	#Cortex A15
	if(cpu_name=='a15'):
		nsets=[16, 32, 64, 128, 256]
		bsize=64
		assoc=2
		sim_cycle=[]
		ipc=[]
		il1_miss_rate=[]
		dir_hits=[]
		pred_miss=[]
		dl1_miss_rate=[]
		list=[]
		for nset in nsets:
			file_path='res/res_sim_outorder' + 'l1_' + str(nset*bsize*assoc) + '.txt'
			
			clean_file(file_path)
			clean_file('res/'+str(nset*bsize*assoc)+'.res')

			instruc_l1_str='-cache:il1 il1:' + str(nset) + ':' + str(bsize) + ':' + str(assoc) + ':l '
			args='-bpred \"2lev\" -bpred:btb 256 1 -decode:width 4 -fetch:mplat 15 -issue:width 8 -commit:width 4 -fetch:ifqsize 8 -ruu:size 16 -lsq:size 16 -res:ialu 5 -res:fpalu 1 -res:imult 1 -res:fpmult 1 '
			sim_cache(program_to_execute_with_args, file_path, nset, bsize, assoc, 'dl1', 
				args + instruc_l1_str + '-cache:il2 dl2 -cache:dl2 dl2:512:64:16:l')
			#export all the useful arguments
			export_arguments(file_path, 'res/'+str(nset*bsize*assoc)+'.res', 'sim_cycle  ' )
			export_arguments(file_path, 'res/'+str(nset*bsize*assoc)+'.res', 'sim_IPC  ' )
			export_arguments(file_path, 'res/'+str(nset*bsize*assoc)+'.res', 'il1.miss_rate  ' )
			export_arguments(file_path, 'res/'+str(nset*bsize*assoc)+'.res', 'bpred_2lev.dir_hits  ' )
			export_arguments(file_path, 'res/'+str(nset*bsize*assoc)+'.res', 'bpred_2lev.misses  ' )
			export_arguments(file_path, 'res/'+str(nset*bsize*assoc)+'.res', 'dl1.miss_rate  ' )
	
			append_to_file('res/'+str(nset*bsize*assoc)+'.res', '1')

			f2list=file_to_list('res/'+str(nset*bsize*assoc)+'.res')
			sim_cycle.append(int(f2list[0][0][1]))
			ipc.append(float(f2list[0][1][1]))
			il1_miss_rate.append(float(f2list[0][2][1]))
			dir_hits.append(float(f2list[0][3][1]))
			pred_miss.append(float(f2list[0][4][1]))
			dl1_miss_rate.append(float(f2list[0][5][1]))

			list.append(file_to_list('res/'+str(nset*bsize*assoc)+'.res'))
		
		x=[nset*bsize*assoc for nset in nsets]
		plt.plot(x, ipc)
		plt.title("Cortex A15 ipc en fonction de la mémoire L1 - " + program_to_execute)
		plt.show()

		plt.plot(x, sim_cycle)
		plt.title("Cortex A15 sim_cycle en fonction de la mémoire L1 - " + program_to_execute)
		plt.show()

		plt.plot(x, il1_miss_rate)
		plt.title("Cortex A15 il1_miss_rate en fonction de la mémoire L1 - " + program_to_execute)
		plt.show()

		plt.plot(x, dl1_miss_rate)
		plt.title("Cortex A15 dl1_miss_rate en fonction de la mémoire L1 - "+ program_to_execute)
		plt.show()

		ratio=[dir_hits[i]/pred_miss[i] for i in range(len(nsets))]
		plt.plot(x, ratio)
		plt.title("Cortex A15 ratio directional hits / miss en fonction de la mémoire L1 - " + program_to_execute)
		plt.show()

		#print(list)
	elif(cpu_name=='a7'):
		nsets=[16, 32, 64, 128, 256]
		bsize=32
		assoc=2
		sim_cycle=[]
		ipc=[]
		il1_miss_rate=[]
		dir_hits=[]
		pred_miss=[]
		dl1_miss_rate=[]
		list=[]
		for nset in nsets:
			file_path='res/res_sim_outorder' + 'l1_' + str(nset*bsize*assoc) + '.txt'
			
			clean_file(file_path)
			clean_file('res/'+str(nset*bsize*assoc)+'.res')

			instruc_l1_str='-cache:il1 il1:' + str(nset) + ':' + str(bsize) + ':' + str(assoc) + ':l '
			args='-bpred \"bimod\" -bpred:btb 256 1 -decode:width 2 -fetch:mplat 8 -issue:width 4 -commit:width 2 -fetch:ifqsize 4 -ruu:size 2 -lsq:size 8 -res:ialu 1 -res:fpalu 1 -res:imult 1 -res:fpmult 1 '
			sim_cache(program_to_execute_with_args, file_path, nset, bsize, assoc, 'dl1', 
				args + instruc_l1_str + '-cache:il2 dl2 -cache:dl2 dl2:128:32:8:l')
			#export all the useful arguments
			export_arguments(file_path, 'res/'+str(nset*bsize*assoc)+'.res', 'sim_cycle  ' )
			export_arguments(file_path, 'res/'+str(nset*bsize*assoc)+'.res', 'sim_IPC  ' )
			export_arguments(file_path, 'res/'+str(nset*bsize*assoc)+'.res', 'il1.miss_rate  ' )
			export_arguments(file_path, 'res/'+str(nset*bsize*assoc)+'.res', 'bpred_bimod.dir_hits  ' )
			export_arguments(file_path, 'res/'+str(nset*bsize*assoc)+'.res', 'bpred_bimod.misses  ' )
			export_arguments(file_path, 'res/'+str(nset*bsize*assoc)+'.res', 'dl1.miss_rate  ' )
	
			append_to_file('res/'+str(nset*bsize*assoc)+'.res', '1')

			f2list=file_to_list('res/'+str(nset*bsize*assoc)+'.res')
			sim_cycle.append(int(f2list[0][0][1]))
			ipc.append(float(f2list[0][1][1]))
			il1_miss_rate.append(float(f2list[0][2][1]))
			dir_hits.append(float(f2list[0][3][1]))
			pred_miss.append(float(f2list[0][4][1]))
			dl1_miss_rate.append(float(f2list[0][5][1]))

			list.append(file_to_list('res/'+str(nset*bsize*assoc)+'.res'))
		
		x=[nset*bsize*assoc for nset in nsets]
		plt.plot(x, ipc)
		plt.title("Cortex A7 ipc en fonction de la mémoire L1 - " + program_to_execute)
		plt.show()

		plt.plot(x, sim_cycle)
		plt.title("Cortex A7 sim_cycle en fonction de la mémoire L1 - " + program_to_execute)
		plt.show()

		plt.plot(x, il1_miss_rate)
		plt.title("Cortex A7 il1_miss_rate en fonction de la mémoire L1 - " + program_to_execute)
		plt.show()

		plt.plot(x, dl1_miss_rate)
		plt.title("Cortex A7 dl1_miss_rate en fonction de la mémoire L1 - "+ program_to_execute)
		plt.show()

		ratio=[dir_hits[i]/pred_miss[i] for i in range(len(nsets))]
		plt.plot(x, ratio)
		plt.title("Cortex A7 ratio directional hits / miss en fonction de la mémoire L1 - " + program_to_execute)
		plt.show()		


def sim_cpu_global_perf(cpu_name, program_to_execute='dijkstra'):
	if(program_to_execute=='dijkstra'):
		program_to_execute_with_args='dijkstra/dijkstra_small.ss input_dat'
	elif(program_to_execute=='blowfish'):
		program_to_execute_with_args='blowfish/blowfish/bf.ss e input_small.asc output_small.out 1234567890123456789'
	else:
		print('Wrong program sim_cpu')
		return
	#Cortex A15
	if(cpu_name=='a15'):
		nsets=[16, 32, 64, 128, 256]
		bsize=64
		assoc=2
		sim_cycle=[]
		ipc=[]
		il1_miss_rate=[]
		dir_hits=[]
		pred_miss=[]
		dl1_miss_rate=[]
		list=[]
		labels=[]
		for nset_d in nsets:
			for nset_i in nsets:
				labels.append(str(nset_i*bsize*assoc) + 'i' + 'x' + str(nset_d*bsize*assoc) + 'd')
				file_path='res/res_sim_outorder' + 'l1_' + str(nset_i*bsize*assoc) + 'x' + str(nset_d*bsize*assoc) + '.txt'
				EXPORT_PATH='res/i'+str(nset_i*bsize*assoc)+ '_d' +str(nset_d*bsize*assoc)+ '.res'
				
				clean_file(file_path)
				clean_file(EXPORT_PATH)

				instruc_l1_str='-cache:il1 il1:' + str(nset_i) + ':' + str(bsize) + ':' + str(assoc) + ':l '
				args='-bpred \"2lev\" -bpred:btb 256 1 -decode:width 4 -fetch:mplat 15 -issue:width 8 -commit:width 4 -fetch:ifqsize 8 -ruu:size 16 -lsq:size 16 -res:ialu 5 -res:fpalu 1 -res:imult 1 -res:fpmult 1 '
				sim_cache(program_to_execute_with_args, file_path, nset_d, bsize, assoc, 'dl1', 
					args + instruc_l1_str + '-cache:il2 dl2 -cache:dl2 dl2:512:64:16:l')
				#export all the useful arguments
				export_arguments(file_path, EXPORT_PATH, 'sim_cycle  ' )
				export_arguments(file_path, EXPORT_PATH, 'sim_IPC  ' )
				export_arguments(file_path, EXPORT_PATH, 'il1.miss_rate  ' )
				export_arguments(file_path, EXPORT_PATH, 'bpred_2lev.dir_hits  ' )
				export_arguments(file_path, EXPORT_PATH, 'bpred_2lev.misses  ' )
				export_arguments(file_path, EXPORT_PATH, 'dl1.miss_rate  ' )
		
				append_to_file(EXPORT_PATH, '1')

				f2list=file_to_list(EXPORT_PATH)
				print(f2list)
				sim_cycle.append(int(f2list[0][0][1]))
				ipc.append(float(f2list[0][1][1]))
				il1_miss_rate.append(float(f2list[0][2][1]))
				dir_hits.append(float(f2list[0][3][1]))
				pred_miss.append(float(f2list[0][4][1]))
				dl1_miss_rate.append(float(f2list[0][5][1]))

				list.append(file_to_list(EXPORT_PATH))
		
		x=np.arange(len(labels))
		fig, ax=plt.subplots()
		#ax=fig.add_axes([0,0,1,1])
		ax.bar(x, ipc)
		ax.set_ylabel('ipc')
		ax.set_xticks(x)
		ax.set_xticklabels(labels)
		ax.set_title("Cortex A15 ipc en fonction de la mémoire L1 - " + program_to_execute)
		
		plt.xticks(rotation='vertical')
		fig.tight_layout()
		plt.show()

		#print(list)
	elif(cpu_name=='a7'):
		nsets=[16, 32, 64, 128, 256]
		bsize=32
		assoc=2
		sim_cycle=[]
		ipc=[]
		il1_miss_rate=[]
		dir_hits=[]
		pred_miss=[]
		dl1_miss_rate=[]
		list=[]
		labels=[]
		for nset_d in nsets:
			for nset_i in nsets:
				labels.append(str(nset_i*bsize*assoc) + 'i' + 'x' + str(nset_d*bsize*assoc) + 'd')
				file_path='res/res_sim_outorder' + 'l1_' + str(nset_i*bsize*assoc) + 'x' + str(nset_d*bsize*assoc) + '.txt'
				EXPORT_PATH='res/i'+str(nset_i*bsize*assoc)+ '_d' +str(nset_d*bsize*assoc)+ '.res'
				
				clean_file(file_path)
				clean_file(EXPORT_PATH)

				instruc_l1_str='-cache:il1 il1:' + str(nset_i) + ':' + str(bsize) + ':' + str(assoc) + ':l '
				args='-bpred \"bimod\" -bpred:btb 256 1 -decode:width 2 -fetch:mplat 8 -issue:width 4 -commit:width 2 -fetch:ifqsize 4 -ruu:size 2 -lsq:size 8 -res:ialu 1 -res:fpalu 1 -res:imult 1 -res:fpmult 1 '
				sim_cache(program_to_execute_with_args, file_path, nset_d, bsize, assoc, 'dl1', 
					args + instruc_l1_str + '-cache:il2 dl2 -cache:dl2 dl2:128:32:8:l')
				#export all the useful arguments
				export_arguments(file_path, EXPORT_PATH, 'sim_cycle  ' )
				export_arguments(file_path, EXPORT_PATH, 'sim_IPC  ' )
				export_arguments(file_path, EXPORT_PATH, 'il1.miss_rate  ' )
				export_arguments(file_path, EXPORT_PATH, 'bpred_bimod.dir_hits  ' )
				export_arguments(file_path, EXPORT_PATH, 'bpred_bimod.misses  ' )
				export_arguments(file_path, EXPORT_PATH, 'dl1.miss_rate  ' )
		
				append_to_file(EXPORT_PATH, '1')

				f2list=file_to_list(EXPORT_PATH)
				sim_cycle.append(int(f2list[0][0][1]))
				ipc.append(float(f2list[0][1][1]))
				il1_miss_rate.append(float(f2list[0][2][1]))
				dir_hits.append(float(f2list[0][3][1]))
				pred_miss.append(float(f2list[0][4][1]))
				dl1_miss_rate.append(float(f2list[0][5][1]))

				list.append(file_to_list(EXPORT_PATH))
		
		x=[nset*bsize*assoc for nset in nsets]
		x=np.arange(len(labels))
		fig, ax=plt.subplots()
		#ax=fig.add_axes([0,0,1,1])
		ax.bar(x, ipc)
		ax.set_ylabel('ipc')
		ax.set_xticks(x)
		ax.set_xticklabels(labels)
		ax.set_title("Cortex A7 ipc en fonction de la mémoire L1 - " + program_to_execute)
		
		plt.xticks(rotation='vertical')
		fig.tight_layout()
		plt.show()


def main():
	#Partie 1
	OUTPUT_FILE="res/res.txt"
	EXPORT_FILE="res/export.txt"
	clean_file(EXPORT_FILE)

	options='-redir:sim ' + '\"'+OUTPUT_FILE+'\" ' + '-iclass true '

	''' SIMULER DIJKSTRA '''
	sim_instructions('dijkstra/dijkstra_small.ss', 'input_dat', options)
	# Si on voulait n'exporter qu'une seule ligne, par exemple "load   "
	#export_arguments("res.txt", "test", '\"load   \"')
	
	export_all_instructions(OUTPUT_FILE, EXPORT_FILE)

	''' SIMULER BLOWFISH '''
	#sim_instructions('blowfish/blowfish/bf.ss', 'e input_medium.asc output_medium.out 1234567890123456789', options)
	blowfish(1, 1234567890, options)

	#export_arguments("res.txt", "test", '\"load   \"')

	append_to_file(EXPORT_FILE, '1') # pour séparer les résultats entre eux
	
	export_all_instructions(OUTPUT_FILE, EXPORT_FILE)
	append_to_file(EXPORT_FILE, '2')

	list=file_to_list(EXPORT_FILE)
	#print(list)

	#Formattage pour affichage (peut sans doute être amélioré)
	val=[]
	row=[]

	val2=[]
	row2=[]
	for i in range(len(list[0])):
		val.append( [list[0][i][1],list[0][i][2]])
		row.append(list[0][i][0])

	for i in range(len(list[1])):
		val2.append( [list[1][i][1],list[1][i][2]])
		row2.append(list[1][i][0])

	# Affichage avec matplotlib
	fig, ax=plt.subplots()
	ax.set_axis_off()
	table=ax.table(
		cellText=val,
		rowLabels=row,
		colLabels=['nombre', 'pourcentage'],
		cellLoc='center',
		loc='upper left'
		)

	table2=ax.table(
		cellText=val2,
		rowLabels=row2,
		colLabels=['nombre', 'pourcentage'],
		cellLoc='center',
		loc='lower left'
		)
	ax.set_title("Comparaison Dijkstra et Blowfish")
	plt.show()

	sim_cpu_global_perf('a7', 'blowfish')
	#sim_cpu('a7', 'blowfish')
		


main()