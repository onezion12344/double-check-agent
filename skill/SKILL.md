---
name: double-check
description: "Unified Fact, Logic, Theory & Tool-Use verification. Three pillars: Fact, Theory, Tool Use. Bounded Rationality paradigm: external enforcement via hooks, not model internalization."
version: 2.1.0
quickref:
  pillars:
    fact: "Price/time/address/spec → Phase 0.5 → CoVe+FIRE → IFCN ≥2 sources → ✅/⚡/❓/❌"
    theory: "Logic/fallacy → FLICC (Fake experts/Cherry picking/Conspiracy) → Toulmin → FoVer → FABLE"
    tool_use: "Post-hoc verification → efficiency/redundancy/privilege/scope → 6-route landscape"
  pipeline:
    - "P0: Dedup gate — emergency skip + content check"
    - "P0.5: Pre-answer — extract claims, time-sensitive = force search"
    - "P1: SIFT — source attribution (✅ source / ⚠️ guessed / ❌ contradiction)"
    - "P2: CoVe+FIRE — independent cross-verification, ≥2 sources"
    - "P3: FABLE — impact grading (🔴 Critical / 🟡 Experience / 🟢 Cosmetic)"
    - "P4: Truth Sandwich — structured correction delivery"
  architecture:
    plugin: "Orchestrator (detect → delegate). pre_llm_call + transform_llm_output hooks. ~200 lines."
    skill: "Deep audit methodology. 28 reference files. 59KB total."
    verification: "Sub-agent via delegate_task. Full tool access (web/browser/terminal)."
---

# Double-Check

> Unified Fact, Logic & Theory verification. Pre-answer fact check + post-answer deep audit + logical fallacy detection + theory consistency analysis.
> 核心原则：每轮降维，不一锅炖。

## 🧠 设计哲学：Bounded Rationality 与 外部强制执行

**核心问题：** LLM 有 bounded rationality。即使是 DeepSeek V4 Pro 这样的前沿模型，在 agent 场景下 tool call 数量仍然太少，不会主动去做充分验证。模型不知道自己不知道什么。

**不是一个二元问题。** AI 验证领域至少有 6+ 条独立路线，每条检查不同的事。Double-Check 填补的是其中唯一的空白——执行后验证 (post-hoc verification)。全部分类见下方「工具选择核查 / Tool Use 相关论文」章节。

| 路线 | 检查什么 | 代表 | Double-Check 的关系 |
|:-----|:---------|:-----|:--------------------|
| **训练** (Training) | 什么时候该调工具 | SMART, Metis, Tool-Overuse Illusion | ❌ 不验证选择正确性 |
| **策略** (Policy) | 工具有没有权限调 | Veto, AgentSpec, Edictum, AGT | ❌ 只拦不准调，不验调得对不对 |
| **规划** (Planning) | 怎么排最优调用链 | ToolTree, Feasible is Not Enough, AutoTool | ❌ 执行前优化，执行后不审计 |
| **选择自验** (Selection-time) | 选的工具对不对 | ToolVerifier (Meta 2024) | ❌ 选的时候验证，调了之后不回头看 |
| **运行时** (Runtime guard) | 有没有重复调 | MLflow ToolCallEfficiency, Tool Spam | ❌ 查重复，不查选错工具 |
| **偏差分析** (Bias) | 为什么偏这个工具 | BiasBusters (ICLR 2026) | ❌ 只分析不纠正 |
| **🔵 Double-Check** | **调完了回头检查是不是最优选择** | Post-hoc verifier: 效率/冗余/权限/scope | **✅ 唯一做 post-hoc 验证的** |

本项目的 methodology（SKILL.md）是模型无关的，可被任何 LLM agent 加载。自动化 Plugin 钩子在 Hermes Agent 上已验证运行，其他平台理论上可行但尚未测试。

**Bounded Rationality 不变：** Double-Check 对所有模型都生效，和模型自身能力正交。不是为了替代训练/策略/规划等方法，而是填补它们都不覆盖的 post-hoc 空白。

## 三大支柱架构

```
Double-Check
├── 🟢 Double-Check Fact     (verified ✓)
│   验证事实准确性：价格/时间/地址/名称/来源
│   已合并 12 篇论文 + 10 新闻标准
│   基准测试：62.5% → 97.5% +35pp (DeepSeek V4 Flash)
│
├── 🟡 Double-Check Theory   (merged ✓)
│   验证逻辑一致性：FLICC谬误/Toulmin论证/FoVer形式化
│   与 Fact 共享 pipeline 架构
│
└── 🔵 Double-Check Tool Use (building ─)
    验证工具选择正确性：是否选对工具、是否冗余、是否最优
    现有：3 个 prompt-based .md skills (agent-tool-discipline repo)
    目标：加 Hermes Plugin hook (pre/post tool call)，与 Fact/Theory 同居 plugin
```

**原则：** 三个 pillar 共享同一套架构模式 (SIFT → CoVe+FIRE → FABLE → Truth Sandwich)，但每轮的**验证对象不同**：
- Fact: 验证 claims 的**外部真实性**（搜 web 确认）
- Theory: 验证推理的**内部逻辑性**（不搜 web，分析结构）
- Tool Use: 验证行为的**选择正确性**（扫描所有可用工具后再做选择）

## ⚠️ 已知限制：`is_time_sensitive()` 纯正则的语义盲区

以及 `pre_llm_call` classify JSON 解析不稳定（2026.06.30 测试发现）。

### `pre_llm_call` classify JSON 解析不稳定（2026.06.30）

2026.06.30 实测发现 plugin 的 `pre_llm_call` hook 能成功触发并调用 `ctx.llm.complete()` 做 classify，但 LLM 返回的 JSON 格式不稳定，偶尔被截断或包含前导换行导致 JSON parse 失败：

```
plugins.double-check - WARNING - Classify failed: '\n  "question_type"'
```

**影响：** classify 失败后 plugin 不会注入验证 context，相当于静默降级为无验证模式。

**临时缓解：** 在 `ctx.llm.complete()` 调用中增加 `response_model` 参数（如 Pydantic model）强制 JSON schema，替代自由格式 prompt → JSON 的路径。

**长期修复：** 参见下方「架构跃迁」——Plugin 只做 detect + inject，真实的 classify 逻辑交给主 agent 在 system prompt 中完成。

### `is_time_sensitive()` 语义盲区

当前 `verify.py` line 68-70 的 `is_time_sensitive()` 使用 9 条正则 pattern 判断 claim 是否需时效搜索：

```python
def is_time_sensitive(claim: str) -> bool:
    return any(p.search(claim.lower()) for p in TIME_SENSITIVE_PATTERNS)
```

**问题：** 正则不理解语义。
- "港币兑人民币汇率" → False（无 ¥/$/时间/地址 pattern），但真实是 time-sensitive
- "华为 matepad 参数" → True（含"参数"），但真实不是 time-sensitive

**改进方案（待实施）：**
1. regex pre-screen 保留作为 gate（0 匹配 → 不调 LLM，直接跳过）
2. 通过后：1 次 LLM call + JSON mode，让 LLM 按语义判断 `{time_sensitive: true/false, claims: [...]}`
3. 只有 LLM 判断为 time-sensitive 才触发 web search

这修正了 Phase 0.5 的核心缺陷——让"判断"从正则升级到大模型语义理解，让"gate"仍由正则做低成本过滤。

## 🔁 架构跃迁：Detect → Delegate（Plugin 不做验证）

**核心原则重构（2026.06.26 确定）：**

> ❌ 旧架构：Plugin 自己做验证（regex + LLM call + 搜索）
> ✅ 新架构：Plugin 只 detect + inject 指令，真正的验证工作交给主 agent 的 `delegate_task`

### 原因

Plugin hook 上下文没有 `delegate_task` 权限。但 Plugin 可以通过注入 context 告诉主 agent：
"此问题涉及事实信息，请使用 delegate_task 启动子 agent 验证。"

### 新架构流程图

```
pre_llm_call:
  ctx.llm.complete() → classify 问题类型 (fact / theory / tool-use)
  → return {"context": "⛔ 此问题涉及事实信息。
     在回答前必须使用 delegate_task 启动子 agent 验证。
     子 agent 做全量搜索 + 交叉验证 + 返回结构化结果。
     等子 agent 返回后再回答。"}
  ↓
Hermes runtime 注入 context 到 system prompt
  ↓
主 agent 看到指令 → 自己调用 delegate_task
  ↓
子 agent 全量搜索 + 验证 → 返回
  ↓
主 agent 用已验证结果回答

transform_llm_output:
  检测回复是否密集（≥300字 + 含事实标记）
  → 无法直接 spawn 子 agent（没有 post_llm_call hook）
  → 改由下一轮 pre_llm_call 顺带：
    同时检查上一轮回复 → 标记 "对上一轮做 SIFT→CoVe+FIRE→FABLE 后验"
```

