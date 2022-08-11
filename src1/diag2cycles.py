import sys
import os
import subprocess
import argparse
import json

from homcloud.version import __version__
from homcloud.full_ph_tree import SpatialSearcher
from homcloud.diagram import PD
from homcloud.visualize_3d import ParaViewSimplexDrawer, ParaViewCubeDrawer
import homcloud.utils as utils
import homcloud.optimal_volume as optimal_volume
from homcloud.utils import deep_tolist


def argumentParser(parser):
    parser.add_argument('-d', '--degree', type = int, help = 'degree of persistent homology')
    parser.add_argument('-X', '--x-range', type = utils.parse_range, help = 'min and max of births')
    parser.add_argument('-Y', '--y-range', type = utils.parse_range, help = 'min and max of deaths')
    parser.add_argument('-l', '--lifetime', type = float, default = 0, help = 'min of life time')
    parser.add_argument('-c', '--cutoff-radius', type= float, default ='100.0', help = 'cutoff radius')
    parser.add_argument('-n', '--retry', type = int, default = '5', help = 'times to retry')
    parser.add_argument('files', type = str, nargs = '+', help = 'input idiagram files')
    parser.add_argument("--solver", help="LP solver")
    parser.add_argument("--constrain-on-birth-simplex", default=False,
                   action="store_true", help="constrain on the birth simplex")
    parser.add_argument("-C", "--optimal-cycle-children", default=False,
                   type=utils.parse_bool)
    parser.add_argument("--integer-programming", default=False,
                   type=utils.parse_bool,
                   help="use integer programming (on/*off*)")
    parser.add_argument("--draw-vertices", default=False, type=utils.parse_bool,
                   help="draw vertices (on/*off*)")
    parser.add_argument("--owned-volume", default=None, type=float,
                   metavar="THRESHOLD", help="Compute owned volumes")
    parser.add_argument("--owned-volume-connected", default=False,
                   type=utils.parse_bool, metavar="BOOL",
                   help="Output only the connecte component "
                   "of owned volume (on/*off*)")
    parser.add_argument("--tightened-volume", default=None, type=float,
                   metavar="THRESHOLD", help="Compute tightened volumes")
    parser.add_argument("--tightened-subvolume", default=None, type=float,
                   metavar="THRESHOLD", help="Compute tightened subvolumes")
    parser.add_argument("--no-optimal-volume", metavar="BOOL", default=False,
                   type=utils.parse_bool,
                   help="Optimal volume is not computed (on/*off*)")
    parser.add_argument("--show-optimal-volume", metavar="BOOL", default=True,
                   type=utils.parse_bool,
                   help="(default: TRUE)")
    parser.add_argument("--threads", default=1, type=int, metavar="NUM_THREADS",
                   help="the number of threads to use by a LP solver, "
                   "this option is used when the solver is pulp-cbc-cmd")
    parser.add_argument("-O", "--option", action="append", default=[],
                   help="Options for LP solver")
    parser.add_argument("--skip-infeasible", default=False, type=utils.parse_bool,
                   help="skip infeasible (on/*off*)")
    return parser

def json2complex(args, jsonFile, complexFile):
    with open(jsonFile) as f:
        complexData = json.load(f)
    with open(complexFile,'w') as f:
        for cycle in complexData['result']:
            print ('#' +' '+ str(cycle['birth-time']) + ' ' + str(cycle['death-time']), file = f) 
            for simplex in cycle['boundary-symbols']:
                print(" ".join(simplex), file = f)

def main():
    parser = argparse.ArgumentParser(description = 'calculate volume optimal cycles from idiagram files')
    parser = argumentParser(parser)
    args = parser.parse_args()
    for file in args.files:
        print ("Processing " + file + "...")
        jsonFile = os.path.splitext(file)[0] + '.json'
        cycleFile = os.path.splitext(file)[0]+ '.complex2'
# this is too slow...
#        voCommand = ['python', '-m', 'homcloud.optimal_volume', '-d', str(args.degree), '-X', args.xrange, '-Y', args.yrange, '-j', jsonFile, '-c', args.cut_off, '-n', args.retry, file]
#        subprocess.call(voCommand)
        diagram = PD.load_from_indexed_diphafile(file, args.degree, True)
        geom_resolver = diagram.geometry_resolver()
        vocfinder = optimal_volume.VolumeOptimalCycleFinder.from_args(diagram, geom_resolver, args)
        spatial_searcher = optimal_volume.build_spatial_searcher(diagram)
        query_args =optimal_volume.build_query_args(args)
        query = optimal_volume.RectangleQuery(args.x_range, args.y_range, spatial_searcher,
                               vocfinder, diagram.index_map, **query_args)
        query.invoke()
        with open(jsonFile, "w") as f:
            json.dump(query.to_jsondict(), f)
        json2complex(args, jsonFile, cycleFile)


if __name__ == '__main__':
    main()
