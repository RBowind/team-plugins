---
name: sddspec
description: 适用于"写 behaviorspec"、"从 PRD 和 techspec 生成行为契约 spec"、"自检 spec"、"review behaviorspec"等请求。输入是 PRD + techspec（复杂 feature），输出中文黑盒行为契约 spec + 交付 contract。spec 只放行为契约，是 AI 开发期间的 target；schema 变更归 contract。不处理实现代码、安全审计或执行。简单 feature（单 Jira 小改）不走；没有 PRD/techspec、或还需要先探索方案时，改用 brainstorming。
---

# sddspec

sddspec 给复杂 feature 从 PRD + techspec 生成黑盒行为契约 spec（behaviorspec），驱动 AI 写 test/code。spec 只写可观测的边界行为：什么触发（WHEN）、什么前提（AND）、什么可见变化（THEN）。实现细节归 design.md。

正文中文，自然工程语言。不用本 skill 自造术语，不在正文留 Open Question、TODO、假设说明（需人决策的点生成时当场拍掉，定不了进 follow-ups 附件）。

## 定位与分层

四层，各管各的，不重叠：

- **techspec（地基）**：高层工程指导，DB 关系、大体流程、架构决策、成功标准。一个 feature 一份。
- **behaviorspec（本 skill 产出）**：黑盒行为契约，按 capability 拆，放目标 repo 的 `docs/specs/<capability>/spec.md`。实现细节归到 design.md。
- **wiki（知识库）**：durable 的 domain knowledge（状态机、契约、cross-repo flow、ADR）。behaviorspec 的 durable 部分 merge 后毕业进 wiki。
- **sprint contract（本 skill 自动生成）**：交付 checklist，与 spec 同目录（`docs/specs/<capability>/`）。

## 输入与流程

1. **判断输入**：确认是复杂 feature（有 PRD + techspec），从 `repo-paths.local.yaml` 解析目标 repo，读 PRD + techspec；没有这个文件的，先问用户要目标 repo 路径。简单 feature（单 Jira 小改）提示不走 sddspec。
2. **回读对齐**：5–10 行回读，说明理解的目标、主流程、实体、已知集成，请用户纠正，不当 approval gate。
3. **缺口处理 + 生成时交互**：起草中遇到需人决策的点，按"缺口处理"执行。
4. **起草 behaviorspec**：按 `references/canon.md` 写（增量三态 + 三层信息密度 + Elaborates techspec pointer），中文。
5. **canon 自检**：按 canon 的可交付自检清单自检。
6. **Evaluator 自检**：按 `references/evaluator-prompt.md` spawn 一个独立 subagent 当 Evaluator（不用 agent team，也不自评），max 2 轮。主 agent 读 verdict 后改，每轮重 spawn 保持干净。2 轮仍 FAIL → 报告 recurring gaps，暂停转人（可能 techspec 输入不足，不是 spec 写作问题）。
7. **人 gate（spec DoD）**：Evaluator PASS 后人审机器判不住的（purity 边界、业务正确性、scope、coverage 补 techspec 没覆盖的、Open Questions/follow-ups 残留）。人不审机器已自检的。
8. **sprint contract 生成**：人 gate 通过后，从 spec scenarios 抽 B*（1:1）+ Q*（通用质量）+ Schema Changes（起草中已梳理，落 contract 不进 spec）+ Follow-ups + Pass Rule。PRD AC 覆盖由 Evaluator 把关（见 evaluator-prompt 降级 coverage），不单列双向对照表。contract 放 feature 目录（`specs/<capability>/contract.md`）。生成即 DRAFT；人评审放行后手动把 Status 改为 APPROVED——这是下游 devloop 唯一的启动授权点，非 APPROVED 不启动。
9. **交付**：spec + contract 交给下游 code 阶段（ride Build / dev agent）实现。

读取本地 PRD/techspec 用 `Read`；读取 Confluence、Jira 等远程来源用对应工具。读不到来源时说明限制，不猜测原文内容。

## 缺口处理

起草中遇到需人决策的点（未定业务规则、purity 边界存疑、业务决策如系数），一次只问一个。

**关键决策**（阻塞生成的：缺了没法往下写）→ 暂停问人，当场拍掉的写正文（resolved，不留标注）。

**非关键**（不阻塞，如字段精度、错误码、非主流程失败分支、局部响应字段）→ 进 follow-ups 附件（`FU-` 随机 ID，不进正文），生成继续。

不要根据经验猜测潜在需求并创建 follow-up。用户或正文已排除的事项不写 follow-up。用户明确说"不用管"或永久不做时直接省略，不留记录。

正文始终是已 resolved 的干净行为契约，不留 `[OQ]`/`[PURITY?]`/`[BIZ]` 标注。

## 输出位置

- **behaviorspec**：目标 repo 的 `docs/specs/<capability>/spec.md`（与 techspec、提案同在 docs/，随代码同仓提交）。
- **cross-feature capability**（跨多个 feature 目录的共享行为）：放 host 更上层目录 + 各 feature 引用；判断不了归属的转人决定。
- **sprint contract**：与 spec 同目录 `docs/specs/<capability>/contract.md`。结构见 canon 产物结构：Behavioral（B* 1:1）+ Quality（Q*）+ Schema Changes（契约级）+ Follow-ups + Pass Rule，不重复 spec 正文、不含 AC 对照表。
- **附件**：同基名 `.follow-ups.md`（未完成非关键项，`FU-` 随机 ID，空时删文件）。

spec 是项目级交付物，放产品 repo，不放知识库。

## 相关资料

| 文件 | 何时读 |
|---|---|
| `references/canon.md` | 起草、自检时：正文结构、增量三态、三层密度、可交付清单、语言约束 |
| `references/evaluator-prompt.md` | spawn Evaluator 时：输入包、评估维度、verdict 格式、降级 coverage、轮次 |

## 相关 skill

- 从零探索一个 feature：brainstorming
- 高层地基：techspec
- Mermaid 语法：mermaid-diagrams
- 安全/合规审计：security-reviewer
- 语言自然度：humanizer

引用的 skill 不在当前环境时的兜底：humanizer 缺失就按上面语言约束自查一遍 AI 味；brainstorming、mermaid-diagrams、security-reviewer 缺失就跳过，在交付说明里注明哪步没做。
