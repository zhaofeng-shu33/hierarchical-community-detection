'''
In this experiment, we prepare a graph with two level hierarchical structures.
The graph has k2 macro-communities and in each macro-community there are k1 micro-communities. Each micro-community
contains n nodes. There are also two parameters p1 and p2 which control the inter-community linkage respectively.
Ideally, when p2=0, the graph has k2 connected components and when p2=1, the graph is random at macro-community level.
p1 controls the micro-community linkage in the same manner.
Notice that p1 cannot be zero, otherwise the two-level structure of the graph does not exist.
By using info-clustering algorithm we try to recover the original graph with 
partition_num_list = [1, k2, k2*k1, n*k2*k1] under certain conditions of p1 and p2.

We also use other clustering algorithm which does not require predetermined cluster number. 
For example, Girvan-Newman algorithm and Affinity Propagation. There algorithms can get the macro-community first
and we rerun the algorithm to get the micro-community structures.

As we can see, if the graph has deep hierarchical structure, info-cluster has advantages since we only need to run ic algorithm once.
'''
import random
import argparse
from time import time
from datetime import datetime
import pdb
import logging
import os
import json

import numpy as np
import networkx as nx # for manipulating graph data-structure
try:
    import graphviz # for writing .gv file
except ImportError:
    pass

from ete3 import Tree
try:
    from ete3 import TreeStyle, NodeStyle
except ImportError: # missing PyQt5 module
    pass

from info_cluster import InfoCluster
from GN import GN
from bhcd import BHCD

import bhcd_parameter
from dendrogram_purity import dendrogram_purity
from ete_robinson_foulds import robinson_foulds

n = 16
k1 = 4 # inner
k2 = 4 # outer
K = 18
color_list = ['red', 'orange', 'green4', 'purple']
shape_list = ['sphere', 'circle', 'sphere', 'sphere']

st = open('ground_truth.txt').read()
ground_truth_tree = Tree(st)
ground_truth_labels = [[i*16+j for j in range(16)] for i in range(16)]
# construct
            
def plot_clustering_tree(tree, alg_name, cutting=0, tree_format='pdf'):
    '''if cutting=True, merge the n nodes at leaf nodes with the same parent.
    '''
    global n,k1
    if(cutting):
        tree_inner = tree.copy()
        cnt = 0
        delete_tree_node_list = []
        for _n in tree_inner:
            try:
                _n.category
            except AttributeError:
                _n.add_features(category=cnt)
                for i in _n.get_sisters():
                    if not(i.is_leaf()):
                        continue
                    try:
                        i.category
                    except AttributeError:
                        i.add_features(category=cnt)
                        delete_tree_node_list.append(i)
                cnt += 1
        for _n in delete_tree_node_list:
            _n.delete()
        # rename the tree node
        tree_inner = Tree(tree_inner.write(features=[]))
    else: 
        tree_inner = tree

    for _n in tree_inner:
        try:
            _n.macro
            break
        except AttributeError:        
            macro_index = int(_n.name) // (n * k1)
            micro_index = (int(_n.name) - macro_index * n * k1) // n 
            _n.macro = macro_index
            _n.micro = micro_index
            if(len(_n.name)>3):
                _n.name = str(_n.category)
        
    ts = TreeStyle()
    ts.rotation = 90
    ts.show_scale = False
    for _n in tree_inner:
        nstyle = NodeStyle()
        nstyle['fgcolor'] = color_list[int(_n.macro)]
        nstyle['shape'] = shape_list[int(_n.micro)]
        _n.set_style(nstyle)
    time_str = datetime.now().strftime('%Y-%m-%d-')
    file_name = time_str + 'tree_' + alg_name + '.' + tree_format
    tree_inner.render(os.path.join('build', file_name), tree_style=ts)
    
def add_category_info(G, tree):
    for n in tree:
        macro_index = G.nodes[int(n.name)]['macro']
        micro_index = G.nodes[int(n.name)]['micro']        
        n.add_features(macro=macro_index, micro=micro_index)

def evaluate_single(alg, G, metric):
    alg.fit(G)
    if(metric == 'norm_rf'):    
        res = robinson_foulds(alg.tree, ground_truth_tree)
        metric_score = res['norm_rf']
    elif(metric == 'dendrogram_purity'):
        metric_score = dendrogram_purity(alg.tree, ground_truth_labels)
    else:
        raise ValueError("unknown metric %s" % metric)
    return metric_score
    
