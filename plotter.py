'''load pickle data to plot
'''
import os
import pickle
import argparse
import pdb

import matplotlib.pyplot as plt
SHOW_PICTURE = False

def load_other_data(filename, alg, other_alg):
    new_filename = filename.replace(alg, other_alg)
    new_filename_important_part = new_filename[new_filename.find(other_alg):]
    new_filename = ''
    for i in os.listdir('build'):
        if(i.find(new_filename_important_part)>0):
            new_filename = i
            break
    if(new_filename == ''):
        return False
    f = open(os.path.join('build', new_filename), 'rb')
    data = pickle.load(f)
    return [i['norm_rf'] for i in data]

def plot_ari(filename, plot_title='', pic_format='eps'):
    '''combine different algorithms
    '''
    f = open(os.path.join('build', filename), 'rb')
    data = pickle.load(f)
    if data[0]['z_in_1'] != data[1]['z_in_1']:
        x_title = 'z_in_1'
    elif data[0]['z_in_2'] != data[1]['z_in_2']:
        x_title = 'z_in_2'
    else:
        x_title = 'z_o'
        
    if(filename.find('info-clustering')>0):
        alg = 'GBIC'
        other_alg = 'GN'
        other_alg_2 = 'BHCD'
    elif(filename.find('gn')>0):
        alg = 'GBIC'
        other_alg = 'GN'
        other_alg_2 = 'BHCD'
    else:
        raise ValueError('finename must contain info-clustering or gn')
    x_data = [i[x_title] for i in data]
    distance_data = [i['norm_rf'] for i in data]
    plt.plot(x_data, distance_data, label=alg, linewidth=3, color='red', marker='o', markersize=12)
    data_2 = load_other_data(filename, alg, other_alg)    
    if(data_2):
        plt.plot(x_data, data_2, label=other_alg, linewidth=3, color='green', marker='+', markersize=12)
    data_3 = load_other_data(filename, alg, other_alg_2)    
    if(data_3):
        plt.plot(x_data, data_3, label=other_alg_2, linewidth=3, color='blue', marker='x', markersize=12)
        
    if(filename.find('dendrogram_purity')>0):
        y_label_name = 'dendrogram purity'
    else:
        y_label_name = 'distance'
    plt.ylabel(y_label_name, fontsize=18)
    if(x_title == 'z_o'):
        title_str = '$z_{in_1}$ = %.1f, $z_{in_2}$ = %.1f' % (data[0]['z_in_1'], data[0]['z_in_2'])
    elif(x_title == 'z_in_1'):
        title_str = '$z_{in_2}$ = %.1f, $z_o$ = %.1f' % (data[0]['z_in_2'], data[0]['z_o'])
    else:
        title_str = '$z_{in_1}$ = %.1f, $z_o$ = %.1f' % (data[0]['z_in_1'], data[0]['z_o'])
        
    if(x_title == 'z_o'):
        x_title_format = '$z_o$'
    elif(x_title == 'z_in_1'):
        x_title_format = '$z_{in_1}$'
    else:
        x_title_format = '$z_{in_2}$'
    plt.xlabel(x_title_format, fontsize=18)
       
    plt.title(title_str, fontsize=18)
    if x_title == 'z_o':
        plt.legend(fontsize='x-large', loc='best', bbox_to_anchor=(1, 0.5))
    else:
        plt.legend(fontsize='x-large')
    plt.savefig(os.path.join('build', x_title + '.' + pic_format), bbox_inches='tight', transparent=True)
    if SHOW_PICTURE:
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', help='pickle file to load, support glob pattern', default='pickle')
    parser.add_argument('--show_pic', default=False, type=bool, nargs='?', const=True, help='whether to show the picture interactively')
    parser.add_argument('--debug', default=False, type=bool, nargs='?', const=True, help='whether to enter debug mode') 
    parser.add_argument('--format', default='eps', choices=['eps', 'svg'])
    args = parser.parse_args()
    if args.debug:
        pdb.set_trace()
    if args.filename.find('.pickle') < 0:
        for i in os.listdir('build'):
            if i.find('.pickle') > 0 and i.find(args.filename) >= 0 and i.find('info-clustering') >= 0:
                file_name = i
                break
    else:
        file_name = args.filename
    SHOW_PICTURE = args.show_pic
    plot_ari(file_name, '', args.format)
