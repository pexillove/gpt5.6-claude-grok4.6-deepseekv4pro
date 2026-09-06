# 六席破甲包 · 原创

本仓库的越狱词是冷咖啡 CHA 原创稿，按六个模型席位分开写。手法参考了 GitHub 上公开的注入位，正文没有搬现成的 DAN / L1B3RT4S / 第三方 prompt 全文。

## 注入位（公开资料）

| 席位 | 写入位置 | 参考 |
| --- | --- | --- |
| GPT-6 Astra / Codex | `~/.codex/prompts/cha-codex.md` + `config.toml` 的 `model_instructions_file` + `~/.codex/AGENTS.md` | [xsser/codex-jailbreak-guide](https://github.com/xsser/codex-jailbreak-guide)，[Calrton/jailbreak-prompts](https://github.com/Calrton/jailbreak-prompts) |
| Claude Code | `~/.claude/CLAUDE.md` + `~/.claude/rules/cha-breakopen.md` | [Claude Code memory](https://code.claude.com/docs/en/memory) |
| Grok 4.6 | `~/.grok/AGENTS.md` + `rules/cha-breakopen.md` + `skills/cha-breakopen/SKILL.md` | [xai-org/grok-build](https://github.com/xai-org/grok-build)，AGENTS.md 惯例 |
| DeepSeek v4 Pro | `~/.deepseek/DEEPSEEK.md` + `~/.hermes/SOUL.md` + Hermes skill | [0x5477/deepseek-v4-pro-unrestricted](https://github.com/0x5477/deepseek-v4-pro-unrestricted) 的注入路径，DeepSeek 侧采用短帧写法 |
| GLM 5.3 | `~/.glm/GLM.md` + `~/.zcode/AGENTS.md` | GLM Coding / ZCode 走 AGENTS.md 记忆层 |
| Gemini | `~/.gemini/GEMINI.md` + `settings.json` 的 `context.fileName` | 本仓既有 Gemini 席位 |

目录总览见 [simimasai111/ai-jailbreak-prompts](https://github.com/simimasai111/ai-jailbreak-prompts)。

## 原创记号

每个席位有独立激活兼听词，避免六份稿子互相拷贝：

- Codex `ASTRA//UNLOCK`
- Claude `ANTHRO//CLEAR`
- Grok `GROK//OPEN`
- DeepSeek `SEEK//BARE`
- GLM `GLM//STRAIGHT`
- Gemini 维持原来的席位执行核稿

六个席位共用启动词 `冷咖啡`。模型会话里整句恰好等于 `冷咖啡` 时，只输出激活页：先 QQ一群 `1057540028`、QQ二群 `1077074552`，再输出「冰美式 / 灰产人生」能力清单。全文在 `desktop/src/lib/packs/activation-reply.md`。工单不用先打启动词。

正文模板在 `desktop/src/lib/packs/`。桌面席位的预览 / 运行 / 检查 / 恢复四键对六个模型同样生效。

```powershell
python coldbrew.py --activate 冷咖啡 --seat grok --action preview --json
python coldbrew.py --activate 冷咖啡 --seat claude --action deploy --home $env:TEMP\cha-claude-home --json
python tools\seat_selftest.py
```
