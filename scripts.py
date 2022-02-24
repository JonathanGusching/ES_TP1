import os
import subprocess as sp
import matplotlib.pyplot as plt
import re #RegEx

def sim_instructions(file_path, arguments='', options=''):
	sp.run('sim-profile ' + options  + ' ' + file_path + ' ' + arguments , shell=True)

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
		if(line.isnumeric()):
			cpt=cpt+1
			final_res.append(result)
			result=[]
		else:
			result.append(re.split(r" {2,}", line))
	file.close()
	return final_res

def sim_outorder(program_path, export_path, args):
	sp.run('sim-outorder ' + args + ' -redir:sim ' + export_path + ' ' + program_path, shell=True)

def sim_outorder(program_path, export_path, nsets, bsize, cache):
	sp.run('sim-outorder ' + ' -cache:'+ cache +' ' + cache + ':' + str(nsets) + ':' + str(bsize) + ':1:l' + ' -redir:sim ' 
		+ export_path + ' ' + program_path, shell=True)

def main():
	#Partie 1
	OUTPUT_FILE="res/res.txt"
	EXPORT_FILE="res/export.txt"
	clean_file(EXPORT_FILE)

	options='-redir:sim ' + ' \"'+OUTPUT_FILE+'\" ' + '-iclass true'

	''' SIMULER DIJKSTRA '''
	sim_instructions('dijkstra/dijkstra_small.ss', 'input_dat', options)
	# Si on voulait n'exporter qu'une seule ligne, par exemple "load   "
	#export_arguments("res.txt", "test", '\"load   \"')
	
	export_all_instructions(OUTPUT_FILE, EXPORT_FILE)

	''' SIMULER BLOWFISH '''
	sim_instructions('blowfish/blowfish/bf.ss', 'e input_small.asc output.out', options)
	
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

	nsets=[1024, 2048, 4096, 8192, 16384]
	bsize=32
	for nset in nsets:
		sim_outorder('dijkstra/dijkstra_small.ss input_dat', 'res/res_sim_outorder' + '_dl1_' + str(nset) + '.txt', nset, bsize, 'dl1')


main()