### 这个架构的优势

| 维度 | 旧架构（Plugin 自做） | 新架构（Plugin detect + inject） |
|:-----|:--------------------|:--------------------------------|
| 验证能力 | 受限：只能 regex + DDGS 搜索 | 完整：子 agent 有全部工具（web/browser/terminal） |
| 语义理解 | 正则盲区 | 子 agent 用 LLM 语义判断 |
| 并发 | 串行搜索 | 子 agent 可并行 N 条搜索 |
| 灵活性 | 死板代码 | 子 agent 自主决策验证策略 |
| 维护 | verify.py 越来越臃肿 | Plugin 保持轻量，验证逻辑在子 agent |

### 三个 pillar 统一架构

```
Double-Check
├── Fact:   pre_llm_call detect 事实问题 → delegate 子 agent 搜事实
├── Theory: pre_llm_call detect 逻辑问题 → delegate 子 agent 分析谬误
└── Tool Use: pre_llm_call detect 复杂任务 → delegate 子 agent 扫工具
```

**总结：Plugin 是调度层（orchestrator），不是执行层（worker）。真正的验证工作由子 agent 完成。**

## Termux 兼容性

Hermes Agent 官方支持 **Android (Termux)**，安装方式与 macOS/Linux 相同：
`curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`

所有 Python 插件（包括 Double-Check）在 Termux 上均可正常工作：
- ✅ `pre_llm_call` / `transform_llm_output` hooks — Python runtime，无依赖
- ✅ `ctx.llm.complete()` — 网络 API 调用
- ✅ `verify_claims` tool — DuckDuckGo 搜索
- ✅ plugin-init.py / verify.py — 纯 Python，无系统依赖
- ❌ 仅 browser/vision 工具受限（无桌面环境）

✅ Termux 能跑 Hermes，所以 Double-Check 也能在 Termux 上跑。

## 工具选择核查（Double-Check Tool Use — 待构建）

**背景：** 2026.06.26 调研确认，现有工具使用纪律方法分两大阵营，但都缺少"工具选择正确性"的验证：

| 阵营 | 代表 | 检查什么 | 不检查什么 |
|:-----|:-----|:---------|:----------|
| 训练路线 | SMART, Metis/HDPO, Alignment | 什么时候不用工具 | 选没选对工具 |
| 策略路线 | AGT, AgentSpec, Edictum, Veto | 工具是否允许调用 | 工具选得对不对 |

**空白：** 没有系统验证「对于当前问题，这个工具是不是最合适的、有没有冗余、有没有更好的选择」。

**计划：** 将 `agent-tool-discipline` repo 的 3 个 prompt-based skills 升级为 Hermes Plugin hook:
- `pre_tool_call`: 扫描所有可用工具 → 预测最佳选择 → 验证选择是否正确
- `post_tool_call`: 检查输出是否回答原始意图 → 标记冗余 → 必要时建议重试

**已有资源：**
- 3 个 .md skills: exhaustive-tool-review / cross-verify-search / fact-check
- Knowing-Doing Gap paper (Cheng et al., UMD, arXiv 2605.14038): 26.5-54.0% mismatch
- Existing frameworks research documented in master session 2026.06.26

# 📚 学术参考

本技能合并 12 篇学术论文 + 10 个新闻标准 + 9 个 AI 验证系统。
完整框架列表、引用和关键洞见 → `skill_view("fact-check", "references/verification-frameworks.md")`
→ 关键：CoVe (Meta 2023), FIRE (ACL 2025), SIFT (Caulfield 2019), IFCN 标准, FABLE (HCI 2025)

## Tool Use 相关论文（2026.06.30 更新调研 — 13 篇新论文）

> 分类框架：现有工作覆盖 6 条路线（A-F），但都没有做我们 gap 的 **post-hoc 工具选择正确性验证**。

### 路线 A — 什么时候该调用工具（要不要调）
| 论文 | 要点 | 关键数据 |
|:-----|:-----|:---------|
| **SMART** (arXiv 2502.11435, ACL 2025 Findings) | 元认知训练减少工具过度使用 | 工具使用 -24%，准确率 +37%；7B 匹配 GPT-4o |
| **Metis/HDPO** (arXiv 2604.08545, Accio-Lab; reportedly Alibaba per VentureBeat) | 分层解耦策略优化，准确率与效率分离 | VentureBeat 报道冗余调用 98%→2%；论文正文说 "reduces tool invocations by orders of magnitude" |
| **To Call or Not to Call** (arXiv 2605.00737, MPII, May 2026) | 决策理论框架评估必要性/效用/可负担性；从 hidden states 训练轻量估计器 | 模型感知的需要和效用与真实需要频繁 misaligned；估计器驱动的 controller 提升决策质量 |
| **Tool-Overuse Illusion** (arXiv 2604.19749, Mar 2026) | 知识认知错觉：模型误判内部知识边界；outcome-only rewards 无意中鼓励过度调用 | 知识感知边界对齐减少 82.8% 工具使用同时提升准确率；平衡 reward 砍 66.7% 不必要的调用 (7B) |
| **Entropy & Tool-Use** (ACL 2026) | 熵在优化工具使用行为中的作用 | — |

**共同点：** 都是训练/策略层面的——教模型什么时候不要调。**不检查**调了之后选没选对。

### 路线 B — 工具是否允许调用（安全/权限/策略）
| 论文 | 要点 | 关键数据 |
|:-----|:-----|:---------|
| **AgentSpec** (arXiv 2503.18666, ICSE 2026) | 轻量 DSL 运行时约束 | 开销 < 5ms/次评估 |
| **Veto** (veto.so, 2026) | 确定性外部策略引擎，7 参数 May judgment | 强制确定性 = 1.0 |
| **Edictum** (edictum.ai) | 开源运行时治理库 | 拦截后评估：允许/阻止/审批/记录 |
| **ABC** (arXiv 2602.22302) | Agent 行为合约：(P)前提(I)不变量(G)治理(R)恢复 | 形式化保证 |
| **AGT** (Microsoft, 2026.04.02) | 7 包治理工具包，MIT 许可 | 覆盖 OWASP Agentic Top 10 |
| **Probity** (github.com/nizos/probity) | 编码代理过程纪律 | 通过 agent hook 系统工作 |
| **Over-Privileged Tool Selection / ToolPrivBench** (arXiv 2606.20023, CAS/CUHK/PKU, Jun 2026) | 研究 agent 在足够低权限替代方案存在时仍选择/升级到高权限工具 | 11 模型评估：Qwen3-8B 64.9% OPUR、LLaMA-3.1-8B 55.9%；6/11 模型 ≥30%；Claude 4.6 Sonnet/GPT-5.2/GLM-5 <10% |
| **Quantitative Certification** (arXiv 2510.03992) | 工具选择的形式化鲁棒性认证 | 认证工具选择在对抗扰动下的鲁棒性 |

**共同点：** 检查权限级别——是不是调了太强的工具。**不检查**工具本身是不是最优的。

### 路线 C — 工具选择偏差（为什么会选某个工具）
| 论文 | 要点 | 关键数据 |
|:-----|:-----|:---------|
| **BiasBusters** (ICLR 2026, Oxford/Microsoft) | 系统性工具选择偏差：模型固定一个 provider 或偏向前置工具；(1) 语义对齐是主因；(2) 小扰动可显著改变选择；(3) 预训练暴露放大偏差 | 7 个 LLM 评估，TV 距离 δ_model ≈ 0.25-0.38；提出 filter+uniform sampling 缓解 |
| **Tool Selection Bias** (OpenReview) | 类似方向，更偏 metadata-level | — |

**共同点：** 揭露 LLM 选工具有系统性偏差。**不提供**运行时验证/纠正。

### 路线 D — 工具链规划（多步最优排序）
| 论文 | 要点 | 关键数据 |
|:-----|:-----|:---------|
| **Feasible is Not Enough** (ACL 2026 Findings) | 多解工具图上 cost-aware 最优工具链规划 | 承认多解存在，选 cost 最低的 |
| **ToolTree** (ICLR 2026) | MCTS 双反馈工具规划 + 双向剪枝，training-free | 4 个 benchmark 一致提升 |
| **AutoTool** (AAAI 2026) | 图基轻量级工具选择，graph-based | 减少推理开销，提升选择效率 |

**共同点：** 规划阶段的（pre-execution）。优化排列组合找到最优链。**不验证**执行阶段的选择是否正确。

