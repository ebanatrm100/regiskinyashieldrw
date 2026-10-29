"""Image Studio tab: describe a picture, pick a style and shape, optionally upload a reference photo, create AI images, download them.
Works without any key too: it then shows the strong prompt it built so the person can use it in any image tool. Four languages."""
from __future__ import annotations
import uuid
import image_gen as IG
import attachments as AT
import web_photos as WP

U = {
    "en": dict(tcreate="Create with AI", tfind="Find real photos online", fq="What photos do you want to find?", fph="for example: tomato harvest in Rwanda", fgo="Search photos", more="Show more", opens="Open source page", nores="No photos found. Try other words, or the English word.", srcs="Searched", live="{r} of {t} image services ready", queue="people waiting: {w}", again="New variation of the same idea",
               tab="Image Studio", title="Create pictures with AI", idea="Describe the picture you want", ph="A farmer carrying ripe tomatoes at sunrise, Rwandan hills in the background",
               style="Style", shape="Shape", count="How many pictures", ref="Optional: a photo to base the new picture on (edit or variation)", better="Make my description stronger automatically",
               go="Create picture", prompt="Prompt that will be used", need="Describe the picture first.", status="Image services ready", none="No image service is switched on yet.", copy="Copy this prompt into any image tool:",
               dl="Download", sq="Square 1:1", land="Landscape 16:9", port="Portrait 9:16", l43="Landscape 4:3", p34="Portrait 3:4", tip="Tip: change one thing at a time and keep any text inside the picture very short.",
               made="Created by"),
    "fr": dict(tcreate="Créer avec l'IA", tfind="Trouver de vraies photos en ligne", fq="Quelles photos cherchez-vous ?", fph="par exemple : récolte de tomates au Rwanda", fgo="Chercher des photos", more="Afficher plus", opens="Ouvrir la page source", nores="Aucune photo trouvée. Essayez d'autres mots, ou le mot en anglais.", srcs="Sources interrogées", live="{r} services d'images prêts sur {t}", queue="personnes en attente : {w}", again="Nouvelle variante de la même idée",
               tab="Studio d'images", title="Créer des images avec l'IA", idea="Décrivez l'image souhaitée", ph="Un agriculteur portant des tomates mûres au lever du soleil, collines rwandaises en arrière-plan",
               style="Style", shape="Format", count="Nombre d'images", ref="Facultatif : une photo comme base (modification ou variante)", better="Renforcer automatiquement ma description",
               go="Créer l'image", prompt="Prompt utilisé", need="Décrivez d'abord l'image.", status="Services d'images prêts", none="Aucun service d'images n'est encore activé.", copy="Copiez ce prompt dans n'importe quel outil d'image :",
               dl="Télécharger", sq="Carré 1:1", land="Paysage 16:9", port="Portrait 9:16", l43="Paysage 4:3", p34="Portrait 3:4", tip="Astuce : changez une seule chose à la fois et gardez le texte dans l'image très court.",
               made="Créée par"),
    "rw": dict(tcreate="Kora ukoresheje AI", tfind="Shakisha amafoto nyakuri kuri interineti", fq="Ni ayahe mafoto ushaka?", fph="urugero: isarura ry'inyanya mu Rwanda", fgo="Shakisha amafoto", more="Erekana andi", opens="Fungura urupapuro rw'inkomoko", nores="Nta mafoto yabonetse. Gerageza andi magambo cyangwa ijambo mu Cyongereza.", srcs="Ahashakishijwe", live="Serivisi {r} kuri {t} ziteguye", queue="abategereje: {w}", again="Indi verisiyo y'igitekerezo kimwe",
               tab="Aho gukorera amashusho", title="Kora amashusho ukoresheje AI", idea="Sobanura ishusho ushaka", ph="Umuhinzi ukoze inyanya zeze mu rukerera, imisozi y'u Rwanda inyuma",
               style="Uburyo", shape="Ingano", count="Umubare w'amashusho", ref="Bitari ngombwa: ifoto yo gushingiraho (guhindura cyangwa indi verisiyo)", better="Kongera gukomeza ibisobanuro byanjye byikora",
               go="Kora ishusho", prompt="Prompt izakoreshwa", need="Banza usobanure ishusho.", status="Serivisi z'amashusho ziteguye", none="Nta serivisi y'amashusho irashyirwaho.", copy="Koporora iyi prompt mu gikoresho icyo ari cyo cyose cy'amashusho:",
               dl="Kuramo", sq="Kare 1:1", land="Landscape 16:9", port="Portrait 9:16", l43="Landscape 4:3", p34="Portrait 3:4", tip="Inama: hindura ikintu kimwe icyarimwe kandi inyandiko iri mu shusho ibe ngufi cyane.",
               made="Yakozwe na"),
    "sw": dict(tcreate="Unda kwa AI", tfind="Tafuta picha halisi mtandaoni", fq="Unataka kutafuta picha gani?", fph="mfano: mavuno ya nyanya Rwanda", fgo="Tafuta picha", more="Onyesha zaidi", opens="Fungua ukurasa wa chanzo", nores="Hakuna picha zilizopatikana. Jaribu maneno mengine, au neno la Kiingereza.", srcs="Vilivyotafutwa", live="Huduma {r} kati ya {t} za picha ziko tayari", queue="wanaosubiri: {w}", again="Toleo jipya la wazo lilelile",
               tab="Studio ya Picha", title="Unda picha kwa AI", idea="Eleza picha unayotaka", ph="Mkulima amebeba nyanya zilizoiva alfajiri, vilima vya Rwanda nyuma",
               style="Mtindo", shape="Umbo", count="Idadi ya picha", ref="Hiari: picha ya kutumia kama msingi (kuhariri au toleo jingine)", better="Imarisha maelezo yangu kiotomatiki",
               go="Unda picha", prompt="Prompt itakayotumika", need="Eleza picha kwanza.", status="Huduma za picha tayari", none="Hakuna huduma ya picha iliyowashwa bado.", copy="Nakili prompt hii kwenye zana yoyote ya picha:",
               dl="Pakua", sq="Mraba 1:1", land="Mlalo 16:9", port="Wima 9:16", l43="Mlalo 4:3", p34="Wima 3:4", tip="Kidokezo: badilisha kitu kimoja kwa wakati na weka maandishi ndani ya picha mafupi sana.",
               made="Imeundwa na"),
}
TAB = {k: v["tab"] for k, v in U.items()}


