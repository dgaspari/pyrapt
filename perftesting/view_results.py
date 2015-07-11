import pstats
p = pstats.Stats('perftesting/example_run_profile1')
p.sort_stats('time').print_stats()
