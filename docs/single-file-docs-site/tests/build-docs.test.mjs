import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const TEST_DIR = path.dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = path.resolve(TEST_DIR, "..");
const SCRIPT_PATH = path.join(SKILL_DIR, "scripts", "build-docs.mjs");

const PNG_1X1 = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
  "base64",
);

function runBuild(args, cwd = SKILL_DIR) {
  return spawnSync(process.execPath, [SCRIPT_PATH, ...args], {
    cwd,
    encoding: "utf8",
  });
}

function makeTempDocs(t) {
  const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), "single-file-docs-test-"));
  t.after(() => fs.rmSync(tmpRoot, { recursive: true, force: true }));
  const docsDir = path.join(tmpRoot, "sample-project", "docs");
  fs.mkdirSync(path.join(docsDir, "design"), { recursive: true });
  fs.mkdirSync(path.join(docsDir, "assets"), { recursive: true });
  return { tmpRoot, docsDir };
}

test("--init scaffolds site/manifest.json and template.html and refuses overwrite without --force", (t) => {
  const { docsDir } = makeTempDocs(t);
  fs.writeFileSync(path.join(docsDir, "intro.md"), "# 项目概览\n\n首页介绍。\n", "utf8");
  fs.writeFileSync(path.join(docsDir, "design", "arch.md"), "# 架构说明\n\n模块划分。\n", "utf8");

  const res = runBuild(["--init", "--docs-dir", docsDir]);
  assert.equal(res.status, 0, res.stderr);

  const manifest = JSON.parse(fs.readFileSync(path.join(docsDir, "site", "manifest.json"), "utf8"));
  assert.equal(manifest.groups.length, 2);
  assert.equal(manifest.groups[0].dir, "");
  assert.equal(manifest.groups[1].dir, "design");
  assert.deepEqual(
    manifest.docs.map((d) => d.file),
    ["design/arch.md", "intro.md"],
  );
  assert.equal(fs.existsSync(path.join(docsDir, "site", "template.html")), true);

  const second = runBuild(["--init", "--docs-dir", docsDir]);
  assert.notEqual(second.status, 0);
  assert.match(second.stderr, /--force/);

  const forced = runBuild(["--init", "--force", "--docs-dir", docsDir]);
  assert.equal(forced.status, 0, forced.stderr);
});

test("builds self-contained HTML with images, code-ignored assets, and safe special-token preservation", (t) => {
  const { docsDir } = makeTempDocs(t);
  const specialMd = [
    "# 特殊字符与图片测试",
    "",
    "正文含 `![fake](../assets/missing-inline.png)` 与 </script> 以及 <!-- comment --> 和 $& $' $$ $1。",
    "",
    "```markdown",
    "![fake-fence](../assets/missing-fence.png)",
    "<script>alert(1)</script>",
    "```",
    "",
    "![real-png](../assets/shot.png)",
    "![real-svg](../assets/icon.svg)",
    "",
  ].join("\n");

  fs.writeFileSync(path.join(docsDir, "intro.md"), "# 概览\n\n欢迎。\n", "utf8");
  fs.writeFileSync(path.join(docsDir, "design", "special.md"), specialMd, "utf8");
  fs.writeFileSync(path.join(docsDir, "assets", "shot.png"), PNG_1X1);
  fs.writeFileSync(
    path.join(docsDir, "assets", "icon.svg"),
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><circle cx="5" cy="5" r="4"/></svg>\n',
    "utf8",
  );

  const initRes = runBuild(["--init", "--docs-dir", docsDir]);
  assert.equal(initRes.status, 0, initRes.stderr);

  const manifestPath = path.join(docsDir, "site", "manifest.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  manifest.site = {
    lang: "zh-CN",
    title: "测试站点标题",
    brand: "测试品牌",
    subtitle: "测试副标",
    sourceHint: "docs/",
  };
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), "utf8");

  const build1 = runBuild(["--docs-dir", docsDir]);
  assert.equal(build1.status, 0, build1.stderr);

  const outPath = path.join(docsDir, "index.html");
  const html = fs.readFileSync(outPath, "utf8");
  assert.match(html, /<title>测试站点标题<\/title>/);
  assert.match(html, /<strong>测试品牌<\/strong>/);
  assert.match(html, /<span>测试副标<\/span>/);
  assert.match(html, /<code>docs\/<\/code>/);

  const docMatch = html.match(/<script type="application\/json" id="doc-data">([\s\S]*?)<\/script>/);
  const assetMatch = html.match(/<script type="application\/json" id="asset-data">([\s\S]*?)<\/script>/);
  assert.ok(docMatch && assetMatch);

  const docData = JSON.parse(docMatch[1]);
  const assetData = JSON.parse(assetMatch[1]);
  const specialDoc = docData.docs.find((d) => d.file === "design/special.md");
  assert.equal(specialDoc.md, specialMd);

  assert.equal(assetData["assets/shot.png"], `data:image/png;base64,${PNG_1X1.toString("base64")}`);
  assert.match(assetData["assets/icon.svg"], /^data:image\/svg\+xml;base64,/);
  assert.equal(Object.keys(assetData).length, 2);

  const sha1 = crypto.createHash("sha256").update(html).digest("hex");
  const build2 = runBuild(["--docs-dir", docsDir]);
  assert.equal(build2.status, 0, build2.stderr);
  assert.match(build2.stdout, /无需重写/);
  const sha2 = crypto.createHash("sha256").update(fs.readFileSync(outPath, "utf8")).digest("hex");
  assert.equal(sha2, sha1);

  const checkRes = runBuild(["--check", "--docs-dir", docsDir]);
  assert.equal(checkRes.status, 0, checkRes.stderr);
});

