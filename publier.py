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
    cartes = []
    for titre, fichiers in SECTIONS:
        for f in fichiers:
            if not os.path.exists(f) or os.path.basename(f).startswith(EXCLURE) or os.path.splitext(os.path.basename(f))[0] in MASQUES: continue
            nom = web(f)
            d = DESC.get(nom, {})
            t, txt = d.get('titre', nom.replace('_', ' ')), d.get('texte', '')
            cartes.append(f'''<figure data-id="{nom}"><div class="poignee" aria-label="Déplacer">⠿</div>
<video src="v/{nom}.mp4" poster="v/{nom}.jpg" controls loop muted playsinline preload="none"></video>
<figcaption><b>{html.escape(t)}</b>{('<br>' + html.escape(txt)) if txt else ''}<span class="sec">{html.escape(titre)}</span></figcaption></figure>''')
    maj = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
    doc = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Essais vidéo du spectacle</title>
<style>
body{{margin:0;background:#0d0d0f;color:#e8e6e3;font:16px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}}
header{{padding:22px 16px 6px;max-width:1300px;margin:auto}} h1{{margin:0 0 6px;font-size:24px}} header p{{margin:4px 0;color:#aaa;font-size:14px}}
.barre{{padding:6px 16px;display:flex;gap:8px;flex-wrap:wrap;max-width:1300px;margin:auto}}
.barre button{{background:#26262b;color:#eee;border:1px solid #3a3a40;border-radius:16px;padding:6px 11px;font-size:13px}}
#liste{{max-width:1300px;margin:auto;padding:6px 16px 20px;display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px}}
figure{{margin:0;background:#17171a;border-radius:10px;overflow:hidden;position:relative}}
video{{width:100%;display:block;aspect-ratio:16/9;background:#000}}
.poignee{{position:absolute;top:6px;right:6px;z-index:3;width:46px;height:46px;border-radius:23px;background:#000a;color:#fff;font-size:26px;
 display:flex;align-items:center;justify-content:center;touch-action:none;cursor:grab;user-select:none;-webkit-user-select:none}}
figcaption{{display:none;padding:10px 12px;font-size:14px;color:#cfcac4}} figcaption b{{color:#fff}}
.sec{{display:block;margin-top:4px;font-size:12px;color:#888}}
body.textes figcaption{{display:block}}
.fantome{{opacity:.35}} .choisi{{outline:3px solid #e0a040}}
#msg{{color:#e0a040;font-size:14px;align-self:center}}
footer{{color:#777;font-size:13px;text-align:center;padding:30px}}
</style></head><body><header><h1>Essais vidéo du spectacle</h1>
<p>Tous les essais d'effets faits à partir des vidéos du spectacle. Ce sont des tests pour choisir une direction. Mis à jour le {maj}.</p>
<p>Pour changer l'ordre : appuyer sur ⠿ et glisser.</p></header>
<div class="barre"><button id="bt">Afficher les textes</button><button id="bp">Partager cet ordre</button><button id="br">Ordre d'origine</button><span id="msg"></span></div>
<div id="liste">
{chr(10).join(cartes)}
</div><footer>Essais faits avec Claude</footer>
<script src="sortable.min.js"></script>
<script>
const L = document.getElementById('liste'), K = 'ordre-essais';
const ids = () => [...L.children].map(e => e.dataset.id);
function appliquer(o) {{
  const tous = ids(), connus = o.filter(i => tous.includes(i)), nouveaux = tous.filter(i => !o.includes(i));
  nouveaux.concat(connus).forEach(i => L.appendChild(L.querySelector('[data-id="' + i + '"]')));
}}
const h = new URLSearchParams(location.hash.slice(1)).get('o');
const o = h ? h.split(',') : JSON.parse(localStorage.getItem(K) || 'null');
if (o) appliquer(o);
function garder() {{ localStorage.setItem(K, JSON.stringify(ids())); history.replaceState(null, '', '#o=' + ids().join(',')); }}
new Sortable(L, {{handle: '.poignee', forceFallback: true, fallbackTolerance: 3, scroll: true, scrollSensitivity: 90, scrollSpeed: 14, animation: 160, ghostClass: 'fantome', chosenClass: 'choisi', onEnd: garder}});
const msg = t => {{ const m = document.getElementById('msg'); m.textContent = t; setTimeout(() => m.textContent = '', 2500); }};
document.getElementById('bt').onclick = e => {{ const on = document.body.classList.toggle('textes'); e.target.textContent = on ? 'Cacher les textes' : 'Afficher les textes'; }};
document.getElementById('bp').onclick = async () => {{
  const u = location.origin + location.pathname + '#o=' + ids().join(',');
  if (navigator.share) {{ try {{ await navigator.share({{title: 'Essais vidéo', url: u}}); }} catch (e) {{}} }}
  else {{ await navigator.clipboard.writeText(u); msg('Lien copié'); }}
}};
document.getElementById('br').onclick = () => {{ localStorage.removeItem(K); location.href = location.pathname; }};
</script></body></html>'''
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
