---
description: 后端 Go 的规格驱动交付循环。读取已批准的 behaviorspec 和 sprint contract，逐项执行“失败测试、独立评审、实现转绿”，最后完成质量检查和本地验证。
argument-hint: <capability> [repo路径]
---

# devloop

根据 `$ARGUMENTS` 执行 Spec-Driven Development（规格驱动开发，SDD）交付循环。

本命令只处理后端 Go。目标 repo 必须有 `go.mod`。如果一个 feature 同时包含前端和后端，只处理 contract 中属于后端 Go 的行为；其他部分交回宿主项目自己的开发流程。

你是主 agent，只负责调度、运行验证和记录进度：

- `team-standards:test-writer` 写测试
- `team-standards:test-reviewer` 独立评审测试
- `team-standards:implementer` 写实现

必须使用完整的 agent 名称。任一 agent 不存在时立即停止，说明插件安装不完整，不要用通用 subagent 顶替。

你不直接写测试或业务代码，不修改 spec，也不替用户批准 contract。你可以更新 contract 的完成状态和执行证据。

以下事情必须由用户决定：未定方案、异常处理、push、开 Pull Request（拉取请求，PR）、合并和部署。

## 1. 启动

1. 确定目标 repo。参数带路径时直接使用；否则从当前工作区查找。找不到就问用户。
2. 确认 repo 根目录存在 `go.mod`。不存在就停止，说明本命令只支持后端 Go。
3. 在 repo 内定位该 capability 的 spec 目录。sddspec 约定 spec 与 feature 代码同目录存放，但目录名不固定（如 `specs/<capability>/`、`spec/features/<capability>/`），文件名也可能带前缀（如 `<name>-spec.md`、`<name>-contract.md`）。按 capability 名搜索定位；找不到或有多个命中时问用户，不要猜。contract 必须存在；spec 通常存在，只有 contract 中剩余行为全部标为 REMOVED、整个 capability 已删除时才允许不存在。
4. contract 头部必须含 `Status: APPROVED`（规范头部为 `# Sprint Contract`、`Source:`、`Status:` 三行，不卡首行）。contract 缺失或状态未批准时停止，提示用户先完成 sddspec 和人工评审。不要创建 contract，也不要自行改状态。
5. 读取 repo 的 `AGENTS.md`、`CLAUDE.md`、README 和测试脚本，确定：
   - 当前行为的测试命令
   - 全量集成测试命令
   - 受影响包的 `go test` 命令
   - 格式化命令
   - lint 命令
   - 测试环境和测试数据库的启动方式；不需要数据库时记为 `N/A`
6. 命令或环境不明确时问用户，不要自创。
7. 读取 contract，只处理 Behavioral Changes 区域中未勾选、且属于后端 Go 的行为。每项必须标为 ADDED、MODIFIED 或 REMOVED；已勾选项直接跳过。前后端范围分不清时先问用户。contract 复选框是唯一进度记录，不另建状态文件。
8. 如果剩余工作明显无法在一个会话内完成，先建议用户拆小 contract。用户确认继续后再执行。

## 2. 准备 schema

contract 没有 Schema Changes 时跳过。

有 schema 变更时，调用 `team-standards:implementer`，并明确 `MODE: SCHEMA`。传入 Schema Changes 原文、repo 绝对路径、迁移命令和测试环境连接方式。

implementer 返回 `STATUS: GREEN` 后，你再运行一条仓库已有的集成测试，确认迁移已生效，测试环境可以连接。返回 `BLOCKED` 或验证失败时停止。

## 3. 逐项实现行为

按 contract 顺序串行处理。当前行为没有完成，不开始下一项。

### 3.1 写失败测试

调用 `team-standards:test-writer`，明确 `MODE: BEHAVIOR`，传入：

- contract.md 的绝对路径，以及存在时的 spec.md 绝对路径；整个 capability 已移除时 spec 写 `N/A`
- 当前行为编号、变更分类和条目原文
- repo 绝对路径
- 当前行为的测试命令
- 测试环境连接方式

处理返回状态：

- `RED` 或 `ALREADY_IMPLEMENTED`：进入独立评审，由 reviewer 确认断言和实际结果
- `BLOCKED`：按“卡住时怎么处理”停止

编译错误、环境错误、fixture 错误或没有匹配到测试，都不算有效红灯。

### 3.2 独立评审测试

调用新的 `team-standards:test-reviewer` 实例，明确 `MODE: BEHAVIOR`，传入：

- 本轮测试文件
- contract.md，以及存在时的 spec.md；整个 capability 已移除时 spec 写 `N/A`
- 本插件 `skills/team-test-standards-backend/SKILL.md` 的绝对路径
- repo 绝对路径
- 当前行为编号和变更分类
- 当前行为的测试命令
- 测试环境连接方式

reviewer 必须自己运行测试。处理 verdict：

