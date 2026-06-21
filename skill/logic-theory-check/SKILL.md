---
name: logic-theory-check
description: "逻辑与理论核查。在事实基础上检查论证结构、因果推理、谬误识别、理论一致性。与 fact-check 互补使用。"
version: 1.0.0
---

# 逻辑与理论核查

> 论证分析 + 谬误识别 + 因果推理 + 理论一致性。
> 与 fact-check 互补：事实核查验证"对不对"，逻辑核查验证"通不通"。

## 关系定位

```
事实核查 (fact-check)        逻辑与理论核查 (logic-theory-check)
━━━━━━━━━━━━━━━━━━━          ━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 价格/时间/地址正确吗       ✅ 论证结构成立吗
✅ 数字/名称准确吗            ✅ 推理过程有无谬误
✅ 来源是否可靠                ✅ 因果推断站得住吗
✅ 时效敏感项最新吗            ✅ 理论内部一致吗
✅ ≥2 独立源验证               ✅ 统计推理合理吗

        ↕ 互补 ↕
  事实错了逻辑再对也没用        逻辑不通事实对了也没意义
```

**加载方式**：
- 只查事实 → `skill_view("fact-check")`
- 只查逻辑 → `skill_view("logic-theory-check")`
- 两者都查 → 先加载 fact-check，再加载 logic-theory-check（事实优先）

## 学术框架来源

| 框架 | 核心 | 来源 |
|:-----|:-----|:-----|
| **FLICC** | Fake experts, Logical fallacies, Impossible expectations, Cherry picking, Conspiracy | Cook et al. (science denial) |
| **Toulmin Model** | Claim → Data → Warrant → Qualifier → Rebuttal → Backing | Toulmin, 1958 |
| **Johnson & Blair** | Irrelevant reason / Hasty conclusion / Problematic premise | Informal Logic, 1983 |
| **FoVer** | First-order logic verification of NL reasoning | TACL, MIT Press |
| **Hamborg** | Media bias: word choice, labeling, framing | NLP bias detection |
| **LLM Fallacy Detection** | LLMs strong on simple fallacies (circular reasoning), weak on complex | ACL/NAACL 2025 |

## 触发条件

| 模式 | 触发时机 | 触发条件 |
|:-----|:---------|:---------|
| **Phase 0.5**（Pre-answer） | **回答前** | 用户问题含论证性/因果性/理论性主张（"为什么"、"所以"、"因为"、理论名称、因果断言） |
| **Round 1-4**（Post-answer） | **回复后** | 回复≥300字且含论证结构（因果关系、推导链条、理论引用） |

**与 fact-check 的互斥规则**：
- 如果 fact-check 已经跑完发现大量事实错误 → 先修正事实，逻辑核查延后
- 如果事实都正确但逻辑不通 → 启动逻辑核查
- 如果事实核查和逻辑核查同时触发 → 串行：事实 → 逻辑

## 第 0 轮 — 去重门

同 fact-check。检查：
1. 紧急场景？→ 延后
2. 同一论证已核过？→ 直接用
3. 没有 → 进入 Phase 0.5 或 Round 1-4

## 🔍 Phase 0.5 — Pre-answer 逻辑预检

**目的**: 用户问题或指令中若含逻辑性/理论性假设，在回答前先检查其合理性。

### 步骤

```
Step 1 - 提取论证结构：
  扫描用户问题中的论证性要素
  → 因果断言: "A 导致 B" "因为...所以..."
  → 理论引用: "根据 XX 理论" "XX 认为"
  → 类比: "就像...一样"
  → 归纳: "每次都...所以总是..."
  → 统计断言: "大多数..." "研究表明..."

Step 2 - 谬误预检（快速）：
  用 LLM 内部知识检查明显谬误：
  → 稻草人: 是否曲解了被反驳的立场？
  → 虚假二分: 是否只给了两个选项？
  → 滑坡: 是否有未经论证的连锁因果？
  → 诉诸权威: 权威在该领域是否有资质？
  → 诉诸情感: 是否有情感操纵代替论证？

Step 3 - 注入预检结果到回答上下文：
  如果发现明显谬误 → 在 context 中标注
  如果无明显问题 → 标注"论证结构初步通过"
```

### 不自查场景

- 纯事实性问题（转交 fact-check）
- 个人偏好/主观判断（无需逻辑核查）
- "你怎么看"类开放问题（除非用户明确要求分析）

## 第 1 轮 — 论证结构映射（SIFT 改编）

**目的**: 不查外部资源。提取你回复中的论证结构，标注每一段推理的类型。