### 路线 E — 工具调用效率 / 运行时守卫（有没有冗余）
| 论文/工具 | 要点 | 关键数据 |
|:----------|:-----|:---------|
| **Tool Spam** (agentpatterns.tech, 2026) | 4 种冗余模式：重复签名/参数抖动/重试放大/扇出泛滥 | 典型案例：1 次 = ~$0.10，6 分钟 52 调用 = ~$3 |
| **MLflow ToolCallEfficiency** (Dec 2025) | Agentic Judge 检测冗余/低效调用 | 5 种低效案例 + 5 种高效案例，LLM-as-Judge |
| **Session-Scoped Deduplication** (dev.to) | 会话级 tool+args_hash 去重 | 防止同一工具同一参数重复调用 |
| **ToolCallCorrectness** (MLflow, companion PR) | Judge 检测工具是否正确响应用户意图 | — |

**共同点：** 检测**重复调用**。**不检查**工具选得对不对（比如用 web_search 代替了专门 API）。

### 路线 F — 工具选择自验证（选对没有）
| 论文 | 要点 | 关键数据 |
|:-----|:-----|:---------|
| **ToolVerifier** (Meta, arXiv 2402.14158, Feb 2024) | 自验证：选择时和参数生成时 self-ask contrastive questions 区分相近候选工具 | ToolBench 4 任务/17 unseen 工具，平均 +22% over few-shot |

**最接近我们 gap 的工作。** ToolVerifier 是 **selection-time** self-verification——在 LLM 选择工具的过程中加入提问环节。但它不是 **post-hoc** 验证——不会在工具已经调了之后回头看它是否最优。

### 空白总结

```
现有 6 条路线覆盖：
  A. 要不要调 ✓（训练/策略教模型省着用）
  B. 允不允许调 ✓（安全/权限门控）
  C. 为什么偏这个 ✓（分析型，不纠正）
  D. 怎么规划最优链 ✓（执行前规划）
  E. 有没有重复调 ✓（运行时去重）
  F. 选的时候对不对 ✓（ToolVerifier，selection-time self-verify）

唯一的空白：
  执行后回头看：已经调了的工具，对于当前问题是不是最优选择？
  具体来说：
  ┌──────────────────────────────────────────────────────────┐
  │ 1. 有没有更高效/更便宜/更快完成同一目标的工具？           │
  │ 2. 这次调用是否产生了冗余（已有信息可从之前调用获得）？     │
  │ 3. 是否有工具组合优于单一工具选择？                       │
  │ 4. 工具是否 over-privileged（调了权限过大但不需要的）？     │
  │ 5. 工具是否 over-scoped（做了问题的范围外的事）？          │
  └──────────────────────────────────────────────────────────┘
  → 这正是 Double-Check Tool Use 要填补的缺口：
    一个 post-hoc 工具选择正确性验证器
```

### Benchmarks
- BFCL V4: GLM-5.1 77.5 (最佳)
- MCP-Atlas: 最佳 83.6% pass rate (Gemini 3.5 Flash), 36 服务器/220 工具/1000 任务
- **ToolPrivBench** (新, Jun 2026): 544 场景×8 领域×5 风险模式，专门测 over-privileged tool use

## Reference Files

- `references/root-matrix.md` — Verified specs for Find N2/N3/N5/N6/OnePlus Open/Z Fold 7 (GSMArena + manufacturer verified)
- `references/tool-use-verification-landscape.md` — Full 6-route taxonomy (A–F) of 20+ papers/tools on tool use verification, with identified gap: post-hoc tool selection correctness verification
- `references/plugin-architecture.md` — Hermes Plugin implementation: hooks, tools, search engine, and how Plugin + Skill complement each other
- `references/bilibili-video-factcheck-methodology.md` — Workflow for fact-checking B站/YouTube videos: subtitle extraction → claim extraction → parallel subagent delegation → combined report. Use when user shares a video link for analysis
- `references/yuegeshuo-video-verified-claims.md` — Verified claim-by-claim results from 月鸽说《有一个性别上厕所时总会被"凝视"》analysis (2026-06-21). 6/10 accurate, 1/10 partial, 3/10 fabricated/distorted
- `references/price-corrections.md` — Known price errors and their corrections from AI Foldable research
- `references/verification-frameworks.md` — Full academic framework reference list
- `references/framework-tradeoffs.md` — Journalism vs LLM Academic: strengths, weaknesses, and why each round borrows from which tradition (researched against actual papers June 2026)
- `references/plugin-architecture.md` — Hermes Plugin implementation: hooks, tools, search engine, and how Plugin + Skill complement each other
- `references/ai-perception-research.md` — Verified cross-cultural AI perception data (Pew, Edelman, KPMG, Anthropic). Covers: AI in relationships, chat analysis privacy, environmental impact, China/HK/US differences. Use when user asks about AI fear/trust/acceptance topics.
- `references/cloud-vps-network-access.md` — Verified mainland China cloud VPS (Tencent Cloud) network access patterns: which LLM APIs work from mainland vs Hong Kong nodes, Hermes deployment/migration paths on Tencent Cloud Lighthouse. Key finding: DeepSeek (api.deepseek.com) ✅ accessible from mainland — do NOT classify as overseas/blocked.
- `references/benchmark-methodology.md` — Repeatable 40-question LLM accuracy benchmark (4 categories × 10 qs). Error type taxonomy, category-level patterns, Δ measurement methodology. Use when evaluating a model's factual accuracy before/after Double-Check pipeline.
- `references/benchmark-v4-3judge-results.md` — Actual benchmark results from 2026-06-25: DeepSeek V4 Flash (62.5%→97.5%, +35pp) vs V4 Pro (72.5%→97.5%, +25pp). Includes 3-judge agreement patterns, shared error types, and 3 human-arbitration cases (AI trust%, SSD price, Cathedral hours). Use as reference when discussing benchmark methodology or when interpreting pipeline effectiveness claims.
- `references/demo-video-narration.md` — MiMo TTS + FFmpeg workflow for adding AI-narrated voiceover to Remotion-generated demo videos. Use when the user asks to add narration to a product demo video.
- `references/security-audit-checklist.md` — Public GitHub submission security audit: search patterns, file types to review, cleanup workflow. Run before any competition/hackathon submission or repo going public. Real incident: NOVA 2026 audit found personal documents, audio transcripts, and local file paths.
- `references/ai-pr-open-source-contract.md` — Charlie Marsh (Ruff/uv/Astral) analysis: AI-generated PRs breaking open source contributor contracts, review cost shifting, Lisp Curse connection. Use when discussing AI impact on code quality or community health.

## Hermes Plugin (External Implementation)

This skill's methodology is also packaged as a **native Hermes Plugin** at `~/.hermes/plugins/fact-check/`. The Plugin handles **always-on** verification (every turn via `pre_llm_call` + `transform_llm_output` hooks). This skill handles **deep audit** (full Round 1-4 with multi-agent parallelization). They share the same methodology and academic frameworks.

| Component | Location |
|:----------|:---------|
| Plugin files | `~/.hermes/plugins/fact-check/` |
| GitHub repo | `onezion12344/double-check-agent` |
| Plugin docs | `skill_view("fact-check", "references/plugin-architecture.md")` |

**学术论文核查专有子模式：** 当核查对象是带有大量论文引用的研究报告时，使用 `references/academic-paper-factcheck.md` 中记录的专用流程——SIFT优先使用已提取的论文全文逐字对照，CoVe根据不同论文类型的可验证性分级处理。

**When to use which:** Enable the Plugin for zero-effort pre-answer checks on every turn. Load this skill (`/skill fact-check`) when the user asks for deep multi-round verification or when you need to run the full SIFT → CoVe+FIRE → FABLE → Truth Sandwich pipeline.

## 触发条件（两种模式）

| 模式 | 触发时机 | 触发条件 | 做什么 |
|:--|:--|:--|:--|
| **Phase 0.5**（Pre-answer 预核查） | **回答前** | 用户问题含事实主张（价格/时间/地址/名称/数值） | 先搜≥2源验证，再回答 |
| **Round 1-4**（Post-answer 后核查） | **回复后** | 回复≥300字且含≥5个具体主张 | 完整四轮（SIFT→CoVe+FIRE→FABLE→Truth Sandwich） |

**选择规则**：
- 用户问 "XX多少钱 / XX地址 / XX几点关门 / XX怎么样" → **Phase 0.5**
- 我已经发了长回复且含大量事实 → **Round 1-4**
- 两者都满足（用户问事实问题+我打算发长回复）→ **先 Phase 0.5 验证 → 回答 → 如果回答密集再补 Round 1-4**

**触发粒度**：仅主 Agent 启动。子 Agent (delegate_task) 不自动启动技能 — 它们的核查结果由主 Agent 在第 3-4 轮汇总。

## ⛔ 自核查协议（用户强制要求）

