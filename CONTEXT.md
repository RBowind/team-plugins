# team-plugins（born-team 插件库）

团队的 Claude Code 插件库：把规范、动作、角色定义打成插件组件，随 git 分发。本文件是术语表，只放概念定义，不放实现细节。

## Language

**behaviorspec（spec）**:
复杂 feature 的黑盒行为契约，按 capability 组织，只写可观测的 WHEN/AND/THEN。
_Avoid_: 行为规格、SDD spec

**sprint contract**:
人 gate 通过后从 spec 抽取的交付 checklist：Behavioral（B*）+ Quality（Q*）+ Schema Changes + Pass Rule。放 feature 目录 `specs/<capability>/contract.md`；Status 只有 DRAFT（生成态）与 APPROVED（人放行态）两值，非 APPROVED 不构成 devloop 启动授权。
_Avoid_: 任务清单、todo

**feature 目录**:
目标 repo 中一个 capability 的规格目录 `specs/<capability>/`，spec.md 与 contract.md 共置。

**B 编号**:
contract 中与 spec Scenario 1:1 的行为条目，测试与验收的最小单位。
_Avoid_: case id、AC

**回链**:
测试用例指向 B 编号的注释锚点（`// spec: B1`），无回链的用例视为游离用例。
_Avoid_: 溯源标记

**devloop**:
以 sprint contract 为输入、按 B 编号逐条"测试先行→独立评审→实现转绿"的交付循环。
_Avoid_: 自动开发、agent 流水线

**TestWriter**:
devloop 中只负责按 test-standards 把 B 编号写成失败测试的角色，不写业务代码。

**TestReviewer**:
devloop 中独立评审测试的角色：对照 spec 与 test-standards 打回或放行，有权要求重跑。
_Avoid_: 自评（写测试者不得自审）

**Implementer**:
devloop 中只负责把业务代码写到全绿的角色，不碰测试、不改 spec。

**Evaluator**:
sddspec 阶段的 spec 自检 subagent（区别于 devloop 的 TestReviewer，两者审的对象不同）。

**提测 gate**:
test-ready 命令，开发完成后的出口人工检查，与 devloop 互不重叠。
_Avoid_: /tice（旧名）

**命令调用名**:
文档与对话中写安装态全名 `/team-standards:<命令名>`（如 `/team-standards:devloop`、`/team-standards:test-ready`）；插件内文件名保持裸名。
