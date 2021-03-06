#//////////////////////////////////////////////////////////////////////////#
#                                                                          #
#   Copyright (C) 2020 by David B. Blumenthal                              #
#                                                                          #
#   This file is part of GEDLIB.                                           #
#                                                                          #
#   GEDLIB is free software: you can redistribute it and/or modify it      #
#   under the terms of the GNU Lesser General Public License as published  #
#   by the Free Software Foundation, either version 3 of the License, or   #
#   (at your option) any later version.                                    #
#                                                                          #
#   GEDLIB is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the           #
#   GNU Lesser General Public License for more details.                    #
#                                                                          #
#   You should have received a copy of the GNU Lesser General Public       #
#   License along with GEDLIB. If not, see <http://www.gnu.org/licenses/>. #
#                                                                          #
#//////////////////////////////////////////////////////////////////////////#

##
# @file generate_molecules.py
# @brief Python script for generating synthetic molecules.
# @details The synthetic molecules generated by this script were used for the experiments in the following paper:
# - D. B. Blumenthal, S. Bougleux, N. Boria, J. Gamper, L. Brun:
#   &ldquo;Comparing heuristics for graph edit distance computation&rdquo;,
#   Accepted for publication in VLDB J. 
# 
# Usage: 
# ```sh
# $ python generate molecules.py [--num-molecules <arg>] [--num-node-labels <arg>] [--min-num-nodes <arg>] [--max-num-nodes <arg>]
# ```
#
# @warning Running this script overrides the molecules distributed with GEDLIB that were used for the experiments in the VLDB J. paper.
'''
Python script for generating synthetic molecules.
'''

from random import randint
from random import shuffle
from os.path import join
import argparse

class Tree:
    
    def __init__(self, num_nodes, edge_list):
        self.num_nodes = num_nodes
        self.node_labels = [0 for node in range(num_nodes)]
        self.edge_list = edge_list
    
    def __repr__(self):
        string = "num_nodes =  " + str(self.num_nodes) + "\n"
        string = string + "node_labels =  " + str(self.node_labels) + "\n"
        string = string + "edge_list =  " + str(self.edge_list)
        return string
    
    def generate_node_labels(self, num_labels):
        for node in range(self.num_nodes):
            self.node_labels[node] = randint(1, num_labels)
            
    def write_to_gxl(self, file_name):
        gxl_file_name = join("data", file_name)
        gxl_file = open(gxl_file_name, "w")
        gxl_file.write("<?xml version=\"1.0\"?>\n")
        gxl_file.write("<!DOCTYPE gxl SYSTEM \"http://www.gupro.de/GXL/gxl-1.0.dtd\">\n")
        gxl_file.write("<gxl>\n")
        gxl_file.write("<graph id=\"{}\" edgeids=\"false\" edgemode=\"undirected\">\n".format(file_name))
        for node in range(self.num_nodes):
            gxl_file.write("\t<node id=\"_{}\">\n".format(node))
            gxl_file.write("\t\t<attr name=\"chem\"><int>{}</int></attr>\n".format(self.node_labels[node]))
            gxl_file.write("\t</node>\n")
        for edge in self.edge_list:
            gxl_file.write("\t<edge from=\"_{}\" to=\"_{}\">\n".format(edge[0], edge[1]))
            gxl_file.write("\t\t<attr name=\"valence\"><int>{}</int></attr>\n".format(edge[2]))
            gxl_file.write("\t</edge>\n")
        gxl_file.write("</graph>\n")
        gxl_file.write("</gxl>\n")
        gxl_file.close()
        

def generate_canonical_pruefer_seq(num_nodes):
    # generate Pruefer sequence
    pruefer_sec = []
    for i in range(num_nodes - 2):
        pruefer_sec.append(randint(0, num_nodes - 1))
    # compute canonical form
    old_to_new_id = {}
    new_id = 0
    for i in range(num_nodes - 2):
        old_id = pruefer_sec[i]
        if not old_id in old_to_new_id:
            old_to_new_id[old_id] = new_id
            new_id = new_id + 1
        pruefer_sec[i] = old_to_new_id[old_id]
    # return canonical form
    return pruefer_sec
    
def pruefer_seq_to_tree(pruefer_seq):
    # collect the degrees
    num_nodes = len(pruefer_seq) + 2
    deg = [1 for node in range(num_nodes)]
    for node in pruefer_seq:
        deg[node] = deg[node] + 1
    # collect all edges except for the last
    edge_list = []
    for tail in pruefer_seq:
        for head in range(num_nodes):
            if deg[head] == 1:
                edge_list.append((tail, head, randint(1,2)))
                deg[tail] = deg[tail] - 1
                deg[head] = deg[head] - 1
                break
    # collect last edge
    u = num_nodes
    v = num_nodes
    for node in range(num_nodes):
        if deg[node] == 1:
            if u == num_nodes:
                u = node
            else:
                v = node
                break
    edge_list.append((u, v, randint(1,2)))
    # return tree
    return Tree(num_nodes, edge_list)
    
def generate_molecule(min_num_nodes, max_num_nodes):
    # create non-isomorphic Pruefer sequences
    pruefer_seq = generate_canonical_pruefer_seq(randint(min_num_nodes, max_num_nodes))
    # shuffle the Pruefer sequences
    num_nodes = len(pruefer_seq) + 2
    permutation = [i for i in range(num_nodes)]
    shuffle(permutation)
    for i in range(num_nodes - 2):
        pruefer_seq[i] = permutation[pruefer_seq[i]]
    # return trees obtained from Pruefer sequences
    return pruefer_seq_to_tree(pruefer_seq)

parser = argparse.ArgumentParser(description="Generate synthetic molecules for scalability tests.")
parser.add_argument("--num-molecules", help="number of molecules that should be generated", type=int, default=1000000)
parser.add_argument("--num-node-labels", help="size of node label alphabet", type=int, default=5)
parser.add_argument("--min-num-nodes", help="minimal number of nodes in molecules", type=int, default=10)
parser.add_argument("--max-num-nodes", help="minimal number of nodes in molecules", type=int, default=15)
args = parser.parse_args()

for mol_id in range(args.num_molecules):
    molecule = generate_molecule(args.min_num_nodes, args.max_num_nodes)
    molecule.generate_node_labels(args.num_node_labels)
    molecule.write_to_gxl("molecule_{}.gxl".format(mol_id))

collection = open("../../collections/S-MOL-5.xml", "w")
collection.write("<?xml version=\"1.0\"?>\n")
collection.write("<!DOCTYPE GraphCollection SYSTEM \"http://github.com/dbblumenthal/gedlib/data/collections/GraphCollection.dtd\">\n")
collection.write("<GraphCollection>\n")
for mol_id in range(args.num_molecules):
    collection.write("\t<graph file=\"molecule_{}.gxl\" class=\"1\"/>\n".format(mol_id))
collection.write("</GraphCollection>\n")
collection.close()