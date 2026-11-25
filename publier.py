"""Publie TOUS les essais vidéo sur une page web (GitHub Pages) : compresse chaque rendu pour le web, génère index.html, push.
python publier.py [--sans-push]"""
import os, sys, glob, json, subprocess, html, datetime

S = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(S, 'v'); os.makedirs(V, exist_ok=True)
T = os.path.join(S, '..', 'tests_code')
DESC = json.load(open(os.path.join(S, 'descriptions.json'), encoding='utf-8'))

# ordre d'affichage : sections → motifs de fichiers
SECTIONS = [
    ('À voir en premier', [os.path.join(T, 'gpu', 'rendus', n) for n in ('best_of_pour_Yan.mp4', 'mini_scene_enchainee.mp4')]),
    ('Version qualité (nouveaux essais)', sorted(glob.glob(os.path.join(T, 'gpu', 'rendus', 'H*.mp4')))),
    ('Version 2 : carte graphique', sorted(glob.glob(os.path.join(T, 'gpu', 'rendus', 'G*.mp4')), key=lambda p: os.path.basename(p))),
    ('Version 1 : premiers essais', sorted(glob.glob(os.path.join(T, 'rendus', '[A-E]*.mp4')))),
]
EXCLURE = ('GPU_', 'tests_', 'best_of_tg')
MASQUES = set(json.load(open(os.path.join(S, 'masques.json'), encoding='utf-8'))) if os.path.exists(os.path.join(S, 'masques.json')) else set()


def web(src):
    nom = os.path.splitext(os.path.basename(src))[0]
    dst, pos = os.path.join(V, nom + '.mp4'), os.path.join(V, nom + '.jpg')
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', 'scale=960:-2', '-c:v', 'libx264', '-crf', '27', '-preset', 'slow',
                        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', dst], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1.5', '-i', dst, '-frames:v', '1', '-vf', 'scale=480:-2', pos], check=True)
    return nom


def page():
    blocs = []
    for titre, fichiers in SECTIONS:
        cartes = []
        for f in fichiers:
            if not os.path.exists(f) or os.path.basename(f).startswith(EXCLURE) or os.path.splitext(os.path.basename(f))[0] in MASQUES: continue
            nom = web(f)
            d = DESC.get(nom, {})
            t, txt = d.get('titre', nom.replace('_', ' ')), d.get('texte', '')
            cartes.append(f'''<figure><video src="v/{nom}.mp4" poster="v/{nom}.jpg" controls loop muted playsinline preload="none"></video>
<figcaption><b>{html.escape(t)}</b>{('<br>' + html.escape(txt)) if txt else ''}</figcaption></figure>''')
        if cartes:
            blocs.append(f'<h2>{html.escape(titre)}</h2><div class="grille">' + '\n'.join(cartes) + '</div>')
    maj = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
    doc = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Essais vidéo du spectacle</title>
<style>
body{{margin:0;background:#0d0d0f;color:#e8e6e3;font:16px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}}
header{{padding:28px 20px 8px;max-width:1300px;margin:auto}} h1{{margin:0 0 6px;font-size:26px}} header p{{margin:4px 0;color:#aaa}}
h2{{max-width:1300px;margin:34px auto 12px;padding:0 20px;font-size:20px;border-bottom:1px solid #333;padding-bottom:6px}}
.grille{{max-width:1300px;margin:auto;padding:0 20px;display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:18px}}
figure{{margin:0;background:#17171a;border-radius:10px;overflow:hidden}} video{{width:100%;display:block;aspect-ratio:16/9;background:#000}}
figcaption{{padding:10px 12px;font-size:14px;color:#cfcac4}} figcaption b{{color:#fff}}
footer{{color:#777;font-size:13px;text-align:center;padding:30px}}
</style></head><body><header><h1>Essais vidéo du spectacle</h1>
<p>Tous les essais d'effets, faits en code (simulation de fumée, feu et particules) à partir des vidéos du spectacle. Rien n'est définitif : ce sont des tests pour choisir une direction.</p>
<p>Mis à jour le {maj}. La page se complète au fur et à mesure.</p></header>
{''.join(blocs)}<footer>Essais faits avec Claude</footer></body></html>'''
    open(os.path.join(S, 'index.html'), 'w', encoding='utf-8').write(doc)


def push():
    g = ['git', '-C', S]
    subprocess.run(g + ['add', '-A'], check=True)
    if subprocess.run(g + ['diff', '--cached', '--quiet']).returncode:
        subprocess.run(g + ['commit', '-q', '-m', 'Mise à jour des essais\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'], check=True)
        subprocess.run(g + ['push', '-q', 'origin', 'main'], check=True)
        print('poussé')
    else:
        print('rien de neuf')


if __name__ == '__main__':
    page()
    if '--sans-push' not in sys.argv: push()
