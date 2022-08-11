#! /bin/env python
# create diag files from xyzfiles
# usage: xyz2diagram.py xyz1 xyz2....
# update for idiagram in homcloud-0.7.0
# update for homcloud-2.8.1 (2020.03.03)

import sys
import os
import subprocess
import homcloud.utils as utils
from homcloud.alpha_filtration import create_alpha_shape
import numpy as np
import argparse
from homcloud import pc_alpha
from homcloud.alpha_filtration import create_alpha_shape, PeriodicBoundaryCondition
from homcloud.utils import parse_bool, load_symbols


def main(args=None):
    #    for fileName in sys.argv[1:]:
    #        print("processing " +fileName + " ...")
    #        baseFileName = os.path.splitext(fileName)[0]
    #        iDiagramFileName = baseFileName+".idiagram"
    #        diphaProcessCommand = ["python", "-m", "homcloud.pc2diphacomplex", "-D", "-d", "3", "--no-square", "-I", fileName, iDiagramFileName]
    #        subprocess.call(diphaProcessCommand)
    args = argument_parser().parse_args()
    for filename in args.inputs:
        print("processing " + filename + " ...")
        output = os.path.splitext(filename)[0] + '.idiagram'
        points = np.loadtxt(filename)
        if args.noise > 0.0:
            points += pc_alpha.noise_array(
                args.noise, args.dimension, args.weighted,
                args.partial_filtration, points.shape[0]
            )

        bc = PeriodicBoundaryCondition(
            *args.periodic) if args.periodic else None
        alpha_shape = create_alpha_shape(points, args.dimension,
                                         args.weighted, args.partial_filtration, bc)
        if args.check_acyclicity:
            pc_alpha.alpha_shape.check_subsets_acyclicity()

        if args.partial_filtration:
            pc_alpha.alpha_shape.become_partial_shape()

        filtration = alpha_shape.create_filtration(args.no_square,
                                                   args.save_boundary_map)

        vertex_symbols = load_symbols(args.vertex_symbols)

        filtration = filtration.indexize(vertex_symbols)

        filtration.compute_diagram_and_save("./out/output_a", 1, args.algorithm)


def argument_parser():
    parser = argparse.ArgumentParser(
        description="Convert a point cloud to dipha's input (boundary matrix)"
    )
    parser.add_argument("-t", "--type", default="text",
                        help="input file format type")
    parser.add_argument("-n", "--noise", type=float, default=0.001,
                        help="level of additive noise")
    parser.add_argument("-d", "--dimension", type=int, default=3,
                        help="dimension of the input data")
    parser.add_argument("-w", "--weighted", action="store_true", default=False,
                        help="use an weighted alpha filtration")
    parser.add_argument("--no-square", action="store_true", default=True,
                        help="no squared output, if a birth radius is negative, the output is -sqrt(abs(r))")
    parser.add_argument("-P", "--partial-filtration", default=False, action="store_true",
                        help="Compute partial filtration (relative homology)")
    parser.add_argument("-A", "--check-acyclicity", default=False, action="store_true",
                        help="Check acyclicity for paritial filtration")
    parser.add_argument("-M", "--save-boundary-map",
                        default=True, type=parse_bool,
                        help="save boundary map into idiagram file"
                        "(only available with phat-* algorithms, *on*/off)")
    parser.add_argument("--algorithm", default=None,
                        help="algorithm (dipha, phat-twist(default), "
                        "phat-chunk-parallel)")
    parser.add_argument("--vertex-symbols", help="vertex symbols file")
    parser.add_argument("--periodic", nargs=6, type=float, default=None,
                        metavar=('xmin', 'xmax', 'ymin',
                                 'ymax', 'zmin', 'zmax'),
                        help="use a periodic alpha filtration")
    parser.add_argument("inputs", metavar="INPUTS",
                        nargs='+', help="input file name")
    return parser


if __name__ == '__main__':
    main()
