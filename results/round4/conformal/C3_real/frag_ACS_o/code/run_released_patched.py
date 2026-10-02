"""Runs a released script unmodified after replacing concurrent.futures.process._check_system_limits
by a no-op (this sandbox refuses os.sysconf('SC_SEM_NSEMS_MAX'); the check only guards the semaphore limit)."""
import sys, runpy, concurrent.futures.process as P
P._check_system_limits = lambda: None
script = sys.argv[1]; sys.argv = [script] + sys.argv[2:]
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.dirname(script)) + '/..')
runpy.run_path(script, run_name='__main__')
