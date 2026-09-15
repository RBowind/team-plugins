---
name: sddspec
description: 适用于"写 behaviorspec""从 PRD+techspec 生成行为契约 spec""自检 spec""review behaviorspec"等请求；输入是 PRD + techspec（复杂 feature），输出中文黑盒行为契约 spec + 交付 contract。spec 只放行为契约，是 AI 开发期间的 target；schema 变更归 contract。不处理实现代码、安全审计或执行；简单 feature（单 Jira 小改）不走；没 PRD/techspec 或需先探索方案时改用 brainstorming。
---

# sddspec

sddspec 给复杂 feature 从 PRD + techspec 生成黑盒行为契约 spec（behaviorspec），驱动 AI 写 test/code。它只写可观测边界行为（WHEN 触发 / AND 前置 / THEN 可观测变化），实现细节归到 design.md。spec.md 是始终描述目标系统当前行为的 live doc，不是变更日志。

正文中文，自然工程语言。不用本 skill 自造术语，不在正文留 Open Question、TODO、假设说明（需人决策的点生成时当场拍掉，定不了进 follow-ups 附件）。

## 定位与分层

四层，各管各的，不重叠：

- **techspec（地基）**：高层工程指导，DB 关系、大体流程、架构决策、成功标准。一个 feature 一份。
- **behaviorspec（本 skill 产出）**：黑盒行为契约，按 capability 拆，放 feature 代码目录的 spec 目录（目录名跟随宿主 repo 既有约定，如 `spec/features/<capability>/`；无约定时新建 `specs/<capability>/`）。实现细节归到 design.md。
- **wiki（知识库，可选）**：durable 的 domain knowledge（状态机、契约、cross-repo flow、ADR）。宿主仓库有知识库时，behaviorspec 的 durable 部分按 `../kb/SKILL.md` 归档进去；没有则留在 spec 原地。
- **sprint contract（本 skill 自动生成）**：交付 checklist，放 feature 目录。

## 输入与流程

1. **判断输入**：确认是复杂 feature（有 PRD + techspec），定位目标 repo（用户给路径就直接用，没给就按当前工作区或停下来问），读 PRD + techspec；已有 spec 时一并读取，作为本次更新的基线。简单 feature（单 Jira 小改）提示不走 sddspec。
2. **回读对齐**：5–10 行回读，说明理解的目标、主流程、实体、已知集成，请用户纠正，不当 approval gate。
3. **缺口处理 + 生成时交互**：起草中遇到需人决策的点，按"缺口处理"执行。
4. **起草 behaviorspec**：按 `references/canon.md` 把变更合并成目标状态（新增写入、修改原位更新、移除直接删除），使用三层信息密度和 Elaborates techspec pointer，中文。
5. **canon 自检**：按 canon 的可交付自检清单自检。
6. **Evaluator 自检**：按 `references/evaluator-prompt.md` spawn isolated subagent（subagent，不是 agent team），更新已有 spec 时同时提供修改前基线或本次 diff，max 2 轮。主 agent 读 verdict 后改，每轮重 spawn 保持干净，不让自己评自己。2 轮仍 FAIL → 报告 recurring gaps，暂停转人（可能 techspec 输入不足，不是 spec 写作问题）。
7. **人 gate（spec DoD）**：Evaluator PASS 后人审机器判不住的（purity 边界、业务正确性、scope、coverage 补 techspec 没覆盖的、Open Questions/follow-ups 残留）。人不审机器已自检的。
8. **sprint contract 生成**：人 gate 通过后，从本次 spec 差异生成 Behavioral Changes：新增/修改项对应目标 spec scenario，移除项直接记录旧行为及移除后的可观测结果；再补 Q*（通用质量）+ Schema Changes（起草中已梳理，落 contract 不进 spec）+ Follow-ups + Pass Rule。移除项可带 Reason/Migration，contract 不重复 spec 正文。PRD AC 覆盖由 Evaluator 把关（见 evaluator-prompt 降级 coverage），不单列双向对照表。contract 放 feature 目录。
9. **交付**：contract 和仍存在的 spec 交给下游 code 阶段实现。后端 Go 项目可运行 `/team-standards:devloop`；其他项目使用宿主仓库自己的开发流程。

读取本地 PRD/techspec 用 `Read`；读取 Confluence、Jira 等远程来源用对应工具。读不到来源时说明限制，不猜测原文内容。

## 缺口处理

起草中遇到需人决策的点（未定业务规则、purity 边界存疑、业务决策如系数），一次只问一个。

**关键决策**（阻塞生成的：缺了没法往下写）→ 暂停问人，当场拍掉的写正文（resolved，不留标注）。

**非关键**（不阻塞，如字段精度、错误码、非主流程失败分支、局部响应字段）→ 进 follow-ups 附件（`FU-` 随机 ID，不进正文），生成继续。

不要根据经验猜测潜在需求并创建 follow-up。用户或正文已排除的事项不写 follow-up。用户明确说"不用管"或永久不做时直接省略，不留记录。

正文始终是已 resolved 的干净行为契约，不留 `[OQ]`/`[PURITY?]`/`[BIZ]` 标注。

## 输出位置

- **behaviorspec**：目标 repo 的 feature 代码目录 spec 目录（和代码 co-located）。目录名跟随宿主 repo 既有约定（如 `spec/features/<capability>/`、`specs/<capability>/`）；无约定时新建 `specs/<capability>/`。整个 capability 被移除时删除对应 spec 文件。
- **cross-feature capability**（跨多个 feature 目录的共享行为）：放 host 更上层目录 + 各 feature 引用；判断不了归属的转人决定。
- **sprint contract**：feature 目录。结构见 canon 产物结构：Behavioral Changes（本次新增/修改/移除）+ Quality（Q*）+ Schema Changes（契约级）+ Follow-ups + Pass Rule，不重复 spec 正文、不含 AC 对照表。
- **附件**：同基名 `.follow-ups.md`（未完成非关键项，`FU-` 随机 ID，空时删文件）。

spec 是项目级交付物，放产品 repo，不放知识库。

## 相关资料

| 文件 | 何时读 |
|---|---|
| `references/canon.md` | 起草、自检时：live doc 结构、基线合并、三层密度、可交付清单、语言约束 |
| `references/evaluator-prompt.md` | spawn Evaluator 时：输入包、评估维度、verdict 格式、降级 coverage、轮次 |

## 相关 skill

- 从零探索一个 feature：brainstorming、grill-with-doc
- 高层地基：techspec
- 图示设计索引：`../tech-diagram-design/SKILL.md`；只在需要理解或重绘 techspec 图示时加载，不把视觉样式写入 behaviorspec
- Mermaid 语法：mermaid-diagrams
- 安全/合规审计：security-reviewer
- 语言自然度：humanizer

引用的 skill 不在当前环境时的兜底：humanizer 缺失就按 canon 的语言约定自查一遍 AI 味；brainstorming、grill-with-doc、mermaid-diagrams、security-reviewer 缺失就跳过，在交付说明里注明哪步没做。
