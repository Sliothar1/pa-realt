"""pa-core data path for the monument table (vendored pa-core, pinned; see vendor/pa-core/VENDORED.md):
ingest data/monuments.csv (+ meta) -> data/d4m/A_mon, A_prov; validate (incl. byte round-trip);
default-deny export -> build/d4m-export; site/data/sites.json + standing.json; D4M side triples A_prop/A_sky.
Run after build_data.py:  python3 scripts/d4m_build.py"""
import json, os, subprocess, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
CLI = [sys.executable, 'vendor/pa-core/pa_d4m.py']; S = ['--schema', 'data/d4m/schema.json']
run = lambda *a: subprocess.run(list(a), check=True)
run(*CLI, 'ingest', 'tabular', '--config', 'data/d4m/tabular.json', *S, '--out', 'data/d4m')
run(sys.executable, 'scripts/d4m_triples.py')
run(*CLI, 'validate', 'data/d4m', *S, '--roundtrip', 'data/d4m/tabular.json')
run(*CLI, 'export', 'data/d4m', *S, '--allow', 'data/d4m/export.allow.json', '--to', 'build/d4m-export')
run(sys.executable, 'scripts/site_data.py')