在回答任何涉及工具、模型、项目状态的比较性主张前，必须先做自核查：

```
走完 5 步，再发送：

1. 我即将说出的每个数字/百分比来自哪里？
   → 如果来自记忆 → 必须重新验证（读取文件或搜索）
   → 如果来自源文件 → 引用行号

2. 每条对比性主张（A vs B）是否验证了两边？
   → "A 有 X 功能而 B 没有" → 确认 B 确实没有
   → "A 的星标比 B 多" → 检查当前实际星标

3. 是否有任何用户可能质疑的假设？
   → "Termux 不能跑" → 没有验证实际文档，就是错的
   → "这个工具有 XX 行代码" → 真的去数一下行数

4. 如不确定 → 坦白说"让我确认一下"→ 搜索/读取后再说
   用户容忍"检查中"远大于容忍错的内容。

5. 至少找到 1 个可验证的源（文件、网页、代码）再交付。
```

**触发条件：** 任何含 ≥3 个事实性主张的回复。
**用户行为模式：** 他会逐条核对你的 claim。如果发现一条错误，后续所有 claim 的可信度都会打折。
**平台兼容性声称专项：** 所有关于"X 能不能在 Y 上跑"的 claim，必须先查官方文档/安装脚本/README。不要默认不能跑。

## ⛔ 第 0 轮 — 去重门（跑之前先检查）

**目的**: 防止同一内容被多个 Agent 重复核查。同时在用户处于紧急场景时跳过。

```
急停检查：
  用户是否在时间敏感场景？
    → 正在餐厅点菜 / 手机快没电 / 路上缺水 / 迷路 / 找巴士
    → YES: 回答紧急问题。DEFER fact-check。标注 "第 0 轮: 紧急场景延后"
    → NO: 继续去重门

去重检查：
  1. 检查上下文: 这条内容已经被核查过了吗？
     → 搜索本轮对话中的 "第 4 轮" / "Truth Sandwich" / "核查报告"
     → 搜索本轮对话中的 "Phase 0.5" / "Pre-answer 预核查"
  2. 如果已有完整结果: 直接用。不重跑。
  3. 从中断点继续。
  4. 没有: 进入 Phase 0.5（如果用户问题含事实主张）或 Round 1-4（如果是我刚发了长回复）
```

**判断标准**: 同一个内容对象只跑一次 Phase 0.5。内容变了（新事实、新主张）才算新核查。

**并行场景**: 如果主 Agent 决定用 delegate_task 加速外验（Phase 0.5 或 Round 2），子 Agent 只做验证部分，不做完整流程。主 Agent 收到结果后继续。

## 🔍 Phase 0.5 — Pre-answer 预核查（新增）

**目的**: 在回答用户之前，先核实问题中涉及的事实主张。防止基于错误假设回答问题。

**触发**：紧接第 0 轮之后判断。如果用户问题**不包含**事实主张（纯闲聊/问意见/问概念），跳过，直接正常回答。

### 步骤

```
Step 1 - 提取用户问题中的事实主张：
  扫描用户问题，提取所有事实性实体
  → 价格: "XX 多少钱" "预算 XX" "XX 要花多少"
  → 时间: "几点关门" "什么时候出发" "XX 多久"
  → 地址/位置: "XX 在哪" "怎么去 XX"
  → 名称: "XX 是什么牌子" "XX 好不好" (含产品/店家/地名)
  → 数值: "几公里" "多大" "多少"

  输出: 待验证主张列表（每条标注类别: 价格/时间/地址/名称/数值）

Step 2 - 分两组处理：
  第一组 - 时效敏感项（强制外验，不依赖内部知识）：
    → 价格、营业时间、时刻表、地址
    → 这些必须 web_search，不能用记忆或猜测
    → 至少搜索 2 个独立来源

  第二组 - 通用事实项（可先用内部知识，不确定再搜）：
    → 产品参数、历史事实、名称确认
    → 先用内部知识判断
    → 置信度低时 -> web_search 补充
    → 置信度高 -> 直接采用（FIRE 论文验证了大部分 claim 不需要搜）

Step 3 - 并行搜索（时效敏感项优先）：
  对第一组：立即并行 web_search ≥2 源（用 batch_search 或多个搜索调用）
  对第二组：置信度低时才触发搜索

  搜索要求：
  - 每条搜索独立，不参考我的原始回答（CoVe 原则）
  - ≥2 个独立来源（IFCN 标准）
  - 检查不同平台/角度，不重复搜同一个来源

Step 4 - 合成验证结果（四类状态）：
  ✅ 基本正确 — ≥2 独立来源一致确认
  ⚡ 有争议 — 来源之间有矛盾，或独立来源不足（如只搜到同一家媒体的多篇文章）
  ❓ 查不到 — 搜了但没找到相关信息。❓≠❌，不要把它当证据说"不存在"
  ❌ 错 — 来源明确反驳该主张

  ⚠️ 未外验 — 非时效敏感项，仅用 LLM 内部知识（需注意：LLM 内部知识可能过时或有误）

Step 5 - 基于验证结果回答问题：
  使用已验证的信息作答
  对 ✅ 项：直接使用，可标注来源
  对 ⚡ 项：在回答中明确标注争议："XX 的说法存在争议，不同来源说法不一"
  对 ❓ 项：诚实说"没有查到可靠信息"——不要用查不到来暗示"所以它是错的"
  对 ❌ 项：不要重复错误说法，直接给出正确的
```

### 输出规范

回答时，对已验证的事实主张采用行内标注：

```
OnePlus Open 闲鱼约 ¥2,400✅（BDtheBear 2026.06，2源确认）
Nillkin 键盘约 ¥460❓（搜了一圈没找到统一报价，Amazon $79.99 但淘宝 ¥430-500，渠道差大）
Correos 周日关门✅（官网确认）
行李转运服务 ⚡（搜到 2 家，评价两极分化，无法判断哪家可靠）
```

**四类状态回答指南：**
- ✅ 标注来源，直接回答
- ⚡ 说明分歧："说法A vs 说法B，目前没有定论"
- ❓ 诚实说"没查到"——不要用❓当证据
- ❌ 纠正但不重复错误："这个说法不对，实际是XX"

### 答后补充

如果 Phase 0.5 后的回答 ≥300 字且含 ≥5 个主张 → 继续走 **第 1-4 轮** 作为补充杀（backstop）。此时第 1 轮的 SIFT 需要把 Phase 0.5 验证过的内容标记为 ✅（已确认），只对新增/未验证的主张做 ⚠️ 标记。

### 不自查场景

- 纯主观问题："哪家好吃" "哪个好看" → 跳过，不需要验证
- 概念解释："什么是 RAG" "量子纠缠是什么" → 跳过 Phase 0.5，直接回答
- 用户明确说"你看看这个"给我文件/URL → 使用 Round 1-4 流程（SIFT 对照），不需要 Phase 0.5
- 紧急场景（第 0 轮已跳过）→ 直接回答

## 第 1 轮 — SIFT 源码对照

**目的**: 区分「原文有的」和「我补的」，不做外部搜索。

```
Stop: 暂停，不信任刚写的内容
Source: 每条主张标注来源
  - ✅ 引用源: km 标记、教堂名 → 逐字对照
  - ⚠️ 推理补全: 价格、地址、营业时间 → 标记为"需外验"
  - ❌ 矛盾: 原文说 X，我写了 Y
Trace: 追溯不在原文里的 → 它们从哪来的？(之前搜索/记忆/推测)
```

输出: **缺口清单** — ✅ ⚠️ ❌ 三类，不越界去做外验。

## 第 2 轮 — CoVe+FIRE 交叉验证

**目的**: 对第 1 轮的 ⚠️ 和随机抽 20% 的 ✅ 做外部验证。

```
CoVe (Chain-of-Verification):
  生成验证问题: "这个地址对吗？" "这个价格对吗？"
  独立回答: 不参考我原来的内容，用新搜索的结果回答

FIRE (Iterative Retrieval):
  搜索 → 不满足 → 再搜 → 直到证据收敛
  每条 ⚠️ 主张 ≥2 个独立源 (IFCN 标准)

时效敏感项强制外验:
  - 营业时间 (最容易变)
  - 价格 (次容易变)  
  - 时刻表 (再容易变)
  - 地址/场馆 (基础设施可能搬迁 — 如 Santiago 巴士站 2021 年已搬)
  这四个不依赖原文 — 原文可能是几年前的。
```

输出: **验证清单** — 每条主张: 基本正确 ✅ / 有争议 ⚡ / 查不到 ❓ / 错 ❌

## 第 3 轮 — FABLE 影响分析

**目的**: 修正后的错误哪些真的影响决策？不查新东西。