def evaluate(num_times, alg, z_in_1, z_in_2, z_o, metric):
    '''
        num_times: int
        alg: algorithm class
        z_in_1: inter-micro-community node average degree     
        z_in_2: intra-micro-community node average degree
        z_o: intra-macro-community node average degree
        
        the evaluated alg is a class, and should provide fit method , which operates on similarity matrix
        and get_category(i) method, where i is the specified category.
    '''
    report = {'norm_rf' : 0,
             }
    assert(z_in_1 > z_in_2 and z_in_2 > z_o)
    logging.info('eval ' + str(type(alg)) + ' num_times=%d, z_in_1=%f,z_in_2=%f, z_o=%f'%(num_times, z_in_1, z_in_2, z_o))
    for i in range(num_times):
        G = construct(z_in_1, z_in_2, z_o)
        norm_rf = evaluate_single(alg, G, metric)
        logging.info('round {0}: with {2}={1}'.format(i, norm_rf, metric))
        report['norm_rf'] += norm_rf
    report['norm_rf'] /= num_times
    report.update({
                'num_times': num_times,
                'z_in_1': z_in_1,
                'z_in_2': z_in_2,
                'z_o': z_o})
    return report
    
def construct(z_in_1, z_in_2, z_out):
    '''
       p2: type float, percentage of edges to be added at macro level.
       p1: type float, percentage of edges to be added at micro level.
    '''
    global n,k1,k2
    p_1 = z_in_1/(n-1)
    
    assert(p_1 <= 1)
    assert(z_out > 0)
    
    p_2 = z_in_2/(n*(k1-1))
    p_o = z_out/(n*k1*(k2-1))
    G = nx.Graph()
    cnt = 0
    for t in range(k2):
        for i in range(k1):
            for j in range(n):
                G.add_node(cnt, macro=t, micro=i)
                cnt += 1
    for i in G.nodes(data=True):
        for j in G.nodes(data=True):
            if(j[0] <= i[0]):
                continue
            if(i[1]['macro'] != j[1]['macro']):
                if(random.random()<=p_o):
                    G.add_edge(i[0], j[0])
            else:
                if(i[1]['micro'] == j[1]['micro']):
                    if(random.random() <= p_1):
                        G.add_edge(i[0], j[0])
                else:
                    if(random.random() <= p_2):
                        G.add_edge(i[0], j[0])
    return G    

def info_clustering_add_weight(G):
    # G is modified within this function
    # for each edge, the weight equals the number of triangles + beta(default to 1)    
    beta = 1
    for e in G.edges():
        i, j = e
        G[i][j]['weight'] = beta
        for n in G.nodes():
            if(G[i].get(n) is not None and G[j].get(n) is not None):
                G[i][j]['weight'] += 1
        G[i][j]['weight'] = G[i][j]['weight']
        
def write_gml_wrapper(G, filename, ignore_attr=False):
    if(ignore_attr):
        _G = nx.Graph()
        for node in G.nodes():
            _G.add_node(node)
        for edge in G.edges():
            i,j = edge
            _G.add_edge(i,j)
            
        # remove the attribute of _G
    else:
        _G = G.copy()
        info_clustering_add_weight(_G)
    nx.write_gml(_G, filename)
        
def graph_plot(G):
    '''
    generate the plot file which is the input of graphviz.
    G: networkx graph object
    '''
    global n, k1, k2
    time_str = datetime.now().strftime('%Y-%m-%d')
    write_gml_wrapper(G, os.path.join('build', 'two_level-%s.gml'%time_str))
    g = graphviz.Graph(filename='two_level-%s.gv'%time_str, engine='neato') # g is used for plotting
    for i in G.nodes(data=True):
        macro_index = i[1]['macro']
        g.node(str(i[0]), shape='point', color=color_list[macro_index])
    for e in nx.edges(G):
        i,j = e
        i_attr = G.nodes[i]
        j_attr = G.nodes[j]
        if(i_attr['macro'] != j_attr['macro']):
            edge_len = 2
            weight_value = 0.1
            edge_color = 'blue'
        elif(i_attr['micro'] != j_attr['micro']):
            weight_value = 1
            edge_len = 1
            edge_color = 'blue'
        else:
            weight_value = 10
            edge_len = 0.5
            macro_index = i_attr['macro']
            edge_color = color_list[macro_index]
        g.edge(str(i), str(j), weight=str(weight_value), penwidth="0.3", len=str(edge_len), color=edge_color, style='dotted')
    g.save(directory='build')