```
Step 1 - 提取原子论证单元：
  每个单元 = [前提] → [推理方式] → [结论]

Step 2 - 标注推理类型：
  ✅ 演绎推理: 如果 A→B 且 A 真，则 B 必真
  ✅ 归纳推理: 多次观察到 A→B，所以 A 大概率导致 B
  ✅ 溯因推理: 观察到 B，而 A 能最好地解释 B，所以 A 可能是原因
  ⚠️ 类比推理: A 像 B，B 有属性 X，所以 A 也有 X
  ⚠️ 因果断言: A 导致 B（需要排除混淆变量）
  ❌ 谬误推理: 见谬误分类表

Step 3 - 输出: 论证结构图
  前提 → 推类型 → 结论 ✅/⚠️/❌
```

### 谬误分类表

| 类别 | 具体谬误 | 识别标记 |
|:-----|:---------|:---------|
| **相关性谬误** | 人身攻击 (ad hominem)、诉诸情感、诉诸大众、诉诸传统、红鲱鱼 | 结论与前提无关 |
| **含混性谬误** | 稻草人、滑坡、虚假二分、模糊概念、歧义谬误 | 曲解/极端化/二选一 |
| **归纳谬误** | 轻率概括、样本偏差、幸存者偏差、事后归因 (post hoc ergo propter hoc) | 小样本→大结论/时间先后→因果 |
| **因果谬误** | 混淆相关与因果、忽略共同原因、因果倒置、复合原因 | 相关≠因果/遗漏关键变量 |
| **证据谬误** | 诉诸权威、诉诸无知、循环论证、乞题、特例推翻通则 | 权威不适格/无法证伪当证据 |
| **统计谬误** | 基率谬误、回归谬误、辛普森悖论、百分比混淆 | 忽略先验概率/忽视分组 |

## 第 2 轮 — 外部验证（逻辑 + 理论）

**目的**: 对第 1 轮的 ⚠️ 和 ❌ 项做外部验证。类比 fact-check 的 CoVe+FIRE。

```
FoVer 方法（一阶逻辑验证）：
  1. 将自然语言论证形式化为一阶逻辑表达式
  2. 检查形式化后的逻辑有效性
  3. 如果无效 → 标注具体违反的推理规则

理论一致性检查：
  1. 提取引用的理论/概念
  2. 搜索该理论的定义和核心主张
  3. 对照检查：回复中的使用是否与理论原意一致
  4. 特别注意：误用、过度简化、断章取义

统计推理检查：
  → 有基率吗？有对照组吗？样本够大吗？
  → 效应量多大？置信区间显示什么？
  → 混淆变量控制了吗？

因果推理检查：
  使用 Bradford Hill 标准（部分）：
  - 时间顺序（因在前果在后？）
  - 剂量反应（越多越强？）
  - 一致性（不同研究结果一致？）
  - 合理性（有理论机制解释？）
  - 特异性（因果链清晰？）
```

### 时效敏感项（强制外验）

- 理论/概念的定义和核心主张
- 统计数据的上下文（基率、样本量、显著性）
- 学术共识状态（公认/争议/推翻？）

## 第 3 轮 — FABLE 影响分析（逻辑版）

**目的**: 逻辑错误有多严重？不查新东西。

```
🔴 **Critical Path**: 逻辑错误导致结论完全不成立
  - 循环论证（结论就是前提）
  - 关键前提被证伪
  - 因果倒置

🟡 **Experience**: 逻辑有瑕疵但不推翻结论
  - 类比不精确但方向对
  - 忽略了次要混淆变量
  - 统计表达不够严谨
    
🟢 **Cosmetic**: 纯表达问题
  - 过度简化（但没歪曲）
  - 例子不够典型
  - 推理步骤跳跃（但补全后成立）
```

## 第 4 轮 — Truth Sandwich 修正（逻辑版）

```
1. What was argued（原论证）
2. What's logically wrong（逻辑错在哪）
   → 违反的推理规则 / 谬误类型
   → 为什么不对
3. What's correct（正确的推理是什么）
   → 修正后的论证
   → + 可选的更严谨表达
4. Source / Reference（理论来源）
5. Severity: 🔴/🟡/🟢
```

## 实例

### 实例 1：因果推理核查

**原回复：** "研究发现喝咖啡的人寿命更长，所以咖啡能延长寿命。"

