import pstats
p = pstats.Stats('example_run_profile4')
p.sort_stats('time').print_stats()