class InfoClusterWrapper(InfoCluster):
    def __init__(self, weight_method='triangle_power'):
        self.weight_method = weight_method
        super().__init__(affinity='precomputed')
    def fit(self, _G):
        G = _G.copy()
        if(self.weight_method == 'triangle_power'):
            info_clustering_add_weight(G)
        try:
            super().fit(G)
        except RuntimeError as e:
            print(e)
            # dump the graph
            print('internal error of the pdt algorithm, graph dumped to build/graph_dump.gml')
            nx.write_gml(_G, os.path.join('build', 'graph_dump.gml'))
            
if __name__ == '__main__':
    method_chocies = ['info-clustering', 'gn', 'bhcd', 'all']
    parser = argparse.ArgumentParser()
    parser.add_argument('--plot_graph', default=False, type=bool, nargs='?', const=True, help='whether to save the .gv file') 
    parser.add_argument('--save_graph', default=0, type=int, help='whether to save gml file, =0 not save(default), =1 save complete, =2 save without attribute')
    parser.add_argument('--load_graph', help='use gml file to initialize the graph')     
    parser.add_argument('--save_tree', default=0, type=int, nargs='?', const=1, help='whether to save the clustering tree pdf file after clustering, =0 not save, =1 save original, =2 save simplified')     
    parser.add_argument('--tree_format', default='pdf', choices=['pdf', 'png', 'svg'])
    parser.add_argument('--alg', default='all', choices=method_chocies, help='which algorithm to run', nargs='+')
    parser.add_argument('--metric', default='norm_rf', choices=['norm_rf', 'dendrogram_purity'], help='which evaluation metric to choose')
    parser.add_argument('--weight', default='triangle_power', help='for info-clustering method, the edge weight shold be used. This parameters'
        ' specifies how to modify the edge weight.', choices=['triangle_power', 'none'])    
    parser.add_argument('--z_in_1', default=14.0, type=float, help='inter-micro-community node average degree')      
    parser.add_argument('--z_in_2', default=3.0, type=float, help='intra-micro-community node average degree')          
    parser.add_argument('--z_o', default=-1, type=float, help='intra-macro-community node average degree')              
    parser.add_argument('--debug', default=False, type=bool, nargs='?', const=True, help='whether to enter debug mode')                  
    parser.add_argument('--evaluate', default=0, type=int, help='whether to evaluate the method instead of run once')
    parser.add_argument('--time', default=False, type=bool, nargs='?', const=True, help='whether to time the algorithm run')
    args = parser.parse_args()
    method_chocies.pop()
    if(args.debug):
        pdb.set_trace()
    if(args.z_o == -1):
        z_o = K - args.z_in_1 - args.z_in_2
    else:
        z_o = args.z_o
    if(args.load_graph):
        G = nx.read_gml(os.path.join('build', args.load_graph))
    else:
        G = construct(args.z_in_1, args.z_in_2, z_o)    
    if(args.plot_graph):
        graph_plot(G)
    if(args.save_graph):
        write_gml_wrapper(G, 'build/tuning.gml', args.save_graph-1)
    methods = []
    if(args.alg.count('all')>0):
        args.alg = method_chocies
    if(args.alg.count('info-clustering')>0):
        methods.append(InfoClusterWrapper(weight_method=args.weight))
    if(args.alg.count('gn')>0):
        methods.append(GN())
    if(args.alg.count('bhcd')>0):
        methods.append(BHCD(restart=bhcd_parameter.restart, 
            gamma=bhcd_parameter.gamma, _lambda=bhcd_parameter._lambda, delta=bhcd_parameter.delta))
    if(len(methods)==0):
        raise ValueError('unknown algorithm')
    
    if(args.evaluate > 0):
        LOGGING_FILE = 'two_level_%d.log'%os.getpid()
        logging.basicConfig(filename=os.path.join('build', LOGGING_FILE), level=logging.INFO, format='%(asctime)s %(message)s')    
        print('logging to', LOGGING_FILE)
        for method in methods:
            report = evaluate(args.evaluate, method, args.z_in_1, args.z_in_2, z_o, args.metric)
            logging.info('final report' + json.dumps(report))
    else:
        for i, method in enumerate(methods):
            alg_name = args.alg[i]
            print('running ' + alg_name)
            start_time = time()
            dis = evaluate_single(method, G, args.metric)
            if(args.time):
                time_elapsed = time() - start_time
                print('elapsed time: %f' % time_elapsed)
            print(args.metric, dis)            
            if(args.save_tree):
                add_category_info(G, method.tree)
                plot_clustering_tree(method.tree, alg_name, args.save_tree - 1, args.tree_format)
else:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
