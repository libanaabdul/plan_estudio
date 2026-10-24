"""Genera frontend/study-guide.js a partir de guide_*.py.

Uso (desde la raíz del repo):  python3 tools/study-plan/build_guide.py

Cada sesión cert de INITIAL (plan === PLAN_VERSION en frontend/index.html) debe
tener su guía; el script falla si falta alguna o si sobra una que ya no existe.
Formato mini-markdown (lo renderiza renderGuide() en index.html):
  ## título · - viñeta (anidar con 2 espacios) · 1. paso · > trampa/tip
  ? pregunta :: respuesta (desplegable) · ``` bloque ``` · `código` · **negrita**
"""
import importlib.util, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
INDEX = os.path.join(ROOT, 'frontend', 'index.html')
OUT = os.path.join(ROOT, 'frontend', 'study-guide.js')

G = {}
for mod in ['guide_cp', 'guide_tf', 'guide_aif', 'guide_cca', 'guide_saa']:
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, mod + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    dup = set(G) & set(m.G)
    assert not dup, f'guías duplicadas: {dup}'
    G.update({k: v.strip() for k, v in m.G.items()})

html = open(INDEX, encoding='utf8').read()
version = re.search(r"const PLAN_VERSION='([^']+)'", html).group(1)
names = [json.loads('"' + l.split('{name:"', 1)[1].split('",date:', 1)[0] + '"')
         for l in html.split('\n') if l.startswith('{name:') and f'plan:"{version}"' in l]
missing = [n for n in names if n not in G]
extra = [k for k in G if k not in names]
if missing or extra:
    print('Sin guía:', missing)
    print('Guías sin sesión:', extra)
    sys.exit(1)

with open(OUT, 'w', encoding='utf8') as fh:
    fh.write('// Guías de estudio detalladas por sesión del plan (clave = nombre del ítem).\n')
    fh.write('// GENERADO por tools/study-plan/build_guide.py — no editar a mano.\n')
    fh.write('window.STUDY_GUIDE=')
    json.dump({n: G[n] for n in names}, fh, ensure_ascii=False, indent=0)
    fh.write(';\n')
print(f'{OUT}: {len(names)} guías (plan {version})')
