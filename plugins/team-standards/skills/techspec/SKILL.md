---
name: techspec
description: >-
  适用于"写 techspec"、"把 PRD 变成 tech spec"、"精简 spec"、"review techspec"、"重塑已有 techspec"等请求。输入是 PRD、techspec 草稿或零散需求，输出中文。不处理实现代码、安全审计或执行；没有 PRD、或还需要先探索方案时，改用 brainstorming。
---

# Techspec

techspec 是给实现者的当前有效工程指导。它只说明现在要实现什么，不保留重命名历史、漂移记录、对账过程、旧方案或决策过程。

最终正文使用自然的工程语言。不要在 techspec 中使用本 skill 自造的术语、Open Question、TODO、假设说明、来源编号或附件编号。

## 输入与流程

1. 判断输入：PRD / 零散需求走起草路径；已有 techspec 走重塑路径。
2. PRD / 零散需求先做 5-10 行回读，说明目标、主流程、实体和已知集成；请用户纠正理解，不把回读当 approval gate。
3. 识别缺口并按“缺口处理”执行。
4. 判形态：单文件 / 文档集（判据见 canon 形态段）。文档集时主 agent 把同一工作区中的入口 + 全部详情文件整套交给 reviewer，并说明形态。
5. 按 `references/techspec-canon.md` 起草或重塑。重塑前诊断结构、内容、图示；删除不表达当前有效决策的历史叙事。
6. 写 techspec 及按需附件。
7. 按 canon 的可交付自检清单自检。
8. 按 `references/reviewer.md` 运行一次独立 reviewer；处理其 finding。修完不再复审，本轮到此为止。

读取本地 PRD 用 `Read`；读取 Confluence、GitHub 等远程来源用可用的对应工具。读不到来源时说明限制，不猜测原文内容。

## 缺口处理

先只问真正缺失的事实，且一次只问一个。

**关键 gap**：缺少该事实会阻塞主流程，或会影响整个流程的走向、责任边界或可实施性。遇到关键 gap 时暂停，只向用户提出这个问题；确认后再继续。

**非关键 gap**：已确认的主流程确实需要该细节，但缺少它不影响主流程。例如字段精度、错误码、非主流程失败分支、局部响应字段和迁移执行方式。主 agent 自动将其加入对应的 follow-ups 附件，不打断起草。

不要根据经验猜测潜在需求并创建 follow-up。用户或正文已明确排除的事项不写 follow-up，也不作为审查缺口。用户明确说某个事项“不用管”或永久不做时，直接省略，不留记录。

## 常驻章节与语义改动

所有 techspec 必须保留 canon 定义的五个常驻章节，顺序不变，不合并、不删除。不适用时保留标题，并用一句自然工程语言说明当前功能为何不涉及该项。

语义级改动必须先经用户确认，才能写进正文。以下改动通常是语义级：字段或类型变更、接口契约变更、状态机变更、新设计选择，以及任何会改变实现者行为的事实。

允许自动修复机械不一致，但必须存在一个明确、可核实且无冲突的权威来源。例如权威来源写 `posted_margin`，正文或图示误写 `margin` 时，可统一为 `posted_margin`。来源冲突、证据不足，或存在相反的用户确认时，报 🔴 并暂停。

新设计可以不同于当前代码。techspec 写目标设计；当前代码只用于证明实现现状，不能单独证明新的设计决定。若目标设计需要改造现有数据，只说明需要完成该数据迁移；不保留旧字段名或改名历史。迁移执行方式默认属于非关键 gap。

## Evidence 与 Follow-ups 附件

附件和 techspec 使用同一基名：

```text
2026-07-24-funding-rate-tech-spec.md
2026-07-24-funding-rate-tech-spec.evidence.md
2026-07-24-funding-rate-tech-spec.follow-ups.md
```

重命名 techspec 时同步重命名附件。附件为空时删除文件。附件中的 ID 不出现在 techspec 正文，并使用不可复用的随机 ID，例如 `GF-a1b2c3d4`、`FU-e5f6a7b8`。

### Evidence

Evidence 只记录 PRD / 源文档之外、当前仍有效的事实及其依据；不记录日期、原始问答、历史冲突或被覆盖的事实。没有内容时不创建该文件。

```markdown
# <功能名> Evidence

- GF-a1b2c3d4：历史 funding API 由 `market-data` 提供。来源：用户确认。
- GF-e5f6a7b8：存在 `funding_rate` 表。来源：已核实 `ma-backend__market-data/db/migrate/20260724_create_funding_rates.rb`（CreateFundingRates）。
```

- 用户确认是最高优先级依据，可证明新的目标设计。
- 代码、迁移、配置只能证明当前实现事实；记录时必须给出仓库、路径和符号或迁移名。
- 已批准 ADR、设计文档和 ticket 可作为依据；记录精确路径或链接。
- 非用户确认的外部来源相互冲突，或与 PRD / 源文档冲突时，报 🔴，由用户决定。
- 用户确认与任何其他来源冲突时，以用户确认的当前决定为准。
- 主 agent 在用户确认或核实来源后创建、更新 evidence。PRD / 源文档后来覆盖并一致时，主 agent 删除冗余 evidence 项。

### Follow-ups

Follow-ups 只记录当前未完成的非关键项，不记录状态、日期、原因或历史。没有未完成项时不创建该文件。

```markdown
# <功能名> Follow-ups

- FU-a1b2c3d4：定义列表分页规则。
```

主 agent 发现符合条件的非关键 gap 时自动创建或更新此文件。用户确认某个 `FU-*` 后，主 agent 删除该项；如果该事实不在 PRD / 源文档中，同时更新 evidence 和 techspec。用户明确永久不做该项时，直接删除该项。

reviewer 也可按 `references/reviewer.md` 的边界维护 follow-ups；它不得修改 techspec、evidence 或来源文件。

## 输出位置

默认写入 `docs/tech-specs/`；用户指定路径或目标仓库已有约定时，以其为准。

- **单文件形态**：`docs/tech-specs/<topic>-tech-spec.md`
- **文档集形态**：`docs/tech-specs/<domain>/`，包含入口文件和详情文件。
- **重塑**：就近写在输入文件同目录，或就地修改。
- **重塑外部源文档时**：使用重塑日期命名 `<YYYY-MM-DD>_<topic>.md`；不要把重塑、canon 这类工作流术语写进文件名或正文。

## 相关资料

| 文件 | 何时读 |
|---|---|
| `references/techspec-canon.md` | 起草、重塑或自检 techspec 时：正文结构、证据规则、图示规则、可交付清单 |
| `references/reviewer.md` | 运行独立 reviewer 时：输入包、核验方式、finding 格式、follow-up 写入边界 |

## 相关 skill

- 从零探索一个 feature：brainstorming
- Mermaid 语法细节：mermaid-diagrams
- 安全或合规审计：security-reviewer
- 语言自然度：优先 humanizer；不可用时 reviewer 自检

引用的 skill 不在当前环境时的兜底：brainstorming、mermaid-diagrams、security-reviewer 缺失就跳过，在交付说明里注明哪步没做。
