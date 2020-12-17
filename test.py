import threading
import argparse
import os, sys
import subprocess
from os.path import expanduser

class Executable(object):
    def __init__(self, cmd, working_dir=None):
        self.cmd = cmd
        self.working_dir = working_dir
        self.process = None
        self.out = None
        self.error = None
        self.exitcode = None
    
    def run_params(self, timeout=3):
        print(self.cmd)
        def target():
            self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.working_dir, preexec_fn=os.setsid)
            self.out, self.error = self.process.communicate()
            self.exitcode = self.process.returncode
        thread = threading.Thread(target=target)
        thread.start()
        thread.join()
        if thread.is_alive():
            # print 'Timeout!'
            os.killpg(self.process.pid, signal.SIGTERM)
            self.process.kill()
            # thread.join()
            # print "join() done"
            return []
        return self.exitcode, self.out, self.error

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--piacin', dest='piacin', action='store_const', const=True, default=False, help='Use piacin (default: False))')
    parser.add_argument('--pypy', dest='pypy', action='store_const', const=True, default=False, help='Use PyPy (default: False))')
    parser.add_argument('bms', help='the benchmark .py script to execute', nargs="+" )
    
    parser.add_argument("-r", "--runs", type=int, default=20, help="Number of time to repeat a single benchmark (default:20")
    parser.add_argument("-n", "--number", type=int, default=100, help="Number of time to repeat execution (default: 100)")
    parser.add_argument("-k", "--bmnumber", type=int, default=50, help="Number of time to repeat benchmark within run (default: 50)")
    parser.add_argument("-c", "--clean", dest="clean", action="store_const", const=True, default=False, help="Clean the piacin bag")

    args = parser.parse_args()

    cmd = which("python")
    if args.pypy:
        cmd = which("pypy")

    for bm in args.bms:
        for run in range(args.runs):
            # get the name of the benchmark
            bm_name = os.path.splitext(bm)[0]
            bag_location = os.path.join(os.path.expanduser("~"), ".piacin")
            bag_file = os.path.join(bag_location, "piacin_hc_bag_%s.pkl" % (bm_name))

            # delete the bag when starting a new run
            bag = os.path.join(bag_location, bag_file)
            try:
                os.remove(bag)
            except OSError:
                print("cannot delete bag")
                # sys.exit(-1)
                pass

            # set up arguments
            cmdarg = None
            if args.piacin:
                cmdarg = " ".join([cmd, bm, "--piacin", "-k", str(args.bmnumber)])
            else:
                cmdarg = " ".join([cmd, bm, "-k", str(args.bmnumber)])

            exe = Executable(cmdarg, os.getcwd())
            log_filename = "./result/hc/log_%s_n_%d_bm_%d_%s_piacin_%d_run_%02d.txt" % (bm, args.number, args.bmnumber, os.path.split(cmd)[1], 1 if args.piacin else 0, run)
            log = open(log_filename, "w")
            print("run %d / %d" % (run + 1, args.runs))
            for i in range(args.number):
                print("execution %d / %d" % ((i + 1), args.number))
                exit_code, out, err = exe.run_params()
                if exit_code != 0:
                    print(err)
                    exit()
                log.write(out.decode()) 
                log.flush()
            log.close()