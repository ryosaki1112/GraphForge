import argparse, pathlib, json
from .graph_build import build
def cli():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['new','reverse'],required=True)
    ap.add_argument('--input',type=pathlib.Path)
    ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path('build_full'))
    ap.add_argument('--log',type=pathlib.Path,default=pathlib.Path('persn_log.jsonl'))
    args=ap.parse_args()
    build().invoke({'mode':args.mode,'input':args.input,'out':args.out,'log':args.log})
    print('done')
if __name__=='__main__': cli()
