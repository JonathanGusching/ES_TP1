import os
import subprocess as sp
import matplotlib as plt

def sim_instructions(file_path, arguments='', options=''):
	sp.run('sim-profile ' + options  + ' ' + file_path + ' ' + arguments , shell=True)

def export_arguments(file_path, export_path, argument):
	sp.run('grep ' + argument + ' ' + file_path + '>>' + export_path, shell=True)

def export_all_instructions(file_path, export_path):
	sp.run('grep ' + '\"load   \"' + ' ' + file_path + '>>' + export_path, shell=True)
	sp.run('grep ' + '\"store   \"' + ' ' + file_path + '>>' + export_path, shell=True)
	sp.run('grep ' + '\"uncond branch   \"' + ' ' + file_path + '>>' + export_path, shell=True)
	sp.run('grep ' + '\"cond branch   \"' + ' ' + file_path + '>>' + export_path, shell=True)
	sp.run('grep ' + '\"int computation   \"' + ' ' + file_path + '>>' + export_path, shell=True)
	sp.run('grep ' + '\"fp computation   \"' + ' ' + file_path + '>>' + export_path, shell=True)
	sp.run('grep ' + '\"trap   \"' + ' ' + file_path + '>>' + export_path, shell=True)

def clean_file(file_path):
	f = open(file_path, 'w')
	f.truncate(0) # need '0' when using r+
	f.close()

OUTPUT_FILE="res.txt"
EXPORT_FILE="export.txt"
clean_file(EXPORT_FILE)

options='-redir:sim ' + ' \"'+OUTPUT_FILE+'\" ' + '-iclass true'

sim_instructions('dijkstra/dijkstra_small.ss', 'input_dat', options)
#export_arguments("res.txt", "test", '\"load   \"')
export_all_instructions(OUTPUT_FILE, EXPORT_FILE)
sim_instructions('blowfish/blowfish/bf.ss', 'e input_small.asc output.out', options)
#export_arguments("res.txt", "test", '\"load   \"')
export_all_instructions(OUTPUT_FILE, EXPORT_FILE)