```
第 1 轮:
  ✅ 前提: 研究发现喝咖啡的人寿命更长
  ⚠️ 推理: 相关→因果（未排除混淆变量：喝咖啡的人可能收入更高/压力更小）
  ❌ 结论: 咖啡能延长寿命（跳过因果验证）

第 2 轮（FoVer 形式化）:
  令 C(x) = x 喝咖啡, L(x) = x 寿命更长
  观察到: ∀x(C(x) → L(x))
  结论: C(x) 导致 L(x)  ← 形式逻辑无效: 相关不蕴涵因果

第 3 轮: 🔴 Critical — 混淆相关与因果是常见且严重的推理错误

第 4 轮:
  1. 原论证: 喝咖啡的人寿命更长 → 咖啡延长寿命
  2. 逻辑错: 未能排除健康用户偏差（喝咖啡的人可能整体更健康）
  3. 正确: "喝咖啡的人寿命更长，但需要控制社会经济地位和基础健康状况等混淆变量后才能判断因果关系"
  4. 来源: Bradford Hill 因果标准 / 统计学常识
  5. Severity: 🔴
```

### 实例 2：推理谬误

**原回复：** "如果 AI 监管太严，创新就会停滞。所以不应该监管 AI。"

```
第 1 轮:
  ✅ 前提: 监管可能增加合规成本
  ⚠️ 推理: 虚假二分（要么不监管=创新，要么严格监管=停滞）
  ❌ 结论: 不应该监管（忽略了适度监管的可能性）

第 2 轮:
  虚假二分谬误确认。(FoVer: 前提只考虑两种极端情况)

第 3 轮: 🟡 — 论证有缺陷但不一定全错

第 4 轮:
  1. 原论证: 严格监管→停滞，所以不监管
  2. 逻辑错: 虚假二分。忽略了中间状态和不同监管方式的差异
  3. 正确: "某些监管方式可能抑制创新，需要评估具体政策的影响"
  4. Severity: 🟡
```

### 实例 3：理论误用

**原回复：** "根据马斯洛需求层次理论，员工需要先满足生理需求才能追求自我实现。"

```
第 1 轮:
  ✅ 理论引用: 马斯洛需求层次
  ⚠️ 推理: 层级是严格顺序的（马斯洛原版确实这么说，但后续研究质疑）

第 2 轮:
  搜索确认: 马斯洛(1943)确实提出严格层级顺序，
  但后续研究(1970s+)发现层级可以共存、顺序因人而异。
  现代组织心理学已不接受严格层级假设。

第 3 轮: 🟡 — 引用经典理论没错但忽略了后续修正

第 4 轮:
  1. 原论证: 根据马斯洛，先生理再自我实现
  2. 逻辑错: 引用的理论本身已被后续研究修正
  3. 正确: "马斯洛理论认为需求有优先级，但现代研究发现各层次可以同时存在"
  4. 来源: Maslow (1943) + Wahba & Bridwell (1976) 综述
  5. Severity: 🟡
```

---

## 与 fact-check 的配合模式

### 串行模式（默认）

```
fact-check 跑完 → 事实全部正确
                      ↓ 启动 logic-theory-check
                    论证结构 → 谬误检测 → 因果验证 → 一致性检查 → 修正
```

### 并行模式（长回复同时含事实和论证）

```
delegate_task(tasks=[
  {goal: "run fact-check on these factual claims", toolsets: ["web", "skills"]},
  {goal: "run logic-theory-check on these arguments", toolsets: ["web", "skills"]}
])
```

### 独立模式

```
只查逻辑不查事实: skill_view("logic-theory-check") 单独加载
```

## 注意事项

- ⛔ **不要用逻辑核查代替事实核查**。事实错了逻辑再对也没用。
- ⛔ **不要过度分析**。日常对话中的推理瑕疵多数是 🟢 级，不必每句都纠。
- ⛔ **FoVer 形式化有信息损失**。自然语言→一阶逻辑会丢失语境和语义细节。标注"形式化近似"。  
- ⚠️ **因果推理的 Bradford Hill 标准是医学/流行病学工具**，不完全适用于社科领域。使用时说明适用边界。
- ⚠️ **谬误分类有重叠**（如 strawman 可以同时是 relevance fallacy 和 ambiguity fallacy 的子类）。选最贴切的即可，不需要穷举。

## 参考

- Cook, J. et al. *Deconstructing climate misinformation to identify reasoning errors*. (FLICC taxonomy)
- Toulmin, S. (1958). *The Uses of Argument*. (Toulmin Model)
- Johnson, R. H. & Blair, J. A. (1983). *Logical Self-Defense*. (3 basic fallacies)
- Bradford Hill, A. (1965). "The Environment and Disease: Association or Causation?" (因果标准)
- FoVer: First-Order Logic Verification for NL Reasoning. TACL, MIT Press.
- Hamborg, F. et al. *Revealing Media Bias in News Articles*. (Bias taxonomy)
- Wahba, M. A. & Bridwell, L. G. (1976). "Maslow reconsidered: A review of research on the need hierarchy theory."