```
FABLE:
  Functional? — 这个修复功能上需要吗？
  Actionable? — 会改变用户做什么吗？
  Blocking? — 不修会打断关键路径吗？
  Likelihood? — 用户遇到这个错误的概率多大？
  Effort? — 修起来成本多大？

三级:
  🔴 Critical Path: 不修会打断行程 (如: 周日取不了行李)
  🟡 Experience: 修了更好但不打断 (如: 餐厅地址错一条街)
  🟢 Cosmetic: 纯文字修正 (如: 酒店名字格式)
```

输出: **分级修复清单** + 替代方案 (对 🔴 必须给方案)

## 第 4 轮 — Truth Sandwich 修正

**目的**: 结构化输出修正，给用户上下文。

```
Truth Sandwich:
  1. What was written (原话)
  2. What's wrong (为什么错)
  3. What's correct (正确是什么)
  4. Source (来源)
  5. Action needed? (需要改变行程吗？)
```

---

## 实例：Camino Notion 核查

- 第 1 轮: 发现 23 条 ⚠️ (我补的地址/价格), 55 条 ✅ (原文有的 km/教堂)
- 第 2 轮: 23 条 ⚠️ 外部验证, 发现 4 个地址错 + 6 个价/时间错
- 第 3 轮: 1 个 🔴 (Correos 周日关门打断 Madrid), 6 个 🟡, 3 个 🟢
- 第 4 轮: Truth Sandwich 修正所有 + 替代方案

## 实例：AI Foldable 手机/配件核查 (2026.06)

### 六轮核查历程
- 第 1 轮: 44 条 ✅ 37 / ⚠️ 3 / ❌ 4（价格全偏低 2-2.6× — Nillkin ¥200实为¥500, Logitech ¥350实为¥620, Poetic $23实为$59）
- 第 2-3 轮: 新增 21 条 → 65 总条 / ✅ 53 / ⚠️ 10 / ❌ 2（BOW HB199 无触控板, GPU 数据从社区抄的→GSMArena验证）
- 第 4-6 轮: 持续更新 Notion 页面 + 修正 SIM 规格 / eSIM / 典藏版 / 系统版本细节
- 错误率趋势: 9% → 3% → 0% 残余

### 手机配件价格陷阱（新增）
- **1688 批发价 ≠ 个人零售价**: 同一个壳 1688 ¥15-30, 淘宝 ¥50-80, Amazon $23-60
- **同一商品多平台价差可达 2-3×**: Nillkin 官方 $69.99, Amazon US $79.99, Amazon UK £49.99(~$63)
- **永远同时查 ≥3 个平台**: 淘宝/京东/拼多多 + Amazon + 官方商店
- **二手/闲鱼价格**: 无法自动化验证 — 标记为"估算"，不列为确定数据

### GPU 基准陷阱（新增）
- GSMArena 的 3DMark Wild Life Extreme 数据 = 可信 (N3: 4,529-4,588)
- 社区/YouTube 跑分 = 不可信 — 环境温度/调频策略/固件版本差异太大
- 不要混用 onscreen 和 offscreen 数字 (如 GFXBench Car Chase onscreen N2=59fps，但我错误地引用了 104fps offscreen)
- 来源统一: GSMArena review page 4 (有完整图表) + Notebookcheck UL Solutions 数据

### OPPO Pen 技术陷阱（新增）
- 52audio 拆解: OPPO Pen = Goodix GP850 主动电容笔，不依赖 EMR 数位板层
- OPPO 官方兼容列表 (opposhop.cn): 仅 Find N2/N3/N5/OnePlus Open
- 普通手机不支持 — 触控控制器需固件支持 USI/HPP 笔协议

---

## 注意事项

- ⛔ **旅行手册/团行程 ≠ 用户实际预订。** 永远优先取用户 app 截图的酒店名、CI 时间、价格。团体行程表只是参考，不是真相。Camino 案例：UMSL 团住 VILLAJARDÍN，Harry 自己定 Pons Minea——用错了会导致整个路线计划报废。
- 第 1 轮禁止外部搜索 — 只对照原文
- 第 2 轮不判断影响 — 只验证
- 第 3 轮不搜索 — 只分析已验证结果
- 每轮必须有不同的输出格式，防止混在一起
- **回答完当前问题再开新话题。** Harry 说 "回答完" — 意思是完成当前回答，不要把答案和下一步混在一起。尤其是路上紧急场景（点菜、找路）

### ⛔ 第 1 轮前置要求：保存源文本

在启动核查前，必须已提取并保存原文全文。若源文本未提取或已从上下文驱逐：
1. 重新提取原文 (web_extract / mcp_anysearch_extract)
2. 完整保存为本地 temp 文件以便逐行对照
3. 才开始第 1 轮

无源文本的 SIFT 是盲人摸象。不要依赖上下文摘要——摘要会遗漏关键细节。

### 域特定 vs 结构轮次（不要混淆）

❌ 错误：三个 agent 按域分（住宿/路线/餐馆）→ 本质是同一方法跑三次
✅ 正确：三个 agent 按结构轮次分（SIFT源码对照 / 外验 / 影响分析）→ 每轮降维

域特定分块仅适用于**并行加速**（第 2 轮大量外验时），不适用于轮次本身。

### 并行子 Agent 核查模式（仅用于加速第 2 轮外验）

当第 2 轮外验量很大时（≥15 条 ⚠️ 主张），可并行 2-3 个子 Agent **同时做外验**（不是做不同轮次）。每个子 Agent 都遵循 fact-check 第 2 轮方法论。

⚠️ 这是**横向分块**（加速），不是轮次替代。第 1、3、4 轮仍然由主 Agent 串行执行。

### 分块策略
```python
delegate_task(tasks=[
  {goal: fact-check phone specs + root claims,  toolsets: ["web","terminal","skills"]},
  {goal: fact-check accessories + prices,       toolsets: ["web","terminal","skills"]},
  {goal: fact-check performance + features,     toolsets: ["web","terminal","skills"]}
])
```

### 每个子 Agent 的 task context 必须包含
1. `Load skill_view(name='fact-check') first` — 让子 Agent 遵循 4 轮方法论
2. 具体的子主张列表（逐条列出要核查的内容）
3. 要求结构化输出：✅ 基本正确 / ⚡ 有争议 / ❓ 查不到 / ❌ 错 + 修正值 + 来源

### ⚠️ LLM Judge LLM 是循环的 — 承认而非隐藏（2026.06.25 新增）

当用 LLM 判断 LLM 自己的输出是否事实正确时，法官和被告有同样的幻觉和偏见。行业对此有三种应对：
1. **纯人工标注 ground truth**（SimpleQA）— 回避 LLM judge，但只能测"答案不变"的问题
2. **多 Judge + 人工校准**（FACTS Grounding）— 3 个不同家族的 LLM judge，用人类评分校准
3. **专用小模型**（HHEM）— 微调 DeBERTaV3 做 binary classifier，不是通用 LLM

Double-Check 的 benchmark 采用混合方法：多 judge 对比 + 分歧透明 + 无法裁决的交人类仲裁。

**规则**：
- 单一 LLM 的判分不能作为"事实真相"呈现
- 所有 judge 之间的分歧必须透明标注，不能静默消掉
- 不存在单一正确答案的问题标记为 ⚡ 或 ❓，不强行归入 ✅/❌
- Pipeline 最诚实的回答有时是"这个问题没有单一正确答案"

详见 `references/industry-benchmark-methodology.md`

### ⚠️ verify_claims 工具限制（2026.06.23 新增）

Hermes 内置的 `verify_claims` 工具是一个搜索式验证工具，但它有严重限制：

- 它对**意图错误的 claim 几乎全部返回 ✅**——因为它做的是关键词匹配式的搜索，不是独立验证
- 2026.06.23 A/B 测试：6 条刻意写错的 claim（价格差 2×、GPU 型号错、特征虚构），全部返回 ✅ 基本正确
- 根本原因：搜到相关内容就判 ✅，不检查内容是否真的支持该 claim
- **正确使用姿势**：`verify_claims` 只作为**第一轮线索发现**（看看搜到了什么），不作为验证结论
- **真正的验证**需要走 Phase 0.5 的完整流程：抽出 claim → CoVe 独立搜索 → FIRE 迭代 → 对照原始来源

### ⚠️ 过时真相信任风险（2026.06.23 新增）

即使「已验证」的数据也可能过时：
- Correos Santiago 周日营业：旧数据说关门（2024 前正确），2024 年后改为 7 天营业
- Santiago 巴士站地址：2021 年搬迁，旧地址仍然出现在很多旅行指南中
- 价格类数据的半衰期最短（几周到几个月）
- **时间敏感类主张（营业时间/价格/地址/活动日程）**：必须查当前来源，不能依赖之前验证过的结果

