import sys
from sklearn import decomposition
import numpy as np
import argparse
import pandas as pd


def addArguments(parser):
    parser.add_argument('-n', '--nfeature', nargs = '?', type=int, help = 'number of features', default = 2)
    parser.add_argument('-d', '--decomposition_method', nargs = '?',help = 'selection of decompsotion method. nmf, lda, pca or svd', default = 'nmf') 
    parser.add_argument('-c', '--component_file', nargs = '?', help = 'output file for   component', default = None)
    parser.add_argument('file', type = str, help = 'doc-word csv file')
    parser.add_argument('-r', '--regularize', action = 'store_true')
    parser.add_argument('-a', '--alpha', type = float, nargs = '?', default=0.0, help = 'penarty term of L1 norm. used only for NMF')
    return parser

def regularize(W, H):
    d = [ np.linalg.norm(H[i]) for i in range(H.shape[0])]
    d_W = np.diag(d)
    d_H = np.diag([1/x for x in d])
    W = np.matmul(W, d_W)
    H = np.matmul(d_H, H)
    return W, H



def main():
    parser=argparse.ArgumentParser(description = 'Apply SVD(=LSA)/NMF/LDA decomposition to cycle files')
    parser=addArguments(parser)
    args = parser.parse_args()
    
    table = pd.read_csv(args.file, index_col = 0)
    # if 'file' column exists, drop it
    if ('file') in table.columns:
        table = table.drop('file', axis = 1)
    corpus_word_list =table.columns
    doc_word_matrix = table.values
    if args.decomposition_method == 'nmf':
        model = decomposition.NMF(n_components = args.nfeature, alpha = args.alpha)
    elif args.decomposition_method == 'svd':
        model = decomposition.TruncatedSVD(n_components = args.nfeature)
    elif args.decomposition_method == 'lda':
        model = decomposition.LatentDirichletAllocation(n_components =args.nfeature)
    elif args.decomposition_method == 'pca':
        model = decomposition.PCA(n_components = args.nfeature)
    else:
        print('error: decomposition method is nmf, lda or svd')
        exit()
    W = model.fit_transform(doc_word_matrix)
    H_tmp = model.components_
    if (args.regularize):
        W, H_tmp = regularize(W, H_tmp)
    if (args.decomposition_method == 'svd' or args.decomposition_method == 'pca'):
        print(model.explained_variance_ratio_, file = sys.stderr)
    H = pd.DataFrame(H_tmp)
    H.columns = corpus_word_list
    np.savetxt(sys.stdout.buffer, W)
    if args.component_file is not None:
        H.to_csv(args.component_file) 


if __name__ == '__main__':
    main()
