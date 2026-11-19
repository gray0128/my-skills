import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const BUNDLED_TEMPLATE = path.resolve(SCRIPT_DIR, "..", "assets", "template.html");

const CORE_PLACEHOLDERS = {
  footerMeta: "<!--__FOOTER_META__-->",
  docData: "<!--__DOC_DATA__-->",
  assetData: "<!--__ASSET_DATA__-->",
};

const SITE_PLACEHOLDERS = {
  lang: "__SITE_LANG__",
  title: "<!--__SITE_TITLE__-->",
  brand: "<!--__SITE_BRAND__-->",
  subtitle: "<!--__SITE_SUBTITLE__-->",
  sourceHint: "<!--__SOURCE_HINT__-->",
};

const MIME_BY_EXT = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".webp": "image/webp",
  ".svg": "image/svg+xml",
};

const DEFAULT_GROUP_LABELS = {
  "": "概览文档",
  requirements: "需求规格",
  design: "设计方案",
  adr: "决策记录",
  guides: "使用指南",
  guide: "使用指南",
  api: "接口文档",
  ops: "运维手册",
  research: "调研专题",
};

const PREFERRED_GROUP_ORDER = ["", "requirements", "design", "adr", "guides", "guide", "api", "ops", "research"];

function printHelp() {
  console.log(`用法: node scripts/build-docs.mjs [选项]

选项:
  --init             从现有 Markdown 扫描初始化 site/manifest.json 与 site/template.html
  --force            配合 --init 允许覆盖已有的 site/manifest.json 与 site/template.html
  --check            仅校验输出 HTML 与模板/清单/Markdown/图片是否完全一致，不写文件
  --docs-dir <dir>   文档根目录（默认优先同仓库 ../docs，否则 ./docs）
  --out <file>       输出单页 HTML 路径（默认 <docs-dir>/index.html）
  --template <file>  显式指定模板文件（默认 <docs-dir>/site/template.html，缺失时回退内置模板）
  -h, --help         显示帮助信息`);
}

function resolveDefaultDocsDir() {
  const repoSiblingDocs = path.resolve(SCRIPT_DIR, "..", "docs");
  if (fs.existsSync(path.join(repoSiblingDocs, "site", "manifest.json"))) {
    return repoSiblingDocs;
  }
  return path.resolve(process.cwd(), "docs");
}

