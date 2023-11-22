import subprocess as sp
from ifcexport import exporter
import multiprocessing as mp

def export_service(source, target):
    proc = sp.Popen(f'python ifcexport.py "{source}" --name {target}'.split(' '), stdin=sp.PIPE, stdout=sp.PIPE,
                    stderr=sp.PIPE)
