"""Image Studio tab: describe a picture, pick a style and shape, optionally upload a reference photo, create AI images, download them.
Works without any key too: it then shows the strong prompt it built so the person can use it in any image tool. Four languages."""
from __future__ import annotations
import image_gen as IG
import attachments as AT

U = {
    "en": dict(tab="Image Studio", title="Create pictures with AI", idea="Describe the picture you want", ph="A farmer carrying ripe tomatoes at sunrise, Rwandan hills in the background",
               style="Style", shape="Shape", count="How many pictures", ref="Optional: a photo to base the new picture on (edit or variation)", better="Make my description stronger automatically",
               go="Create picture", prompt="Prompt that will be used", need="Describe the picture first.", status="Image services ready", none="No image service is switched on yet.", copy="Copy this prompt into any image tool:",
               dl="Download", sq="Square 1:1", land="Landscape 16:9", port="Portrait 9:16", l43="Landscape 4:3", p34="Portrait 3:4", tip="Tip: change one thing at a time and keep any text inside the picture very short.",
               made="Created by"),
    "fr": dict(tab="Studio d'images", title="Créer des images avec l'IA", idea="Décrivez l'image souhaitée", ph="Un agriculteur portant des tomates mûres au lever du soleil, collines rwandaises en arrière-plan",
               style="Style", shape="Format", count="Nombre d'images", ref="Facultatif : une photo comme base (modification ou variante)", better="Renforcer automatiquement ma description",
               go="Créer l'image", prompt="Prompt utilisé", need="Décrivez d'abord l'image.", status="Services d'images prêts", none="Aucun service d'images n'est encore activé.", copy="Copiez ce prompt dans n'importe quel outil d'image :",
               dl="Télécharger", sq="Carré 1:1", land="Paysage 16:9", port="Portrait 9:16", l43="Paysage 4:3", p34="Portrait 3:4", tip="Astuce : changez une seule chose à la fois et gardez le texte dans l'image très court.",
               made="Créée par"),
    "rw": dict(tab="Aho gukorera amashusho", title="Kora amashusho ukoresheje AI", idea="Sobanura ishusho ushaka", ph="Umuhinzi ukoze inyanya zeze mu rukerera, imisozi y'u Rwanda inyuma",
               style="Uburyo", shape="Ingano", count="Umubare w'amashusho", ref="Bitari ngombwa: ifoto yo gushingiraho (guhindura cyangwa indi verisiyo)", better="Kongera gukomeza ibisobanuro byanjye byikora",
               go="Kora ishusho", prompt="Prompt izakoreshwa", need="Banza usobanure ishusho.", status="Serivisi z'amashusho ziteguye", none="Nta serivisi y'amashusho irashyirwaho.", copy="Koporora iyi prompt mu gikoresho icyo ari cyo cyose cy'amashusho:",
               dl="Kuramo", sq="Kare 1:1", land="Landscape 16:9", port="Portrait 9:16", l43="Landscape 4:3", p34="Portrait 3:4", tip="Inama: hindura ikintu kimwe icyarimwe kandi inyandiko iri mu shusho ibe ngufi cyane.",
               made="Yakozwe na"),
    "sw": dict(tab="Studio ya Picha", title="Unda picha kwa AI", idea="Eleza picha unayotaka", ph="Mkulima amebeba nyanya zilizoiva alfajiri, vilima vya Rwanda nyuma",
               style="Mtindo", shape="Umbo", count="Idadi ya picha", ref="Hiari: picha ya kutumia kama msingi (kuhariri au toleo jingine)", better="Imarisha maelezo yangu kiotomatiki",
               go="Unda picha", prompt="Prompt itakayotumika", need="Eleza picha kwanza.", status="Huduma za picha tayari", none="Hakuna huduma ya picha iliyowashwa bado.", copy="Nakili prompt hii kwenye zana yoyote ya picha:",
               dl="Pakua", sq="Mraba 1:1", land="Mlalo 16:9", port="Wima 9:16", l43="Mlalo 4:3", p34="Wima 3:4", tip="Kidokezo: badilisha kitu kimoja kwa wakati na weka maandishi ndani ya picha mafupi sana.",
               made="Imeundwa na"),
}
TAB = {k: v["tab"] for k, v in U.items()}


def render(st, lang):
    k = lang if lang in U else "en"
    u = U[k]
    st.subheader(u["title"])
    avail = IG.configured()
    st.caption((u["status"] + ": " + ", ".join(avail)) if avail else u["none"])
    idea = st.text_area(u["idea"], placeholder=u["ph"], key=f"studio_idea_{k}", height=110)
    c1, c2, c3 = st.columns(3)
    sids = list(IG.STYLES)
    style = c1.selectbox(u["style"], sids, format_func=lambda s: IG.STYLES[s][0][k], key=f"studio_style_{k}")
    shapes = {"1:1": u["sq"], "16:9": u["land"], "9:16": u["port"], "4:3": u["l43"], "3:4": u["p34"]}
    aspect = c2.selectbox(u["shape"], list(shapes), format_func=lambda a: shapes[a], key=f"studio_aspect_{k}")
    n = c3.slider(u["count"], 1, 3, 1, key=f"studio_n_{k}")
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
    if st.button(u["go"], key=f"studio_go_{k}", type="primary"):
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
        try:
            with st.spinner("…"):
                res = IG.generate(prompt, aspect, n, ref)
            st.session_state[f"studio_out_{k}"] = res
        except IG.ImageGenError as e:
            st.session_state.pop(f"studio_out_{k}", None)
            st.warning(IG.friendly_error(e, k))
            if str(e) == "not_configured" and prompt:
                st.caption(u["copy"])
                st.code(prompt, language=None)
    out = st.session_state.get(f"studio_out_{k}")
    if out:
        cols = st.columns(len(out))
        for i, (data, mime, prov) in enumerate(out):
            with cols[i]:
                try:
                    st.image(data, use_container_width=True)
                except TypeError:
                    st.image(data)
                st.caption(f"{u['made']} {prov}")
                st.download_button(u["dl"], data, file_name=f"kinyashield_image_{i + 1}." + ("jpg" if mime == "image/jpeg" else "webp" if mime == "image/webp" else "png"), mime=mime, key=f"studio_dl_{k}_{i}")
        st.caption(IG.DISCLOSE[k])