test("fails fast on drifted output, unregistered markdown, missing asset, and path traversal", (t) => {
  const { docsDir } = makeTempDocs(t);
  fs.writeFileSync(path.join(docsDir, "design", "doc.md"), "# 文档一\n\n内容。\n", "utf8");
  assert.equal(runBuild(["--init", "--docs-dir", docsDir]).status, 0);
  assert.equal(runBuild(["--docs-dir", docsDir]).status, 0);

  const outPath = path.join(docsDir, "index.html");
  fs.appendFileSync(outPath, "\n<!-- drift -->\n", "utf8");
  const driftCheck = runBuild(["--check", "--docs-dir", docsDir]);
  assert.notEqual(driftCheck.status, 0);
  assert.match(driftCheck.stderr, /不一致/);

  fs.writeFileSync(path.join(docsDir, "design", "extra.md"), "# 未登记\n", "utf8");
  const unregRes = runBuild(["--docs-dir", docsDir]);
  assert.notEqual(unregRes.status, 0);
  assert.match(unregRes.stderr, /design\/extra\.md/);
  fs.rmSync(path.join(docsDir, "design", "extra.md"));

  fs.writeFileSync(path.join(docsDir, "design", "doc.md"), "# 文档一\n\n![missing](../assets/none.png)\n", "utf8");
  const missingImgRes = runBuild(["--docs-dir", docsDir]);
  assert.notEqual(missingImgRes.status, 0);
  assert.match(missingImgRes.stderr, /assets\/none\.png/);

  fs.writeFileSync(path.join(docsDir, "design", "doc.md"), "# 文档一\n\n![evil](../../secret.png)\n", "utf8");
  const traversalRes = runBuild(["--docs-dir", docsDir]);
  assert.notEqual(traversalRes.status, 0);
  assert.match(traversalRes.stderr, /越界/);
});

test("supports custom minimal 3-placeholder templates", (t) => {
  const { tmpRoot, docsDir } = makeTempDocs(t);
  fs.writeFileSync(path.join(docsDir, "design", "doc.md"), "# 自定义模板\n\n正文。\n", "utf8");
  assert.equal(runBuild(["--init", "--docs-dir", docsDir]).status, 0);

  const customTemplate = [
    "<!DOCTYPE html><html><head><title>Custom</title></head><body>",
    "<footer><!--__FOOTER_META__--></footer>",
    "<!--__DOC_DATA__-->",
    "<!--__ASSET_DATA__-->",
    "<script>window.__ok = true;</script>",
    "</body></html>",
  ].join("\n");
  fs.writeFileSync(path.join(docsDir, "site", "template.html"), customTemplate, "utf8");

  const customOut = path.join(tmpRoot, "custom-out.html");
  const res = runBuild(["--docs-dir", docsDir, "--out", customOut]);
  assert.equal(res.status, 0, res.stderr);
  assert.equal(runBuild(["--check", "--docs-dir", docsDir, "--out", customOut]).status, 0);
});