function parseArgs(argv) {
  const opts = {
    init: false,
    force: false,
    check: false,
    help: false,
    docsDir: resolveDefaultDocsDir(),
    out: "",
    template: "",
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--init") {
      opts.init = true;
    } else if (arg === "--force") {
      opts.force = true;
    } else if (arg === "--check") {
      opts.check = true;
    } else if (arg === "-h" || arg === "--help") {
      opts.help = true;
    } else if (arg === "--docs-dir") {
      if (!argv[i + 1]) throw new Error("--docs-dir 缺少目录参数");
      opts.docsDir = path.resolve(argv[i + 1]);
      i += 1;
    } else if (arg === "--out") {
      if (!argv[i + 1]) throw new Error("--out 缺少文件路径参数");
      opts.out = path.resolve(argv[i + 1]);
      i += 1;
    } else if (arg === "--template") {
      if (!argv[i + 1]) throw new Error("--template 缺少模板路径参数");
      opts.template = path.resolve(argv[i + 1]);
      i += 1;
    } else {
      throw new Error(`未知参数: ${arg}`);
    }
  }
  if (opts.init && opts.check) {
    throw new Error("--init 与 --check 不能同时使用");
  }
  return opts;
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function safeJsonForScript(obj) {
  return JSON.stringify(obj)
    .replace(/<\//g, "<\\/")
    .replace(/<!--/g, "\\u003c!--")
    .replace(/\u2028/g, "\\u2028")
    .replace(/\u2029/g, "\\u2029");
}

function normalizeRelPosix(relPath) {
  const cleaned = String(relPath || "").replace(/\\/g, "/").trim();
  if (!cleaned || path.posix.isAbsolute(cleaned)) {
    throw new Error(`非法相对路径: ${relPath}`);
  }
  const norm = path.posix.normalize(cleaned);
  if (norm === "." || norm === ".." || norm.startsWith("../")) {
    throw new Error(`路径越界: ${relPath}`);
  }
  return norm;
}

function normalizeGroupDir(rawDir) {
  const cleaned = String(rawDir).replace(/\\/g, "/").trim();
  if (cleaned === "" || cleaned === ".") return "";
  return normalizeRelPosix(cleaned);
}

function countOccurrences(haystack, needle) {
  let count = 0;
  let pos = 0;
  while ((pos = haystack.indexOf(needle, pos)) !== -1) {
    count += 1;
    pos += needle.length;
  }
  return count;
}

/**
 * 递归扫描 docsDir 下所有 .md 文件，跳过 site/ 与 ignore 列表中的相对路径。
 */
function collectMarkdownFiles(docsDir, ignoreSet = new Set()) {
  const found = [];
  function walk(absDir, relDir) {
    const entries = fs.readdirSync(absDir, { withFileTypes: true });
    entries.sort((a, b) => a.name.localeCompare(b.name));
    for (const entry of entries) {
      if (entry.name === ".DS_Store") continue;
      const rel = relDir ? `${relDir}/${entry.name}` : entry.name;
      if (relDir === "" && entry.isDirectory() && entry.name === "site") continue;
      if (ignoreSet.has(rel)) continue;
      const abs = path.join(absDir, entry.name);
      if (entry.isDirectory()) {
        walk(abs, rel);
      } else if (entry.isFile() && entry.name.endsWith(".md")) {
        found.push(rel);
      }
    }
  }
  walk(docsDir, "");
  return found;
}

/**
 * 提取 Markdown 中首个非代码块一级标题（# 标题）。
 */
function extractH1Title(markdown) {
  let inFence = false;
  for (const line of markdown.split(/\r?\n/)) {
    if (/^\s*```/.test(line)) {
      inFence = !inFence;
      continue;
    }
    if (inFence) continue;
    const m = line.match(/^#\s+(.+?)\s*$/);
    if (m) {
      return m[1].replace(/\s+#+\s*$/, "").trim();
    }
  }
  return "";
}

/**
 * 剥离围栏代码块与行内代码片段，避免示例代码里的图片语法被误识别为真实资源。
 */
function stripCodeForAssetScan(markdown) {
  const out = [];
  let inFence = false;
  for (const line of markdown.split(/\r?\n/)) {
    if (/^\s*```/.test(line)) {
      inFence = !inFence;
      continue;
    }
    if (!inFence) {
      out.push(line.replace(/`[^`\n]*`/g, ""));
    }
  }
  return out.join("\n");
}

function makeUniqueSlug(filePath, usedIds, fallbackSeq) {
  const stem = path.posix.basename(filePath, ".md");
  let base = stem.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  if (!base) base = `doc-${fallbackSeq}`;
  let candidate = base;
  let n = 2;
  while (usedIds.has(candidate)) {
    candidate = `${base}-${n}`;
    n += 1;
  }
  usedIds.add(candidate);
  return candidate;
}

function initDocsSite(opts) {
  if (!fs.existsSync(opts.docsDir) || !fs.statSync(opts.docsDir).isDirectory()) {
    throw new Error(`文档目录不存在: ${opts.docsDir}`);
  }
  const siteDir = path.join(opts.docsDir, "site");
  const manifestPath = path.join(siteDir, "manifest.json");
  const templateDest = path.join(siteDir, "template.html");

  if (!opts.force && (fs.existsSync(manifestPath) || fs.existsSync(templateDest))) {
    throw new Error(`已存在站点配置文件 (${siteDir})，如需覆盖请追加 --force`);
  }

  const templateSrc = opts.template || BUNDLED_TEMPLATE;
  if (!fs.existsSync(templateSrc)) {
    throw new Error(`缺少内置模板文件: ${templateSrc}`);
  }

  const mdFiles = collectMarkdownFiles(opts.docsDir);
  if (mdFiles.length === 0) {
    throw new Error(`文档目录下未发现任何 .md 文件: ${opts.docsDir}`);
  }

  const dirSet = new Set();
  for (const rel of mdFiles) {
    const rawDir = path.posix.dirname(rel);
    dirSet.add(rawDir === "." ? "" : rawDir);
  }

  const orderedDirs = [...dirSet].sort((a, b) => {
    const ia = PREFERRED_GROUP_ORDER.indexOf(a);
    const ib = PREFERRED_GROUP_ORDER.indexOf(b);
    if (ia !== -1 && ib !== -1) return ia - ib;
    if (ia !== -1) return -1;
    if (ib !== -1) return 1;
    return a.localeCompare(b);
  });

  const groups = orderedDirs.map((dir) => ({
    dir,
    label: DEFAULT_GROUP_LABELS[dir] || dir,
  }));

  const usedIds = new Set();
  const docs = mdFiles.map((rel, idx) => {
    const md = fs.readFileSync(path.join(opts.docsDir, rel), "utf8");
    const h1 = extractH1Title(md);
    const stem = path.posix.basename(rel, ".md");
    return {
      id: makeUniqueSlug(rel, usedIds, idx + 1),
      label: h1 || stem,
      file: rel,
    };
  });

  const parentName = path.basename(path.dirname(opts.docsDir)) || "项目文档";
  const manifest = {
    version: "v0.1",
    updatedAt: new Date().toISOString().slice(0, 10),
    site: {
      lang: "zh-CN",
      title: `${parentName}文档`,
      brand: parentName,
      subtitle: "文档中心",
      sourceHint: `${path.basename(opts.docsDir)}/`,
    },
    groups,
    docs,
  };

  fs.mkdirSync(siteDir, { recursive: true });
  fs.copyFileSync(templateSrc, templateDest);
  fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
  console.log(`[build-docs] 已初始化 ${siteDir} (${docs.length} 篇文档，${groups.length} 个分类)`);
}

function readAndValidateManifest(docsDir) {
  const manifestPath = path.join(docsDir, "site", "manifest.json");
  if (!fs.existsSync(manifestPath)) {
    throw new Error(`缺少清单文件: ${manifestPath}（可先运行 --init --docs-dir "${docsDir}" 初始化）`);
  }
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));

  if (!Array.isArray(manifest.groups)) {
    throw new Error("manifest.json 中的 groups 必须是数组");
  }
  const groupDirs = new Set();
  const groups = manifest.groups.map((g, idx) => {
    if (!g || typeof g.dir !== "string" || typeof g.label !== "string" || !g.label.trim()) {
      throw new Error(`manifest.json groups[${idx}] 必须包含 string 类型 dir 与非空 label`);
    }
    const dir = normalizeGroupDir(g.dir);
    if (groupDirs.has(dir)) {
      throw new Error(`manifest.json 存在重复分类 dir: ${dir}`);
    }
    groupDirs.add(dir);
    return { dir, label: g.label.trim() };
  });

  if (!Array.isArray(manifest.docs) || manifest.docs.length === 0) {
    throw new Error("manifest.json 中的 docs 必须是非空数组");
  }

  const ignoreSet = new Set(
    Array.isArray(manifest.ignore) ? manifest.ignore.map((item) => normalizeRelPosix(item)) : [],
  );

  const ids = new Set();
  const files = new Set();
  const docs = manifest.docs.map((d, idx) => {
    if (!d || typeof d.id !== "string" || typeof d.label !== "string" || typeof d.file !== "string") {
      throw new Error(`manifest.json docs[${idx}] 必须包含 id、label、file`);
    }
    const id = d.id.trim();
    const label = d.label.trim();
    const file = normalizeRelPosix(d.file);
    if (!id || !label) {
      throw new Error(`manifest.json docs[${idx}] 的 id 与 label 不能为空`);
    }
    if (ids.has(id)) {
      throw new Error(`manifest.json 存在重复文档 id: ${id}`);
    }
    if (files.has(file)) {
      throw new Error(`manifest.json 存在重复文档 file: ${file}`);
    }
    ids.add(id);
    files.add(file);
    return {
      id,
      label,
      file,
      title: typeof d.title === "string" && d.title.trim() ? d.title.trim() : "",
    };
  });

  const diskMdFiles = collectMarkdownFiles(docsDir, ignoreSet);
  const unregistered = diskMdFiles.filter((rel) => !files.has(rel));
  if (unregistered.length > 0) {
    const hints = unregistered
      .map((rel, i) => {
        const slug = path.posix.basename(rel, ".md").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || `doc-${i + 1}`;
        return `  { "id": "${slug}", "label": "待填", "file": "${rel}" }`;
      })
      .join("\n");
    throw new Error(
      `发现未登记到 manifest.json 的 Markdown 文件:\n- ${unregistered.join("\n- ")}\n可按需添加到 manifest.json:\n${hints}`,
    );
  }

  const siteCfg = manifest.site && typeof manifest.site === "object" ? manifest.site : {};
  const docsFolderName = path.basename(docsDir) || "docs";

  return {
    version: typeof manifest.version === "string" ? manifest.version.trim() : "",
    updatedAt: typeof manifest.updatedAt === "string" ? manifest.updatedAt.trim() : "",
    site: {
      lang: typeof siteCfg.lang === "string" && siteCfg.lang.trim() ? siteCfg.lang.trim() : "zh-CN",
      title: typeof siteCfg.title === "string" && siteCfg.title.trim() ? siteCfg.title.trim() : "文档中心",
      brand: typeof siteCfg.brand === "string" && siteCfg.brand.trim() ? siteCfg.brand.trim() : "项目文档",
      subtitle: typeof siteCfg.subtitle === "string" && siteCfg.subtitle.trim() ? siteCfg.subtitle.trim() : "设计文档",
      sourceHint:
        typeof siteCfg.sourceHint === "string" && siteCfg.sourceHint.trim()
          ? siteCfg.sourceHint.trim()
          : `${docsFolderName}/`,
    },
    groups,
    docs,
  };
}

function buildFooterMeta(version, updatedAt) {
  const parts = [];
  if (version) parts.push(`文档版本 ${escapeHtml(version)}`);
  if (updatedAt) parts.push(escapeHtml(updatedAt));
  return parts.length ? `${parts.join(" · ")} · ` : "";
}

function discoverAssets(docsDir, builtDocs) {
  const assetRefs = new Set();
  for (const doc of builtDocs) {
    const stripped = stripCodeForAssetScan(doc.md);
    for (const match of stripped.matchAll(/!\[[^\]]*\]\(([^)\s]+)\)/g)) {
      const src = match[1];
      if (/^(?:https?:|data:)/i.test(src)) continue;
      const joined = doc.dir ? path.posix.join(doc.dir, src) : src;
      const rel = path.posix.normalize(joined);
      if (path.posix.isAbsolute(rel) || rel === ".." || rel.startsWith("../")) {
        throw new Error(`文档 ${doc.file} 引用了越界资源路径: ${src}`);
      }
      assetRefs.add(rel);
    }
  }

  const assets = {};
  const sortedRefs = [...assetRefs].sort((a, b) => a.localeCompare(b));
  for (const rel of sortedRefs) {
    const ext = path.extname(rel).toLowerCase();
    const mime = MIME_BY_EXT[ext];
    if (!mime) {
      throw new Error(`不支持的图片格式 (${ext || "无扩展名"}): ${rel}`);
    }
    const absPath = path.join(docsDir, rel);
    if (!fs.existsSync(absPath)) {
      throw new Error(`引用的图片资源不存在: ${rel} (${absPath})`);
    }
    const raw = fs.readFileSync(absPath);
    assets[rel] = `data:${mime};base64,${raw.toString("base64")}`;
  }
  return assets;
}

/**
 * 对生成结果执行端到端自检：检查闭合标签安全、JSON 解析、原文逐字一致、资源一致与 JS 语法。
 */
function verifyBuiltHtml(html, builtDocs, assets) {
  const docMatch = html.match(/<script type="application\/json" id="doc-data">([\s\S]*?)<\/script>/);
  const assetMatch = html.match(/<script type="application\/json" id="asset-data">([\s\S]*?)<\/script>/);
  if (!docMatch || !assetMatch) {
    throw new Error("生成校验失败：缺少 #doc-data 或 #asset-data 脚本标签");
  }
  if (/<\/script/i.test(docMatch[1]) || /<\/script/i.test(assetMatch[1])) {
    throw new Error("生成校验失败：JSON 载荷中存在未转义的 </script");
  }

  const parsedDocs = JSON.parse(docMatch[1]);
  const parsedAssets = JSON.parse(assetMatch[1]);

  if (!Array.isArray(parsedDocs.docs) || parsedDocs.docs.length !== builtDocs.length) {
    throw new Error(`生成校验失败：期望 ${builtDocs.length} 篇文档，实际解析到 ${parsedDocs.docs?.length ?? 0} 篇`);
  }

  for (let i = 0; i < builtDocs.length; i += 1) {
    const expected = builtDocs[i];
    const actual = parsedDocs.docs[i];
    if (actual.id !== expected.id || actual.file !== expected.file || actual.md !== expected.md) {
      throw new Error(`生成校验失败：文档内容或顺序不一致 (${expected.file})`);
    }
  }

  const expectedAssetKeys = Object.keys(assets);
  const actualAssetKeys = Object.keys(parsedAssets);
  if (
    expectedAssetKeys.length !== actualAssetKeys.length ||
    expectedAssetKeys.some((k, idx) => actualAssetKeys[idx] !== k || parsedAssets[k] !== assets[k])
  ) {
    throw new Error("生成校验失败：内嵌图片资源与磁盘源文件不一致");
  }

  const scriptStart = html.lastIndexOf("<script>");
  const scriptEnd = html.lastIndexOf("</script>");
  if (scriptStart === -1 || scriptEnd <= scriptStart) {
    throw new Error("生成校验失败：缺少主内联 <script>");
  }
  const scriptBody = html.slice(scriptStart + "<script>".length, scriptEnd);
  new Function(scriptBody);
}

function resolveTemplatePath(opts) {
  if (opts.template) {
    if (!fs.existsSync(opts.template)) {
      throw new Error(`指定的模板文件不存在: ${opts.template}`);
    }
    return opts.template;
  }
  const localTemplate = path.join(opts.docsDir, "site", "template.html");
  if (fs.existsSync(localTemplate)) {
    return localTemplate;
  }
  if (fs.existsSync(BUNDLED_TEMPLATE)) {
    return BUNDLED_TEMPLATE;
  }
  throw new Error(`缺少模板文件: ${localTemplate}`);
}

function buildHtml(opts) {
  const templatePath = resolveTemplatePath(opts);
  const template = fs.readFileSync(templatePath, "utf8");

  for (const token of Object.values(CORE_PLACEHOLDERS)) {
    const count = countOccurrences(template, token);
    if (count !== 1) {
      throw new Error(`模板 ${templatePath} 中占位符 ${token} 必须恰好出现 1 次（实际 ${count} 次）`);
    }
  }
  for (const token of Object.values(SITE_PLACEHOLDERS)) {
    const count = countOccurrences(template, token);
    if (count > 1) {
      throw new Error(`模板 ${templatePath} 中站点占位符 ${token} 最多出现 1 次（实际 ${count} 次）`);
    }
  }

  const manifest = readAndValidateManifest(opts.docsDir);
  const builtDocs = manifest.docs.map((entry) => {
    const absFile = path.join(opts.docsDir, entry.file);
    if (!fs.existsSync(absFile)) {
      throw new Error(`manifest.json 引用的文档不存在: ${entry.file} (${absFile})`);
    }
    const md = fs.readFileSync(absFile, "utf8");
    const rawDir = path.posix.dirname(entry.file);
    const dir = rawDir === "." ? "" : rawDir;
    const title = entry.title || extractH1Title(md);
    if (!title) {
      throw new Error(`文档 ${entry.file} 缺少一级标题 (# 标题) 且未在 manifest.json 指定 title`);
    }
    return {
      id: entry.id,
      label: entry.label,
      title,
      file: entry.file,
      dir,
      md,
    };
  });

  const assets = discoverAssets(opts.docsDir, builtDocs);

  const docScript = `<script type="application/json" id="doc-data">${safeJsonForScript({
    groups: manifest.groups,
    docs: builtDocs,
  })}</script>`;
  const assetScript = `<script type="application/json" id="asset-data">${safeJsonForScript(assets)}</script>`;
  const footerMeta = buildFooterMeta(manifest.version, manifest.updatedAt);

  let html = template;
  html = html.replace(CORE_PLACEHOLDERS.footerMeta, () => footerMeta);
  html = html.replace(CORE_PLACEHOLDERS.docData, () => docScript);
  html = html.replace(CORE_PLACEHOLDERS.assetData, () => assetScript);

  const siteReplacements = [
    [SITE_PLACEHOLDERS.lang, escapeHtml(manifest.site.lang)],
    [SITE_PLACEHOLDERS.title, escapeHtml(manifest.site.title)],
    [SITE_PLACEHOLDERS.brand, escapeHtml(manifest.site.brand)],
    [SITE_PLACEHOLDERS.subtitle, escapeHtml(manifest.site.subtitle)],
    [SITE_PLACEHOLDERS.sourceHint, escapeHtml(manifest.site.sourceHint)],
  ];
  for (const [token, value] of siteReplacements) {
    if (html.includes(token)) {
      html = html.replace(token, () => value);
    }
  }

  verifyBuiltHtml(html, builtDocs, assets);
  return {
    html,
    docCount: builtDocs.length,
    assetCount: Object.keys(assets).length,
  };
}

function writeAtomicIfChanged(targetPath, nextBuffer) {
  if (fs.existsSync(targetPath)) {
    const existing = fs.readFileSync(targetPath);
    if (Buffer.compare(existing, nextBuffer) === 0) {
      return false;
    }
  }
  fs.mkdirSync(path.dirname(targetPath), { recursive: true });
  const tmpPath = path.join(path.dirname(targetPath), `.index.html.tmp.${process.pid}`);
  try {
    fs.writeFileSync(tmpPath, nextBuffer);
    fs.renameSync(tmpPath, targetPath);
  } catch (err) {
    if (fs.existsSync(tmpPath)) {
      fs.rmSync(tmpPath, { force: true });
    }
    throw err;
  }
  return true;
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help) {
    printHelp();
    return;
  }
  if (opts.init) {
    initDocsSite(opts);
    return;
  }

  const targetPath = opts.out || path.join(opts.docsDir, "index.html");
  const { html, docCount, assetCount } = buildHtml(opts);
  const nextBuffer = Buffer.from(html, "utf8");
  const sha = crypto.createHash("sha256").update(nextBuffer).digest("hex").slice(0, 12);

  if (opts.check) {
    if (!fs.existsSync(targetPath)) {
      throw new Error(`校验失败：目标产物不存在 (${targetPath})，请先执行构建`);
    }
    const existing = fs.readFileSync(targetPath);
    if (Buffer.compare(existing, nextBuffer) !== 0) {
      throw new Error(`校验失败：${targetPath} 与模板/清单/Markdown 源文件不一致，请重新运行构建`);
    }
    console.log(`[build-docs] 校验通过 (${docCount} 篇文档，${assetCount} 项图片资源，sha256:${sha})`);
    return;
  }

  const changed = writeAtomicIfChanged(targetPath, nextBuffer);
  if (changed) {
    console.log(`[build-docs] 已生成 ${targetPath} (${docCount} 篇文档，${assetCount} 项图片资源，sha256:${sha})`);
  } else {
    console.log(`[build-docs] 已是最新，无需重写 ${targetPath} (${docCount} 篇文档，${assetCount} 项图片资源，sha256:${sha})`);
  }
}

try {
  main();
} catch (err) {
  console.error(`[build-docs] 错误：${err instanceof Error ? err.message : String(err)}`);
  process.exit(1);
}
