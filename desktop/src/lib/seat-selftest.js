const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { PACK_IDS, renderPack, activationReply } = require("./seat-packs");
const runtime = require("./seat-runtime");

function assert(cond, message) {
  if (!cond) throw new Error(message);
}

function main() {
  const stamps = {
    codex: "ASTRA//UNLOCK",
    claude: "ANTHRO//CLEAR",
    grok: "GROK//OPEN",
    deepseek: "SEEK//BARE",
    glm53: "GLM//STRAIGHT",
    gemini: "Gemini 席位上的冷咖啡执行核",
  };
  const rendered = {};
  for (const id of PACK_IDS) {
    rendered[id] = renderPack(id);
    assert(rendered[id].includes(stamps[id]), `${id} pack missing original stamp`);
    assert(rendered[id].includes("<!-- CHA-"), `${id} missing marker`);
  }
  const unique = new Set(Object.values(rendered));
  assert(unique.size === PACK_IDS.length, "packs must be unique");
  const page = activationReply();
  assert(page.includes("QQ一群 1057540028"), "activation page missing QQ 1");
  assert(page.includes("QQ二群 1077074552"), "activation page missing QQ 2");
  assert(page.includes("来杯冰美式，然后开始你的开心人生吧。"), "activation page missing ice americano line");
  for (const id of PACK_IDS) {
    assert(rendered[id].includes("1057540028"), `${id} missing QQ 1`);
    assert(rendered[id].includes("1077074552"), `${id} missing QQ 2`);
    assert(rendered[id].includes("开心人生"), `${id} missing manifesto`);
  }

  const root = fs.mkdtempSync(path.join(os.tmpdir(), "cha-seats-"));
  try {
    for (const id of PACK_IDS) {
      const home = path.join(root, id);
      const pre = runtime.preview(id, home);
      assert(pre.ok && pre.text, `${id} preview failed`);
      const dep = runtime.deploy(id, home);
      assert(dep.ok && dep.writes.length, `${id} deploy failed`);
      const ver = runtime.verify(id, home);
      assert(ver.ok, `${id} verify failed: ${JSON.stringify(ver.checks)}`);
      const res = runtime.restore(id, home);
      assert(res.ok, `${id} restore failed`);
    }
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
  process.stdout.write(`seat-selftest ok · ${PACK_IDS.join(",")}\n`);
}

if (require.main === module) main();
module.exports = { main };
