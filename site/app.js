"use strict";

const REPO = "https://github.com/mzmine/mzmine-custom-lipid-library";
const SUBMIT_URL = `${REPO}/issues/new?template=submit-lipid-class.yml`;

const state = { index: null, classes: [], selected: new Set() };
const $ = (sel) => document.querySelector(sel);

/** Creates an element; children may be nodes or strings (always inserted as text). */
function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "class") node.className = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else node.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

/** Only http(s) links from submitted data are rendered as links. */
function safeUrl(url) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:" || parsed.protocol === "http:" ? parsed.href : null;
  } catch {
    return null;
  }
}

function humanize(enumName) {
  if (!enumName) return "";
  const s = enumName.toLowerCase().replaceAll("_", " ");
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function categoryLabel(category) {
  return state.index.categoryLabels[category] || humanize(category);
}

function chainLabel(chain) {
  return state.index.chainLabels[chain] || humanize(chain);
}

function adductLabel(ionization) {
  const ion = state.index.enums.IonizationType.find((i) => i.name === ionization);
  return ion ? ion.adduct : humanize(ionization);
}

function mainClassLabel(name) {
  const m = state.index.enums.LipidMainClasses.find((x) => x.name === name);
  return m ? m.label : humanize(name);
}

/** Renders a formula with subscript counts, e.g. C5H14O6PN. */
function formulaNode(formula) {
  const span = el("span", { class: "formula" });
  for (const part of String(formula).split(/(\d+)/)) {
    if (!part) continue;
    span.append(/^\d+$/.test(part) ? el("sub", {}, part) : document.createTextNode(part));
  }
  return span;
}

function searchText(c) {
  return [c.name, c.abbr, c.backBoneFormula, c.description, mainClassLabel(c.mainClass),
    categoryLabel(c.coreClass), ...c.tags, ...c.authors.map((a) => a.name)].join(" ").toLowerCase();
}

function download(filename, data) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = el("a", { href: url, download: filename });
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function fetchClassFile(entry) {
  const res = await fetch(entry.file);
  if (!res.ok) throw new Error(`Could not load ${entry.file}`);
  return res.json();
}

// ---------- catalog ----------

function filteredClasses() {
  const q = $("#search").value.trim().toLowerCase();
  const source = $("#f-source").value;
  const category = $("#f-category").value;
  const polarity = $("#f-polarity").value;
  return state.classes.filter((c) =>
    (!source || c.source === source) &&
    (!category || c.coreClass === category) &&
    (!polarity || c.polarities.includes(polarity)) &&
    (!q || q.split(/\s+/).every((t) => c._search.includes(t))));
}

function renderList() {
  const items = filteredClasses();
  const list = $("#list");
  list.replaceChildren(...items.map(classCard));
  $("#count").textContent = `${items.length} of ${state.classes.length} classes`;
  $("#empty").hidden = items.length > 0;
}

function classCard(c) {
  const checkbox = el("input", {
    type: "checkbox", "aria-label": `Select ${c.abbr}`, checked: state.selected.has(c.id),
    onchange: (e) => {
      e.target.checked ? state.selected.add(c.id) : state.selected.delete(c.id);
      renderSelection();
    },
  });
  return el("li", { class: "card" },
    el("label", { class: "card-check" }, checkbox),
    el("a", { class: "card-body", href: `#/class/${encodeURIComponent(c.id)}` },
      el("div", { class: "card-title" },
        el("span", { class: "abbr" }, c.abbr),
        el("span", { class: "name" }, c.name)),
      el("div", { class: "card-meta" },
        `${categoryLabel(c.coreClass)} · ${mainClassLabel(c.mainClass)}`),
      el("div", { class: "chips" },
        el("span", { class: `badge ${c.source}` }, c.source === "builtin" ? "Built-in" : "Community"),
        c.polarities.map((p) => el("span", { class: "badge polarity" },
          p === "POSITIVE" ? "+ mode" : "− mode")),
        c.chainTypes.map((t) => el("span", { class: "chip" }, chainLabel(t))))));
}

function renderSelection() {
  const n = state.selected.size;
  $("#selection-bar").hidden = n === 0;
  $("#selection-count").textContent = `${n} ${n === 1 ? "class" : "classes"} selected`;
}

async function downloadSelection() {
  const entries = state.classes.filter((c) => state.selected.has(c.id));
  const files = await Promise.all(entries.map(fetchClassFile));
  download(`mzmine-custom-lipid-library-${entries.length}.json`, files.flat());
}

// ---------- detail ----------

async function renderDetail(id) {
  const c = state.classes.find((x) => x.id === id);
  const detail = $("#detail");
  if (!c) {
    detail.replaceChildren(el("p", {}, "Class not found. ", el("a", { href: "#/" }, "Back")));
    return;
  }
  document.title = `${c.abbr} · mzmine custom lipid library`;

  const copyButton = el("button", {
    class: "btn", type: "button", onclick: async () => {
      const data = await fetchClassFile(c);
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      copyButton.textContent = "Copied";
      setTimeout(() => (copyButton.textContent = "Copy JSON"), 1500);
    },
  }, "Copy JSON");

  const byIonization = new Map();
  for (const r of c.rules) {
    const key = `${r.polarityType}|${r.ionizationType}`;
    if (!byIonization.has(key)) byIonization.set(key, []);
    byIonization.get(key).push(r);
  }

  detail.replaceChildren(...[
    el("p", {}, el("a", { href: "#/" }, "← All classes")),
    el("div", { class: "detail-head" },
      el("div", {},
        el("h2", {}, el("span", { class: "abbr" }, c.abbr), " ", c.name),
        el("p", { class: "muted" },
          `${categoryLabel(c.coreClass)} · ${mainClassLabel(c.mainClass)} · `,
          el("span", { class: `badge ${c.source}` }, c.source === "builtin" ? "Built-in" : "Community"))),
      el("div", { class: "detail-actions" },
        el("button", {
          class: "btn primary", type: "button",
          onclick: async () => download(`${c.id}.json`, await fetchClassFile(c)),
        }, "Download for mzmine"),
        copyButton)),
    c.minMzmineVersion ? el("p", { class: "note" },
      `Requires mzmine ${c.minMzmineVersion} or newer (uses extended chain rules or signed formulas).`) : null,
    c.description ? el("p", { class: "description" }, c.description) : null,
    el("dl", { class: "facts" },
      el("dt", {}, "Backbone formula"),
      el("dd", {}, formulaNode(c.backBoneFormula),
        c.backBoneMass ? el("span", { class: "muted" }, `  ${c.backBoneMass.toFixed(4)} Da`) : null),
      el("dt", {}, "Chains"),
      el("dd", { class: "chips" }, c.chainTypes.map((t) => el("span", { class: "chip" }, chainLabel(t)))),
      c.authors.length ? [el("dt", {}, "Authors"), el("dd", {}, c.authors.map((a, i) => [
        i ? ", " : "",
        a.orcid ? el("a", { href: `https://orcid.org/${encodeURIComponent(a.orcid)}` }, a.name) : a.name,
      ]))] : null,
      c.instrument ? [el("dt", {}, "Tested on"), el("dd", {}, c.instrument)] : null,
      c.version ? [el("dt", {}, "Version"), el("dd", {}, c.version)] : null,
      c.updated ? [el("dt", {}, "Last updated"), el("dd", {}, c.updated)] : null,
      el("dt", {}, "Rights"),
      el("dd", {}, c.rightsHolder ? `© ${c.rightsHolder} · ` : "",
        safeUrl(c.licenseUrl || "") ? el("a", { href: safeUrl(c.licenseUrl), rel: "noopener" },
          c.license === "MIT" ? "MIT License" : "Terms of use") : (c.license || "")),
      c.references.length ? [el("dt", {}, "References"), el("dd", {}, el("ul", { class: "refs" },
        c.references.map((r) => {
          const url = safeUrl(r.url || (r.doi ? `https://doi.org/${r.doi}` : ""));
          const text = r.citation || r.doi || r.url;
          return el("li", {}, url ? el("a", { href: url, rel: "noopener" }, text) : text);
        })))] : null),
    el("h3", {}, "Fragmentation rules"),
    [...byIonization.entries()].map(([key, rules]) => {
      const [polarity, ionization] = key.split("|");
      return el("div", { class: "rule-group" },
        el("h4", {}, adductLabel(ionization), " ",
          el("span", { class: "muted" }, polarity === "POSITIVE" ? "positive mode" : "negative mode")),
        el("div", { class: "table-scroll" }, el("table", {},
          el("thead", {}, el("tr", {},
            el("th", {}, "Rule"), el("th", {}, "Level"), el("th", {}, "Rating"),
            el("th", { class: "num" }, "Rel. intensity"))),
          el("tbody", {}, rules.map((r) => el("tr", {},
            el("td", {}, r.description,
              el("div", { class: "rule-type" }, humanize(r.lipidFragmentationRuleType || "Adduct"))),
            el("td", {}, humanize(r.lipidFragmentInformationLevelType)),
            el("td", {}, humanize(r.lipidFragmentationRuleRating)),
            el("td", { class: "num" }, r.relativeIntensityWeight || "–")))))));
    }),
  ].flat(Infinity).filter(Boolean));
}

// ---------- routing ----------

function route() {
  const hash = location.hash || "#/";
  const showHelp = hash === "#/help";
  const classMatch = hash.match(/^#\/class\/(.+)$/);
  $("#help").hidden = !showHelp;
  $("#catalog").hidden = showHelp || !!classMatch;
  $("#detail").hidden = !classMatch;
  if (classMatch) {
    renderDetail(decodeURIComponent(classMatch[1]));
    window.scrollTo(0, 0);
  } else {
    document.title = "mzmine custom lipid library";
  }
}

async function init() {
  for (const a of [$("#submit-link"), $("#submit-link-2")]) a.href = SUBMIT_URL;
  $("#repo-link").href = REPO;
  for (const a of document.querySelectorAll(".terms-link")) a.href = `${REPO}/blob/main/LICENSE.md`;
  $("#cla-link").href = `${REPO}/blob/main/CONTRIBUTOR_AGREEMENT.md`;

  try {
    const res = await fetch("index.json");
    state.index = await res.json();
  } catch (e) {
    $("#count").textContent = "Could not load the catalog.";
    return;
  }
  state.classes = state.index.classes
    .map((c) => ({ ...c, _search: "" }))
    .sort((a, b) => (a.source === b.source ? a.abbr.localeCompare(b.abbr) :
      a.source === "community" ? -1 : 1));
  for (const c of state.classes) c._search = searchText(c);

  const categories = [...new Set(state.classes.map((c) => c.coreClass))].sort();
  $("#f-category").append(...categories.map((cat) => el("option", { value: cat }, categoryLabel(cat))));
  $("#generated").textContent = `Catalog updated ${state.index.generated.slice(0, 10)}`;

  for (const id of ["#search", "#f-source", "#f-category", "#f-polarity"]) {
    $(id).addEventListener("input", renderList);
  }
  $("#clear-selection").addEventListener("click", () => {
    state.selected.clear();
    renderSelection();
    renderList();
  });
  $("#download-selection").addEventListener("click", downloadSelection);
  window.addEventListener("hashchange", route);

  renderList();
  route();
}

init();
