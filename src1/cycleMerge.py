import sys
from sklearn import decomposition
import numpy as np
import argparse
import pandas as pd


def docs2dwmatrix(fileList, weight_variable, weight_exponent):
    """ create doc-word matrix. The weight of word is the sum of life time of cycles """

    dwmatrix = np.empty((0, 0))
    corpuswordList = []
    for file in fileList:
        docwordList = []
        docweightList = []
        fin = open(file, "r")
        for line in fin.readlines():
            if line[0] == "#":  # life death line
                data = line.split()

                if weight_variable == 'lt':
                    weight = float(data[2])-float(data[1])
                elif weight_variable == 'b':
                    weight = float(data[1])
                elif weight_variable == 'd':
                    weight = float(data[2])
                else:
                    print("error: weight must be b, d, or lt")
                    exit()
            else:
                word = line[:-1]
                if word in docwordList:
                    docweightList[docwordList.index(
                        word)] += pow(weight, weight_exponent)
                else:
                    docwordList.append(word)
                    docweightList.append(weight)
        fin.close()
        # append new column if new word appended
        for word in docwordList:
            if word not in corpuswordList:
                corpuswordList.append(word)
                dwmatrix = np.append(dwmatrix, np.zeros(
                    (dwmatrix.shape[0], 1)), axis=1)
        # append new row
        dwmatrix = np.append(dwmatrix, np.zeros(
            (1, dwmatrix.shape[1])), axis=0)
        for word in docwordList:
            doc_index = docwordList.index(word)
            corpus_index = corpuswordList.index(word)
            dwmatrix[-1, corpus_index] = docweightList[doc_index]
    return dwmatrix, corpuswordList


def addArguments(parser):
    #parser.add_argument('-n', '--nfeature', nargs = '?', type=int, help = 'number of features', default = 2)
    #parser.add_argument('-d', '--decomposition_method', nargs = '?',help = 'selection of decompsotion method. nmf, lda or svd', default = 'nmf')
    #parser.add_argument('-c', '--component_file', nargs = '?', help = 'output file for   component', default = None)
    parser.add_argument('file_list', nargs='+', help='cycle files')
    #parser.add_argument( '--no_weight', action = 'store_true', default = False, help = 'don\'t use life time as weight (for nmf or svd)')
    #parser.add_argument('--table_only', action = 'store_true', default = False, help = 'create doc-word table in stdout without decompositon')
    #parser.add_argument('-a', '--alpha', type = float, nargs = '?', default=0.0, help = 'penarty term of L1 norm. used only for NMF')
    parser.add_argument('-e', '--exponent', type=float, nargs='?',
                        default=1.0, help='exponent for weight. default = 1.0')
    parser.add_argument('-w', '--weight', type=str, nargs='?',
                        default='lt', help='variables as weight. b, d, or lt')
    return parser


def main():
    parser = argparse.ArgumentParser(
        description='create topological feature vector table from cycle file')
    parser = addArguments(parser)
    args = parser.parse_args()
    doc_word_matrix, corpus_word_list = docs2dwmatrix(
        args.file_list, args.weight, args.exponent)
    H = pd.DataFrame(doc_word_matrix)
    H.columns = corpus_word_list
    H.to_csv(sys.stdout)


if __name__ == '__main__':
    main()
