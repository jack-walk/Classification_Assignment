
const urlSegments = "babydog_to_annotate.csv";
const SEED = 303;

let videos = [];
let queue = [];
let labels = [];
let reviewer = "";

const $ = (id) => document.getElementById(id);

function mulberry32(a) {
  return function () {
    a |= 0; a = a + 0x6d2b79f5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

function shuffle(items, seed) {
  const rand = mulberry32(seed);
  for (let i = items.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [items[i], items[j]] = [items[j], items[i]];
  }
  return items;
}

function parseCsv(text) {
  const rows = [];
  let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ",") { row.push(field); field = ""; }
    else if (c === "\n") { row.push(field); rows.push(row); row = []; field = ""; }
    else if (c !== "\r") field += c;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  const header = rows.shift();
  return rows.map((r) => Object.fromEntries(header.map((h, j) => [h, r[j]])));
}

function loadVideos(text) {
  videos = parseCsv(text);
  shuffle(videos, SEED);
  $("status").textContent = `${videos.length} videos loaded.`;
  $("file-row").hidden = true;
}

function storageKey() { return "babydog-labels:" + reviewer; }
function readLabels() {
  try { return JSON.parse(localStorage.getItem(storageKey())) || []; } catch (e) { return []; }
}
function saveLabels() {
  try { localStorage.setItem(storageKey(), JSON.stringify(labels)); } catch (e) { /* labels still download */ }
}

function start() {
  reviewer = $("reviewer").value.trim();
  if (!reviewer || videos.length === 0) return;
  labels = readLabels();
  const done = new Set(labels.map((l) => l.video_id));
  queue = videos.filter((v) => !done.has(v.video_id));
  $("setup").hidden = true;
  show();
}

function show() {
  const v = queue[0];
  $("labeler").hidden = !v;
  $("done").hidden = !!v;
  if (!v) return;
  $("progress").textContent = `${labels.length + 1} of ${videos.length}  |  ${reviewer}`;
  $("player").src = `https://www.youtube.com/embed/${v.video_id}?rel=0`;
  $("text").textContent = v.title;
  $("date").textContent = v.date;
}

function answer(value) {
  const v = queue.shift();
  if (!v) return;
  labels.push({ video_id: v.video_id, contains_babydog_human: value, reviewer: reviewer });
  saveLabels();
  show();
}

function undo() {
  const last = labels.pop();
  if (!last) return;
  queue.unshift(videos.find((v) => v.video_id === last.video_id));
  saveLabels();
  show();
}

function csvCell(value) {
  const s = String(value ?? "");
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}

function download() {
  const header = ["video_id", "contains_babydog_human", "reviewer"];
  const lines = [header.join(",")].concat(labels.map((l) => header.map((h) => csvCell(l[h])).join(",")));
  const blob = new Blob([lines.join("\n") + "\n"], { type: "text/csv" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `babydog_labels_${reviewer || "reviewer"}.csv`;
  a.click();
  URL.revokeObjectURL(a.href);
}

$("start").addEventListener("click", start);
$("reviewer").addEventListener("keydown", (e) => { if (e.key === "Enter") start(); });
$("undo").addEventListener("click", undo);
$("download").addEventListener("click", download);
document.querySelectorAll("[data-answer]").forEach((b) => b.addEventListener("click", () => answer(b.dataset.answer)));
document.addEventListener("keydown", (e) => {
  if ($("labeler").hidden || e.target.tagName === "INPUT") return;
  if (e.key.toLowerCase() === "y") answer("True");
  if (e.key.toLowerCase() === "n") answer("False");
  if (e.key.toLowerCase() === "s") answer("");
  if (e.key.toLowerCase() === "b") undo();
});
$("file").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (file) loadVideos(await file.text());
});

fetch(urlSegments)
  .then((r) => { if (!r.ok) throw new Error(r.status); return r.text(); })
  .then(loadVideos)
  .catch(() => {
    $("status").textContent = "";
    $("file-row").hidden = false;
  });