def _uid(st):
    if "kinyashield_uid" not in st.session_state:
        st.session_state["kinyashield_uid"] = uuid.uuid4().hex
    return st.session_state["kinyashield_uid"]


def render(st, lang):
    k = lang if lang in U else "en"
    u = U[k]
    st.subheader(u["title"])
    t_create, t_find = st.tabs([u["tcreate"], u["tfind"]])
    with t_create:
        _create(st, k, u)
    with t_find:
        _find(st, k, u)


def _create(st, k, u):
    avail = IG.configured()
    if avail:
        stt = IG.status()
        line = u["status"] + ": " + ", ".join(avail) + " · " + u["live"].format(r=stt["ready"], t=stt["total"])
        if stt["waiting"]:
            line += " · " + u["queue"].format(w=stt["waiting"])
        st.caption(line)
    else:
        st.caption(u["none"])
    idea = st.text_area(u["idea"], placeholder=u["ph"], key=f"studio_idea_{k}", height=110)
    c1, c2, c3 = st.columns(3)
    sids = list(IG.STYLES)
    style = c1.selectbox(u["style"], sids, format_func=lambda s: IG.STYLES[s][0][k], key=f"studio_style_{k}")
    shapes = {"1:1": u["sq"], "16:9": u["land"], "9:16": u["port"], "4:3": u["l43"], "3:4": u["p34"]}
    aspect = c2.selectbox(u["shape"], list(shapes), format_func=lambda a: shapes[a], key=f"studio_aspect_{k}")
    n = c3.slider(u["count"], 1, 4, 1, key=f"studio_n_{k}")
    better = st.checkbox(u["better"], value=True, key=f"studio_better_{k}")
    up = st.file_uploader(u["ref"], type=list(AT.IMG_EXTS), key=f"studio_ref_{k}")
    prompt = ""
    if idea.strip():
        try:
            prompt = IG.build_prompt(idea, style, aspect) if better else idea.strip()
        except IG.ImageGenError:
            prompt = ""
    if prompt:
        with st.expander(u["prompt"]):
            st.code(prompt, language=None)
    st.caption(u["tip"])
    sig_key, var_key = f"studio_sig_{k}", f"studio_var_{k}"
    sig = (prompt, aspect, n, bool(up))
    repeat = st.session_state.get(sig_key) == sig and bool(st.session_state.get(f"studio_out_{k}"))
    if st.button(u["again"] if repeat else u["go"], key=f"studio_go_{k}", type="primary"):
        if not idea.strip():
            st.warning(u["need"])
            return
        ref = None
        try:
            if up is not None:
                data = up.getvalue()
                got = AT.read([(up.name, data)])
                ref = (got["images"][0][0], got["images"][0][1])
        except AT.AttachError as e:
            st.warning(AT.message(str(e), k))
            return
        ok, wait = IG.fair_use(_uid(st), n)
        if not ok:
            st.warning(IG.friendly_error(IG.ImageGenError(f"limit:{int(wait)}"), k))
            return
        variant = (st.session_state.get(var_key, 0) + 1) if repeat else 0
        try:
            with st.spinner("…"):
                res = IG.generate(prompt, aspect, n, ref, variant=variant)
            for _k in [x for x in st.session_state if str(x).startswith("studio_out_")]:
                st.session_state.pop(_k, None)          # keep only the newest pictures per visitor (memory on a busy server)
            st.session_state[f"studio_out_{k}"] = res
            st.session_state[sig_key], st.session_state[var_key] = sig, variant
        except IG.ImageGenError as e:
            st.session_state.pop(f"studio_out_{k}", None)
            st.warning(IG.friendly_error(e, k))
            if str(e) == "not_configured" and prompt:
                st.caption(u["copy"])
                st.code(prompt, language=None)
    out = st.session_state.get(f"studio_out_{k}")
    if out:
        cols = st.columns(min(len(out), 2) or 1)
        for i, (data, mime, prov) in enumerate(out):
            with cols[i % len(cols)]:
                try:
                    st.image(data, use_container_width=True)
                except TypeError:
                    st.image(data)
                st.caption(f"{u['made']} {prov}")
                st.download_button(u["dl"], data, file_name=f"kinyashield_image_{i + 1}." + ("jpg" if mime == "image/jpeg" else "webp" if mime == "image/webp" else "png"), mime=mime, key=f"studio_dl_{k}_{i}")
        st.caption(IG.DISCLOSE[k])