修复方法：查官网或用 `site:domain` 限制搜索范围。

### 价格核查要点
- 价格是最常见错误源。不要依赖记忆或估算。
- 实际查验时：搜索平台名 + 商品名 → 提取当前价格 → 标注币种和日期
- 二手/优惠价格 ≠ 当前零售价。明确标注来源平台和是否为促销价。
- 例：Nillkin Cube Pocket — 第一次说 ¥200（是记忆/批发价），实际 Amazon $79.99（2026.06）

### ⚠️ 消息平台输出截断（2026.06.25 新增）

事实核查的四轮报告（SIFT → CoVe+FIRE → FABLE → Truth Sandwich）结构完整但占用大——在 Telegram 等消息平台上容易超出长度限制被截断，导致用户看不到关键修正。**用户不得不要求重发是一种失职。**

**Mitigation 策略（按优先级）：**

1. **倒置交付顺序** — 先发 Truth Sandwich（修正本身，用户最需要的），再发完整四轮详情。如果被截断，至少修正到了。
2. **内联浓缩版** — 每一轮输出用 3-5 行文字而不是完整段落。详细证据链放在引用文件中，需要时才展开。
3. **分条发送** — 把每一轮作为独立消息发送，用序号 1/4、2/4 标识。比一口气全发出去更可靠。
4. **修正如短** — 如果只发现 1-2 条错误（如本 session），直接在原文基础上标注修正，不需要铺开完整四轮。完整四轮保留在内部过程即可。

**选择规则：**
- 1-2 条轻微错误 → 选项 4（修正如短）
- 3-5 条错误且影响🟡以上 → 选项 1（倒置顺序）
- 6+ 条错误或🔴关键路径 → 选项 2 或 3（分条/浓缩）

**实例：** 本 session 核查 Tencent Cloud 网络访问问题，只有 1 条❌ + 1 条⚡ → 应当在原文标注修正，不需要展开完整四轮导致截断。

### ⚠️ 网页交付（"事实核查 网站呈现/cf"模式 — 2026.12.02 新增）

当用户要求"事实核查"后补充"网站呈现"、"cf 给我"或类似表达时，表示他想要一份**可视化的独立报告**，而非仅内联文本。这个信号意味着：

**触发词：** "网站呈现"、"cf"、"html 呈现"、"做个网页"

**交付流程：**
1. 在 Telegram 先发**浓缩文本版**（按上述 Mitigation 策略选择对应格式）
2. 同时创建独立的 HTML 文件，包含完整的四轮核查内容
3. 在消息末尾告知文件路径

**HTML 报告的标准结构（5区块）：**
| 区块 | 内容 |
|:-----|:-----|
| Header | 标题 + 整体评级 + 时间戳 |
| Stats Row | ✅/⚠️/❌/总主张数 + 核验论文数 |
| Round 1 - SIFT | 逐条对照表 + 原文引用证词 |
| Round 2 - CoVe+FIRE | ⚠️ 项外验结果 + 独立搜索来源 |
| Round 3 - FABLE | 影响分级卡片（🔴/🟡/🟢） |
| Round 4 - Truth Sandwich | 每修正（原话→为什么错→正确→来源） |
| 方法论 | 搜索后端、轮次、限制声明 |

**参考文件：** `references/html-factcheck-example-20251202.md` 包含真实 HTML 报告的截图作为参考。

### ⚠️ 跨境地区服务可用性陷阱（2026.06.26 新增）

当用户需要同时服务 >1 个地区（如深圳+香港、大陆+海外）时，云存储/网络服务的选择必须检查两地可用性：

| 服务 | 在大陆可用 | 在香港/海外可用 | 核查来源 |
|:-----|:----------:|:---------------:|:---------|
| Google Photos | ❌ **被墙** | ✅ | Wikipedia, OxeraVPN 确认 |
| Dropbox | ❌ **被墙** | ✅ | |
| OneDrive | ✅ Azure CN | ✅ | Microsoft 大陆有合规 |
| Ente | ✅ App端 | ✅ | 无域名墙 |
| pCloud | ⚠️ 瑞士服务器可能慢 | ✅ | |

**预防方法：** 推荐跨地区云服务时，先问用户「你主要在哪些地区使用？」如果 >1 个地区，自动检查每个服务在全部地区的可用性，不要假设「国际服务全球可用」。

### 常见陷阱

