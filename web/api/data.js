// Reads your Google Sheet and sends it to the website as JSON.
const SHEET_CSV = "https://docs.google.com/spreadsheets/d/1sO1ly233qkEqw4_bKr4s_WZwK0uAF6StDMi8pR4ZTxs/export?format=csv&gid=1030199938";

function parse(t) {
  const rows = []; let r = [], f = "", q = false;
  for (let i = 0; i < t.length; i++) {
    const c = t[i];
    if (q) { if (c === '"') { if (t[i + 1] === '"') { f += '"'; i++; } else q = false; } else f += c; }
    else if (c === '"') q = true;
    else if (c === ",") { r.push(f); f = ""; }
    else if (c === "\n" || c === "\r") { if (c === "\r" && t[i + 1] === "\n") i++; r.push(f); rows.push(r); r = []; f = ""; }
    else f += c;
  }
  if (f || r.length) { r.push(f); rows.push(r); }
  return rows;
}

module.exports = async (req, res) => {
  try {
    const text = await (await fetch(SHEET_CSV)).text();
    const [h, ...rows] = parse(text);
    const head = h.map(x => x.trim());
    const data = rows.filter(r => r.some(x => x.trim()))
      .map(r => Object.fromEntries(head.map((k, i) => [k, (r[i] || "").trim()])));
    res.setHeader("Cache-Control", "s-maxage=60, stale-while-revalidate");
    res.status(200).json(data);
  } catch (e) { res.status(500).json({ error: String(e) }); }
};