- `PASS`：进入实现
- `FAIL`：把完整 verdict 和执行证据交回 test-writer；test-writer 只修 Gaps 中列出的测试问题
- `ALREADY_IMPLEMENTED`：你亲自重跑后停止，请用户核对 contract
- `BLOCKED`：先处理环境问题；无法处理就停止

每次返工后都调用新的 reviewer。最多评审两轮；仍未通过就停止。

### 3.3 实现到测试通过

评审通过后，调用 `team-standards:implementer`，明确 `MODE: BEHAVIOR`，传入：

- 当前行为编号、变更分类和测试文件
- contract.md、存在时的 spec.md，以及存在时的 design.md
- repo 绝对路径
- 当前行为的测试命令
- 测试环境连接方式

implementer 不得修改测试、spec 或 contract。每轮结束后，由你重跑当前行为的测试。最多三轮；仍未通过就停止。

implementer 如果报告测试可能有错，把证据交回 test-writer，并重新走独立评审。不要让 implementer 自己改测试。

### 3.4 跑回归测试

当前行为通过后，运行全量集成测试。

如果全量测试通常超过五分钟，可以在循环中只跑当前行为和受影响包，全部行为完成后再跑一次全量测试。采用此方式时，把原因写进 contract。

### 3.5 更新 contract

只有当前行为测试和回归测试都通过，才能勾选对应复选框，并记录：

`测试驱动开发（Test-Driven Development，TDD）红绿证据：<命令和关键输出> | 受影响包：<测试结果>`

已经有 commit 时补上 commit 哈希。未通过或仍在返工的行为不能勾选。

每完成一项，向用户报告一行进度和测试结果。

## 4. 收尾

### 4.1 变异测试

只有仓库已经配置变异测试，或用户明确要求时才运行。使用项目现有命令，只覆盖本次改动的包。不要自行安装工具。

变异测试由主 agent 统一执行，test-writer 和 test-reviewer 都不自己跑。工具在 Windows 原生跑不起来时（如 go-mutesting 编译失败），把 repo 的 Windows 路径换算成 `/mnt/<盘>/...` 转在 WSL 里跑，输出全文留存，并记下这个限制。

检查变异分数和存活清单，不能只看退出码；存在存活变异体时退出码仍是 0。有存活变异体时：

1. 调用 test-writer，明确 `MODE: MUTATION`，传入存活变异体 diff、允许改动的测试文件、contract.md、存在时的 spec.md、测试命令和 repo 路径。
2. 调用新的 test-reviewer，明确 `MODE: MUTATION`，只评审本轮增量测试。
3. 由你重跑全量测试和变异测试。

最多两轮。仍存活的变异体，以及等价变异、不可达分支等候选理由，都交给用户确认。未经确认，不写成最终结论。

### 4.2 检查 Quality 条目

调用 test-reviewer，明确 `MODE: QUALITY`，传入 contract 中每条 Quality 原文、存在时的 spec、相关测试文件、repo 路径和需要执行的验证命令。

reviewer 对每条给出“已满足”“未满足”或“需用户确认”。未满足且属于当前实现范围的，交给 implementer 修复后重审；其他项加入待处理清单。

### 4.3 跑最终验证

逐条核对 Pass Rule，并运行：

- 受影响包的 `go test`；改动跨多个包时覆盖全部受影响包
- 全量集成测试
- 仓库规定的格式化命令
- `golangci-lint run` 或仓库规定的等价命令
- README 或持续集成（Continuous Integration，CI）规定的其他必跑项

使用仓库已有命令。任何一项没跑或失败，都要在总结中写明。

### 4.4 输出总结

总结包括：

- 每个行为的状态和测试证据
- 变异测试结果；跳过时写明原因
- 每个 Quality 条目的结论
- Pass Rule 和本地检查结果
- 仍需用户处理的事项

全部通过且没有待处理事项时，写“本地交付已完成”，并提示用户可以跑 `/team-standards:test-ready` 提测。是否 push、开 PR 或提测，由用户决定；提测 gate 是出口人工检查，本命令只提示，不代跑。

## 5. 卡住时怎么处理

出现以下任一情况，立即停止当前循环：

- reviewer 两轮后仍不通过
- implementer 三轮后测试仍不通过
- schema 或测试环境无法使用
- spec、contract、实现或外部契约互相冲突
- 涉及资金、安全或其他高风险决策，现有材料不足

报告三部分：

1. 卡在哪个行为、哪一步。
2. reviewer verdict、测试输出等直接证据。
3. 两个可选处理方向，各写一句依据，等用户决定。

不要猜答案，也不要继续处理后面的行为。

## 6. 不改 spec

主 agent、test-writer、test-reviewer 和 implementer 都不得修改 spec.md，也不得改写 contract 中已有行为的判定条件。

如果 spec 与现实不符，停止循环，回到 sddspec 原位修正 live spec，并更新 contract 中的变更分类、依据和迁移信息。删除行为直接从 spec 移除，不保留旧编号或勘误墓碑；历史由 Git 和 contract 保留。spec 与 contract 重新批准前，devloop 保持阻塞。