- ⛔ **公开提交前必须做安全审计（2026.06.26 新增）**：competition/hackathon 提交的 GitHub repo 必须 audit 干净——email drafts、audio transcripts、personal academic records、完整文件路径全是泄漏源。详见 `references/security-audit-checklist.md`。不要等别人发现再改。NOVA 2026 实战：在 /tmp 克隆两个 repo 后 grep 了 7 个模式，发现并清理了 8 个文件+5 处路径。
- 文章/评测里的价格可能是过时价或首发价，不等于当前价
- 同一商品在不同平台（Amazon/淘宝/京东）价差可达 2×
- 国内渠道（1688/拼多多）价低但有起批量限制，个人不一定能买到
- ⚡ **云存储价格陷阱**：存储分级名称相似（归档/冷归档/深度冷归档），容易把不同层的规格混在一起。2026.06 案例：阿里云 冷归档 取回时间我说成 1-5 分钟（实际 1-12 小时），最短存储期我说成 60天（实际 180天）——正确数据是 归档 而非 冷归档 的。**修正方法**：第三方总结文章（developer.aliyun.com/blog）的对比表可能混层数据，必须到官网价格页 (aliyun.com/price/detail/oss) 逐格对照。验证云存储价格时同时检查：① 存储费单价 ② 取回时间（是否按优先级分档）③ 最短存储时长 ④ 取回请求费 ⑤ 隐藏费用（解冻期间的临时存储费）。
- ⚠️ **Google Photos 第三方 API 骤变（2025.05 — 影响持续至今）**：2025年5月7日 Google 升级了 Photos API，**使 MultCloud／CloudHQ 等第三方工具失去了批量读取用户相册的能力**。推荐 Partner Sharing 给用户时，注明这是唯一无损迁移方式。误推第三方工具会导致用户陷入「每7天手动选2000张、原画质降级、元数据丢失」的陷阱。详见 `references/google-photos-thirdparty-api-limitation.md`。
- ⚡ **云存储加密层陷阱（2026.06.25 新增）**：说「云服务商看不到你的加密数据」时，必须检查具体加密层。**默认 SSE 加密（SSE-COS / SSE-S3）密钥在服务商手上**，员工有系统权限就可以访问。只有 **SSE-C（客户自备密钥）** 才真正做到服务商无法解密（COS 不存储用户密钥，只存 HMAC 散列值，丢失密钥=数据永久丢失）。这个陷阱同样适用于 AWS S3（SSE-S3 vs SSE-KMS vs SSE-C）和 Azure Blob。**修正方法**：一律问清楚「默认的还是自备密钥的」。如果文档没说用户提供密钥，那就是默认层，不要承诺「服务商看不到」。
- 🐙 **餐厅菜单/营养数据不可编造**：不要说 "他们有 empanada" 除非你查到了菜单。不要说 "章鱼蛋白 15g" — 实际是 29.8g（USDA）。编造的"合理数字"几乎总是错的。
- ⚠️ **引用第三方辟谣文章时的 Claim 对齐陷阱（2026.06.26 新增）**：当引用已有的事实核查/辟谣文章时，必须检查该文章覆盖的是**被核查帖子的同一主张**，而非相邻话题。用户发"高才通续签94%"帖子，我引用了 Annie Lab 关于"永居加分制"的辟谣——话题相近（都是香港身份）但主张不同（永居申请 vs 高才通续签）。辟谣文章的正确性不意味着它能自动反驳相邻话题的主张。**每条 claim 必须有自己的证据链。** 搜索时使用具体计划名称（"高才通"、"优才"、"永居"），不搜模糊的"香港身份"类关键词。用户说"See again. Fix"时，立即重读原帖、重搜、不依赖第一轮结论。
- ⚠️ **自产主张同等待遇 (Self-Produced Claims)**：当你自己做出一个事实性主张（尤其是安全评估、机制解释、配置说明），用户可能要求你"事实核查"它。这些主张必须走同样的 SIFT → CoVe+FIRE → FABLE → Truth Sandwich 流程，不能因为是你自己写的就跳过。2026.12.02 案例：关于 Cloudflare Tunnel 安全性和 CT 日志暴露的自我主张，通过 Google 官方文档 + Cloudflare 官方文档 + DEV 安全研究三方独立验证，无错误。**预防**：每次发表技术/安全/机制类主张时，先自问「这个我有来源吗？」如果没有，标记为 ⚠️ 并在输出中声明「来自推断，非官方确认」。：不要说 "他们有 empanada" 除非你查到了菜单。不要说 "章鱼蛋白 15g" — 实际是 29.8g（USDA）。编造的"合理数字"几乎总是错的。
- ⚠️ **双源污染 (Dual-Source Contamination)**：当同一话题有两个不同来源时，必须区分哪个对哪个是权威的。案例：Camino 规划时，UMSL 学生团小册子对教堂名/km 是权威来源，但对用户的酒店预订完全不是——用户自己在 Booking.com 定的。第 1 轮必须标注每条主张的*意图*来源（这个信息应该来自用户还是文档？），不只是*字面*来源。用户已确认的信息（Booking 截图、日历事件）比公开文档优先级更高。
- ⚠️ **⚠️ 来源外标记是 SIFT 的灵魂**：第 1 轮最有价值的输出不是 ✅ 和 ❌，而是 ⚠️——你补的内容。这些是第 2 轮外验的靶子。不要跳过它们，不要觉得"合理的补全"无所谓。这次 Camino 核查中，酒店名字全错但教堂名字全对——因为酒店是你补的（未标注），教堂是原文有的。如果第 1 轮把酒店标记为 ⚠️，第 2 轮外验就能纠正。
- 📊 **研究引用陷阱 (Research Citation Traps)** — 2026.06 AI 恐惧研究和 EDWC 研究中自核查发现了多类引用错误：
  - **归因混淆**：75%"AI损害就业" 的数据实际来自 Bentley-Gallup 2024，但写成了 Pew 2025。搜索结果中多个机构数字混在一起，写回答时凭记忆关联了错误出处。**预防**：每条统计数据引用时，从搜索结果中直接复制**原始出处**（调查机构+年份），不依赖记忆归因。
  - **数字反转**：Anthropic 数据显示 57% 增补型 / 43% 自动化型，但写成了"70% 自动化倾向，仅11%增补"——完全反了。**预防**：阅读数字时先确认每个百分比对应的类别再引用。比例型数据（A/B占比）特别容易在转述时把分子分母搞反。写完后用 CoVe 原则自问一次："这个比例是我从原文读到的数字，还是模糊记忆？"
  - **数字近似偏移**：Pew 数据显示 52% 工人担心，写成了 54%。搜索摘要里有多个接近数字（34%、40%、50%、52%），写回答时凭模糊记忆选了接近的整数。**预防**：每条具体数字必须从搜索结果直接提取，不在转述时四舍五入或随意取整。CoVe 自验时对每个数字问："这个精确值在哪篇原文里出现过？"
  - **自检方法**：Round 2 外验时，专门对**比例**和**归属**类主张做交叉检查。最常见的错误模式：A) 数据正确但来源错；B) 来源对但数字反；C) 数字近似但没意识到。10 条以上引用中几乎必然出现至少一条。
  - **引用年份陷阱 (Citation Year Drift)**：2026.06.23 自我核查發現 Schooler 語言遮蔽效應原始論文為 1990（Schooler & Engstler-Schooler, Cognitive Psychology），但在回答中寫成了「1993」。verify_claims 工具對這個年份偏差返回了 ✅ 基本正确——因為它做的是關鍵詞匹配搜索，搜到相關論文就判過，不檢查引用年份的精確性。**預防**：每條學術引用直接從搜索結果中複製「作者 (年份) 期刊名」的完整格式，不靠記憶輸出年份。對口耳相傳的經典研究（Schooler、Pennebaker、Milgram 等），每次引用時都快速確認一次原始發表年份。verify_claims 的 ✅ 不等於引文格式正確。 
  - **PMC ID vs 期刊名混淆**：Macchi, Poli & Caravona (2025) 的論文存於 PMC（PMC11942870）但發表於 *Journal of Intelligence*。回答時說「PMC article」不算錯但省略了實際期刊名。對學術讀者來說期刊名比 PMC ID 更有意義。**預防**：優先引用期刊名（*Journal of Intelligence* 13(3), 36）而非倉儲名（PMC11942870），除非用戶明確要找 PubMed。
  - **全球 vs 国家数据混淆**：2026.06 EDWC 能源研究中，将 IEA 的全球 DC 用电预测（945 TWh by 2030）错误地归因为美国数据，写成了"美国 800+ TWh"。实际美国预测为 ~430 TWh（45% 份额）。**预防**：多国对比时，每看到一个具体数字要先确认范围限定词——原文说的是 "global" 还是 "US" / "China"。IEA 报告常在同一句子内切换全球和国家视角，容易混淆。自检时对每个数字问："这个数字是全球总量还是某国分量？占全球多少份额？" 如果数字超过全球总量除以 2 还不符合常识，大概率是归属错了。
  - **单位混淆 (Unit Confusion)**：2026.06 AI 环境研究中，把用水量 "4.2-6.6 billion m³ of water by 2027" 写成了 "4.2-6.6% of global electricity"。搜索摘要里两个数字（4.2-6.6 + 百分比）来自同一页的不同句子，写回答时把数字和单位从不同句子里拼在一起了。**预防**：每条数字的**单位**（kWh / m³ / % / tons / $ / ¥ / ml）必须和数字来自同一来源同一句，绝不能跨句拼接。Round 1 SIFT 溯源时专门标记"数值+单位"对。CoVe 自验时对每个数字问："这个数字的精确计量单位是什么？从哪一句原文来的？"
  - **同机构多调查混淆 (Same-Institution Different-Survey)**：2026.06 AI 恐惧研究中，Edelman 在同一时间段发布了多个调查：Edelman Trust Barometer (general trust) 和 Edelman AI Flash Poll (AI-specific trust)。同一个机构、同一个名字，但对 AI 信任度的数据不同（AI Flash Poll：中国 87% AI 信任 vs 美国 32%；General Trust Barometer：中国 83 总体信任 vs 沙特 87）。写回答时容易混淆。**预防**：引用来源时写明**子报告名称**（"Edelman AI Flash Poll Nov 2025" 而非仅 "Edelman"）。子名称比机构名称更关键。搜索时增加限定词如 "AI trust" 而非仅 "trust"。
  - **数据可视化误导**：2026.06 AI 环境页面中，把 0.26ml（Gemini）、0.5ml（ChatGPT估计）、519ml（总足迹争议值）放在**同一个线性图表**上。跨越 3 个数量级的数据在线性比例上让微小值完全不可见，让极大值不成比例地被突出。**预防**：跨越 >=2 个数量级的数据用对数比例或分段图表（或单独标注每个值的文字说明）。线性图标只能用于 <10x 范围的数据。对 1000x 差距的数据，用表格或分段标注而非单一条状图。
  - **争议数字范围标注 (Range Notation)**：2026.06 AI 环境核查中，"ChatGPT 每次查询用水量"的说法从 0.26ml（Google官方直测Gemini）到 519ml（总足迹估算，包含发电间接用水）不等，相差 2000 倍。发布一个单一数字（无论选哪个）都是误导。**预防**：当搜索结果显示同一指标的不同来源数值差距 &gt;5x 时，不要选一个"折中"或"看起来合理"的数字。改为标注**范围**（如 "0.26ml–519ml，因方法论不同而异"）并在旁边解释分歧原因（直接冷却 vs 总水足迹）。方法论的差异解释比数字本身更有价值。
  - **单次 vs 总量陷阱 (Per-Query vs Aggregate)**：2026.06 AI 环境讨论中，公众关注的焦点是"每次查询用多少资源"，而真正的环境问题是总量增长（2030年~3%全球电力、13亿人用水量）。一个每次仅 0.26ml 但每天 25 亿次查询的服务，总量效应远大于"每瓶水"的叙事。**预防**：引用"每 X"指标时，自动追问"总量呢？"如果总量比单次重要，在回答中明确标注："单次——X，但按当前使用规模——Y"。不要只给单次数据而忽略总量上下文。
  - **GitHub Star 数陷阱 (Search-Snippet Star Drift)**：2026.06 微信方案对比核查中发现，搜索摘要的 GitHub star 数经常过时或近似。wechaty 我写了 20K（实际 22.9K），CowAgent 写了 44K（实际 45.6K）。搜索摘要的数字来自索引时的快照，可能差几周甚至几个月。**预防**：引用 GitHub star 数时，必须直接打开 GitHub 仓库页面读取实时数字（browser_navigate → 页面顶部的 Star 按钮旁的数字）。不要从搜索摘要、第三方排名站、或记忆中的数字引用。写对比表时，每个项目最后标注实际 Star 数（如 "45.6k ⭐（GitHub 2026.06.24 直接读取）"）。同样的原则适用于 GitHub fork 数、release 版本号等快速变化的项目元数据。
  - **付费墙元分析的效应量陷阱 (Paywalled Meta-Analysis Effect Sizes)** — 2026.12.02 核查 van Straten 2017 时发现：该论文在付费墙后，无法提取全文确认具体 d 值。**后果**：引用了未经验证的 d=0.5-1.0，在后续核查中被标记为 ⚠️。**预防**：当论文在付费墙后无法全文提取时：① 优先找 PMC/arXiv 开源版本 ② 找不到时，不要引用具体数值（d值、百分比、置信区间），改用定性描述（"大效应"、"效果显著"）并标注「未全文验证」③ 如果必须引用具体数值，需有第二独立来源（如系统综述的汇总表、Google Scholar 引用页的摘要截图）能独立交叉验证同一数字。不要因为「这是元分析」就认为里面的数字一定可以不经验证直接引用。
  - **二级来源陷阱 (Secondary Source Trap)** — 2026.06.30 Tool Use 调研自核查发现：从技术媒体（VentureBeat、Unite.AI、Medium）引用数字时，这些媒体可能 reinterpret 论文数据甚至添加自己的 inference。**三个实锤**：① BiasBusters 的机构标签我从记忆写了 "Oxford/Torch/OpenAI" 实际是 "Oxford/Microsoft"—我没去论文确认作者单位。② Metis "Alibaba" 标签来自 VentureBeat，论文本身没提 Alibaba。③ "某些 API 被选中频率差 10x" 来自 Medium 博客转述，论文本身用 TV 距离 δ_model。**预防**：每次引用数字前自问「这个数字是我从论文 abstract 直接读的，还是从二手文章看来的？」如果是二手 → 先找论文原文确认。如果找不到原文 → 标注 ⚡（来源：媒体报道）。查看 GitHub 时也要从 browser 直接读取实际数字，不从搜索 snippet。
  - **机构标签推断陷阱 (Inferred Institution Labels)** — 2026.06.30 自核查发现。从 arXiv/论文页面提取信息时，作者机构通常不在 Abstract 页面的 metadata 中，而在 HTML 全文内。**不要凭作者名字或研究领域推断机构归属**：BiasBusters 含 Philip Torr → 我推断 "Oxford/Torch/OpenAI"，实际只有 **Oxford + Microsoft**（Torch 和 OpenAI 纯属臆测）；Metis/HDPO VentureBeat 称 "Alibaba's" → 我直接标了 Alibaba，但 arXiv 页面无 Alibaba 隶属标注。**预防**：提取论文时一并获取完整作者机构块。不确定时标注 "reportedly" 或不标注机构。Abstract 页面无法获取机构信息。

