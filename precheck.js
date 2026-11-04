// Pré-checar mídia — valida CADA URL antes de criar o container no Instagram.
// GET Range 0-1023 esperando 200/206 + content-type image/* ou video/*.
// Falhou: purga o jsDelivr, espera e tenta de novo (3x); depois tenta o host reserva (item.json.alt[url] = GitHub Pages).
// Nenhum serviu: ERRO explícito (execução fica vermelha) — nunca manda URL quebrada pro Instagram.
const TRIES = 3, WAIT_MS = 15000;
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const helpers = this.helpers;
async function probe(url) {
  try {
    const r = await helpers.httpRequest({ method: 'GET', url, headers: { Range: 'bytes=0-1023' },
      returnFullResponse: true, ignoreHttpStatusErrors: true, encoding: 'arraybuffer', timeout: 30000 });
    const ct = String((r.headers || {})['content-type'] || '');
    return { ok: (r.statusCode === 200 || r.statusCode === 206) && /^(image|video)\//.test(ct), status: r.statusCode, ct };
  } catch (e) { return { ok: false, status: 'ERR', ct: String(e.message || e).slice(0, 120) }; }
}
async function purge(url) {
  const m = url.match(/^https:\/\/(?:cdn|fastly|gcore)\.jsdelivr\.net\/(gh\/.+)$/);
  if (!m) return;
  try { await helpers.httpRequest({ method: 'GET', url: `https://purge.jsdelivr.net/${m[1]}`, timeout: 30000, ignoreHttpStatusErrors: true }); } catch (e) {}
}
async function resolve(url, alt, log) {
  for (const cand of [url, alt].filter(Boolean)) {
    for (let t = 1; t <= TRIES; t++) {
      const r = await probe(cand);
      log.push(`${t}x ${r.status} ${r.ct} ${cand}`);
      if (r.ok) return cand;
      if (t < TRIES) { await purge(cand); await sleep(WAIT_MS); }
    }
  }
  throw new Error(`Mídia indisponível após ${TRIES} tentativas em cada host: ${url}${alt ? ' | alt: ' + alt : ''}\n` + log.slice(-6).join('\n'));
}
const out = [];
for (const item of $input.all()) {
  const j = { ...item.json }; const alt = j.alt || {}; const log = [];
  const R = (u) => resolve(u, alt[u], log);
  if (j.image_url) j.image_url = await R(j.image_url);
  if (j.video_url) j.video_url = await R(j.video_url);
  if (j.cover_url) j.cover_url = await R(j.cover_url);
  if (Array.isArray(j.assetsUrls)) j.assetsUrls = await Promise.all(j.assetsUrls.map(R));
  if (Array.isArray(j.frames)) j.frames = await Promise.all(j.frames.map(async fr => ({ ...fr, url: await R(fr.url) })));
  delete j.alt;
  j.precheck_log = log;
  out.push({ json: j });
}
return out;