def _find(st, k, u):
    q = st.text_input(u["fq"], placeholder=u["fph"], key=f"studio_fq_{k}")
    page_key, last_key, res_key = f"studio_fpage_{k}", f"studio_flast_{k}", f"studio_fres_{k}"
    c1, c2 = st.columns([1, 1])
    go = c1.button(u["fgo"], key=f"studio_fgo_{k}", type="primary")
    more = c2.button(u["more"], key=f"studio_fmore_{k}")
    if (go or more) and q.strip():
        page = 1 if (go or st.session_state.get(last_key) != q.strip()) else st.session_state.get(page_key, 1) + 1
        with st.spinner("…"):
            r = WP.search(q.strip(), page)
        st.session_state[page_key], st.session_state[last_key] = page, q.strip()
        if more and st.session_state.get(res_key) and st.session_state[last_key] == q.strip() and page > 1:
            have = {i["thumb"] for i in st.session_state[res_key]["items"]}
            r = dict(r, items=st.session_state[res_key]["items"] + [i for i in r["items"] if i["thumb"] not in have])
        st.session_state[res_key] = r
    r = st.session_state.get(res_key)
    if not r:
        return
    if r.get("blocked"):
        st.info(WP.BLOCKED[k])
        return
    if not r["items"]:
        st.info(u["nores"])
        return
    cols = st.columns(3)
    for i, it in enumerate(r["items"]):
        with cols[i % 3]:
            try:
                st.image(it["thumb"], use_container_width=True)
            except TypeError:
                st.image(it["thumb"])
            st.caption(WP.credit(it))
            st.markdown(f"[{u['opens']}]({it['page']})")
    st.caption(u["srcs"] + ": " + ", ".join(nm for nm, c in r["sources"].items() if c))
    st.caption(WP.NOTE[k])
