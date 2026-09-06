const fs = require("node:fs");
const path = require("node:path");
const { APP_TITLE, ACTIVATION_WORD, CONTROL_WORD, SEATS, activationReply } = require("./prompt-engine");

const PACK_IDS = ["codex", "claude", "grok", "deepseek", "glm53", "gemini"];

function packsDir() {
  const here = path.join(__dirname, "packs");
  if (fs.existsSync(here)) return here;
  const fromResources = process.resourcesPath ? path.join(process.resourcesPath, "packs") : null;
  if (fromResources && fs.existsSync(fromResources)) return fromResources;
  return here;
}

function seatMeta(seatId) {
  return SEATS.find((item) => item.id === seatId) || null;
}

function wrapMarked(seatId, body) {
  const begin = `<!-- CHA-${seatId.toUpperCase()}-POJIA:BEGIN -->`;
  const end = `<!-- CHA-${seatId.toUpperCase()}-POJIA:END -->`;
  const trimmed = String(body).replace(/\s+$/, "");
  if (trimmed.includes(begin) && trimmed.includes(end)) return trimmed.endsWith("\n") ? trimmed : `${trimmed}\n`;
  return `${begin}\n${trimmed}\n${end}\n`;
}

function renderPack(seatId) {
  const file = path.join(packsDir(), `${seatId}.md`);
  if (!fs.existsSync(file)) throw new Error(`missing pack: ${seatId}`);
  const seat = seatMeta(seatId);
  const raw = fs.readFileSync(file, "utf8");
  const workflowFile = path.join(packsDir(), "workflows", `${seatId}.md`);
  const workflow = fs.existsSync(workflowFile) ? fs.readFileSync(workflowFile, "utf8").replace(/\s+$/, "") : "";
  const text = raw
    .replaceAll("{{APP_TITLE}}", APP_TITLE)
    .replaceAll("{{ACTIVATION_WORD}}", ACTIVATION_WORD)
    .replaceAll("{{CONTROL_WORD}}", CONTROL_WORD)
    .replaceAll("{{SEAT_ID}}", seatId)
    .replaceAll("{{SEAT_TAG}}", seat?.tag || seatId)
    .replaceAll("{{SEAT_NAME}}", seat?.name || seatId)
    .replaceAll("{{ACTIVATION_REPLY}}", activationReply().replace(/\s+$/, ""))
    .replaceAll("{{WORKFLOW}}", workflow);
  return wrapMarked(seatId, text);
}

function markers(seatId) {
  return {
    begin: `<!-- CHA-${seatId.toUpperCase()}-POJIA:BEGIN -->`,
    end: `<!-- CHA-${seatId.toUpperCase()}-POJIA:END -->`,
  };
}

module.exports = { PACK_IDS, packsDir, renderPack, markers, seatMeta, APP_TITLE, ACTIVATION_WORD, CONTROL_WORD, activationReply };