---

## 📏 Benchmarking & Evaluation Methodology

> ⛔ 关键原则：**不要用单一 LLM 既当选手又当裁判。** 这是循环论证。
> **Harry 汇报偏好：直接给数字（62.5% → 97.5% +35pp），不要定性描述。方法论必须有破绽分析——LLM judge LLM 是已知问题，必须标注局限性。multi-judge 的分歧是精华不是噪音。**

当用户要求评测模型或 pipeline 的准确率时，必须遵循下面的多源判分方法论。

### 核心问题：AI 判断 AI 的循环

Double-Check 覆盖的事实类型（价格、时间、逻辑谬误、统计数据）多样性极高——无法用程序化脚本判分（如 SimpleQA 的字符串精确匹配）。这意味着：

- ❌ **程序化脚本判分不可行**：Pew 调查的"AI 信任度"没有单一正确答案
- ❌ **单一 LLM 判分不可信**：同一 LLM 出答案又判断对错，是循环论证
- ✅ **正确做法**：多 judge 面板 + 人类校准集 + 分歧透明报告

### 行业三种方法论参考

| 方法 | 代表 | 核心机制 | 适合场景 |
|:-----|:-----|:---------|:---------|
| **纯人工 Ground Truth** | SimpleQA (OpenAI, 2024) | 4,326 题，人类标正确答案，字符串精确匹配。无 LLM judge | 答案不变的事实 |
| **3-Judge + 人类校准** | FACTS Grounding (Google DeepMind, 2024) | 3 个不同 LLM judge（Gemini/GPT-4o/Claude），用人类评分校准 judge prompt | 长文本事实性，需理解上下文 |
| **专用小模型判分** | HHEM (Vectara, 2023-2026) | 微调 DeBERTaV3 做 factual consistency binary classifier | 摘要一致性检测 |

FACTS 原文：*"We selected a combination of different judges to mitigate any potential bias of a judge giving higher scores to the responses produced by a member of its own model family."*

### 推荐的 Benchmark 方案（适用此技能的场景）

```
Layer 1 — 人类校准集（关键锚点）
  创建 N 题测试集（N=20-40），每道题由人类标注 ground truth
  覆盖：价格、规格、统计数据、逻辑谬误、时间/地点信息

Layer 2 — 多 Judge 面板（至少 3 个不同模型）
  Judge A: 当前模型本身
  Judge B: 另一个不同家族的模型
  Judge C: Double-Check pipeline 自带的验证结果
  每个 judge 独立判断 raw 输出和 pipeline 输出

Layer 3 — 分歧仲裁
  3 judge 一致 → 可信
  2:1 分叉 → 标记"有争议"，人类仲裁
  3 judge 全不同 → 题目本身有问题

Layer 4 — 最终报告
  声明："LLM judge 有已知偏差。本报告采用 3 个独立 judge + 人类校准 + 分歧透明报告来约束偏差。"
```

### 不应再使用的方法（已弃用）

❌ 单一 LLM 出答案 → 同一 LLM 搜索确认 → 同一 LLM 判分——这是循环。

✅ 替代方法：见上面的 4 层方案。核心改变是引入人类校准集 + 多 judge 面板。

---

# 🧠 逻辑与理论核查（Logic & Theory Check）

> 与事实核查互补：事实核查验证"对不对"，逻辑核查验证"通不通"。
> 加载此技能即包含完整的事实核查 + 逻辑核查能力。

```
事实核查 (fact-check)              逻辑与理论核查 (logic-theory-check)
━━━━━━━━━━━━━━━━━━━                ━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 价格/时间/地址正确吗             ✅ 论证结构成立吗
✅ 数字/名称准确吗                  ✅ 推理过程有无谬误
✅ 来源是否可靠                     ✅ 因果推断站得住吗
✅ 时效敏感项最新吗                 ✅ 理论内部一致吗

        ↕ 互补 ↕
  事实错了逻辑再对也没用         逻辑不通事实对了也没意义
```

## 学术框架

| 框架 | 核心 | 来源 | 关键数据 |
|:-----|:-----|:-----|:---------|
| **FLICC** | Fake experts, Logical fallacies, Impossible expectations, Cherry picking, Conspiracy | Cook et al., Nature Sci Rep 2024 | NLP 自动化检测 F1 比前作高 2.5-3.5× |
| **Toulmin Model** | Claim → Data → Warrant → Qualifier → Rebuttal → Backing | Toulmin, 1958 | 现代论证理论基石 |
| **Jeong Prompt Ranking** | 3 种上下文增强 prompt → 排序 → 分类 | NAACL Findings 2025 | Zero-shot F1 +0.60, 29 谬误类型 |
| **FoVer** | 自然语言→一阶逻辑→自动验证 | TACL (MIT Press) 2025 | 形式化逻辑验证 |
| **CLOVER** | 组合式 FOL 翻译+验证（FoVer 后续） | arXiv 2024 | 神经符号方法 |
| **Hamborg** | Word choice, labeling, framing | Springer 2023 | 跨学科媒体偏见框架 |

## LLM 谬误检测表现

| 表现 | 谬误类型 | 说明 |
|:-----|:---------|:-----|
| ✅ **强** | 循环论证、诉诸大众、标语化 | 结构简单，模式固定 |
| 🟡 **中** | 稻草人、虚假二分、滑坡、诉诸情感、红鲱鱼 | 需要推理解码 |
| ❌ **弱** | 虚假类比、统计谬误、辛普森悖论 | 需背景知识+多步推理 |

## 5 个 Benchmark 数据集

| 数据集 | 规模 | 领域 | 谬误类型 |
|:-------|:-----|:-----|:--------|
| PROPAGANDA | 12,267 | 新闻/政治 | 18 |
| LOGIC | 2,449 | 教育对话 | 13 |
| ARGOTARIO | 1,338 | 对话/通用 | 6 |
| CLIMATE | 685 | 新闻/气候 | 11 |
| COVID-19 | 154 | 社交媒体 | 11 |

## 触发规则（与事实核查互斥）

- 如果事实核查已跑完且发现大量事实错误 → 先修正事实，逻辑核查延后
- 如果事实都正确但逻辑不通 → 启动逻辑核查
- 如果同时触发 → 串行：事实 → 逻辑
