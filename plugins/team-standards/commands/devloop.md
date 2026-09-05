---
description: SDD 交付循环：输入 sddspec 的 behaviorspec + 人已放行的 sprint contract，逐条 B"写失败测试→独立评审→实现转绿"，收尾跑 mutation testing 和 Q* 自查，全绿后提示 /team-standards:test-ready 提测。仅后端 Go。
argument-hint: <capability> [repo路径]
---

# devloop

对 $ARGUMENTS 执行 devloop 交付循环。

范围限制：v1 只支持后端 Go。本 feature 若含前端改动，前端部分不进循环，仍走手工开发 + /team-standards:test-ready。

你的角色：主 agent，只做编排——spawn subagent、读它们的输出、跑测试、判红绿灯、勾 contract。你不写测试代码、不写业务代码、不改 spec、不替人放行。

三个执行角色由本插件 agents/ 提供，spawn 时用带命名空间的名称：`team-standards:test-writer`、`team-standards:test-reviewer`、`team-standards:implementer`。spawn 找不到 agent 说明插件 agents 未安装，停下报告，不要改用通用 subagent 顶替。提测 gate（/team-standards:test-ready）是出口人工检查，循环只在收尾时提示跑它，不代跑。

## 1. 启动检查

1. **解析 repo 路径**：参数里给了 repo 路径就直接用；没给就按 sddspec 的规则读 `repo-paths.local.yaml` 解析目标 repo。没有这个文件，先问用户要路径。
2. **确认硬前提**，缺任一项拒绝启动，提示先跑 sddspec：
   - 目标 repo 存在 `specs/<capability>/spec.md`；
   - `specs/<capability>/contract.md`（sprint contract）存在，且首行 `Status: APPROVED`。sddspec 生成 contract 即 DRAFT，人评审放行后手改 APPROVED；非 APPROVED 一律视为未放行。
   你不生成 contract、不替人放行、不把"找不到 contract"当成"contract 已放行"。
3. **确认测试命令**：以项目 README 记录为准，启动时向用户确认一次。README 没记录就停下来问（与 /team-standards:test-ready 口径一致）。
4. **读 contract**：列出 Behavioral（B*）里所有未勾项，本循环只做这些；已勾的是已完成，直接跳过。contract 复选框是唯一进度状态：断点续跑就是重跑 /team-standards:devloop，从第一个未勾项继续；不新建任何进度文件。

## 2. Schema 阶段

进 B 循环之前，落 contract 的 Schema Changes：spawn implementer 写迁移/DDL，准备测试库环境（`TEST_DATABASE_URL` 或一次性 PostgreSQL 容器）。传入：contract 的 Schema Changes 条目原文、repo 绝对路径、测试库连接方式。等它报 `STATUS: DONE`，你再亲跑一条项目已有的集成测试，确认报错不是连库失败。这一步完成才进第 3 节——没有 schema 就没有可跑的集成测试。落不了 → 第 5 节。

## 3. 逐条 B 循环（按 B 编号串行）

每条 B 走一遍下面 6 步，全部 B 绿后进第 4 节；任何一步卡住 → 第 5 节。

1. **spawn `team-standards:test-writer` 写这条 B 的失败测试**。传入：spec.md 路径（含对应 Scenario）、contract.md 路径与该 B 条目原文、repo 绝对路径、测试命令、测试库连接方式（第 2 节确定的 `TEST_DATABASE_URL` 或容器起法）。它按 team-test-standards-backend 执行：`It` 上方回链注释 `// spec: Bn`、四层断言（端到端响应、参数 edge case、外部服务调用参数、数据库字段变动）、缺哪层写理由注释。
2. **spawn `team-standards:test-reviewer` 评审**。传入路径：本轮测试文件、spec.md、contract.md、本插件 `skills/team-test-standards-backend/SKILL.md` 的绝对路径（你从插件安装目录解析，不让 reviewer 自己翻找）；执行参数：repo 绝对路径、B 编号、第 1.3 步确认的测试命令。独立评审，不采信作者自述；最多 2 轮，每轮重新 spawn 一个新实例。口径必须包含：实际执行测试，确认它是红的，且红因是"该 B 行为未实现"。编译错误、连不上库、fixture 崩这类红得不对的，直接打回。
3. **处理 verdict**：打回 → 把 verdict（Gaps + 执行证据）交给 test-writer 返工，Gaps 是本轮唯一修改范围，改完再进第 2 轮评审；2 轮仍打回 → 第 5 节。
4. **放行后 spawn `team-standards:implementer` 写业务代码到绿**。传入：B 编号与测试文件路径、spec.md 路径、contract.md 路径、design.md（若有）、测试命令、repo 绝对路径、测试库连接方式、本轮范围（默认只跑该 B 用例到绿；全量由你第 5 步跑）。implementer 不碰测试文件、不改 spec。红绿灯循环最多 3 轮（每轮 = implementer 改代码 + 你重跑该 B 测试）；3 轮不绿 → 第 5 节。
5. **跑全量集成 suite**：这条 B 绿后，按第 1.3 步确认过的命令跑全量集成测试，防止后条 B 打碎前面已完成的 B。仅当项目 suite 超过 5 分钟才降级：循环中只跑当前 B 的测试——降级时派活给 implementer 要明确写"本轮只跑 Bn"，全部 B 转绿后补跑一次全量兜底，并把降级原因记进 contract。
6. **勾 contract + 输出进度**：全绿才勾 `- [ ] Bn` 复选框，勾时在 contract 该条旁附一行证据（测试命令 + 结果）。打回的、没转绿的，一律不勾。同时向用户输出一行进度，例：`B3 ✓ 集成 14/14 绿`。

## 4. 收尾

1. **跑一次 mutation testing**：go-mutesting，只能在 WSL 里跑（Windows 原生编译失败），只跑本次改动的包。做法：把目标 repo 的 Windows 路径换算成 `/mnt/<盘>/...`，执行 `wsl -e bash -lc "cd <mnt路径> && go install github.com/zimmski/go-mutesting/cmd/go-mutesting@latest && go-mutesting ./internal/<改动包>/..."`，输出全文留存。有存活变异体时退出码仍是 0——必须读 mutation score 和存活清单，不能只看命令成败。
2. **补杀**：存活变异体 → spawn test-writer 补测试杀掉（传入存活清单每条的 diff、补杀范围、全量 suite 命令、repo 绝对路径）→ 以增量模式 spawn test-reviewer 只审增量 diff（另传本轮补测的改动文件列表）→ 你重跑全量 suite 和 go-mutesting。go-mutesting 由你统一执行，test-writer 和 test-reviewer 都不自己跑。最多 2 轮。
3. **存活转人**：2 轮后仍存活的、以及 TestWriter 在补杀交付里判为等价变异/不可达分支并附依据的存活项，一并列清单转人裁决。理由经人确认或改写后才写进 contract 与提测说明——agent 的候选理由不充当最终结论。
4. **Q* 自查**：以 Q* 自查模式 spawn test-reviewer，传入 contract 的 Q* 条目原文 + 相关测试与 spec 材料路径，逐条给结论，三种：已满足 / 未满足 / 需人确认。未满足且属实现范围的 → 派 implementer 修（计入红绿灯 3 轮预算）后重过本步；需人确认与不可自动修的 → 进第 5 节转人清单。
5. **Pass Rule 核对**：按 contract 的 Pass Rule 逐条核对（含 lint），结论写进总结报告。
6. **总结报告**：每条 B 的状态与证据、mutation score 与存活处理情况、Q* 结论、Pass Rule 核对结果、转人清单。只有无转人残留且 Pass Rule 逐条满足时，最后一句才是：全部收敛，可以跑 /team-standards:test-ready 提测；否则列出未裁决与未满足项，不写收敛结论。

## 5. 卡点转人

触发条件：test-reviewer 2 轮打回不收敛、红绿灯 3 轮不绿、schema 落不了、怀疑 spec 本身写错。

转人时停止循环，报告三件事：

1. 卡在哪：哪条 B、哪一步；
2. 证据：test-reviewer 的 verdict、测试输出原文；
3. 两种候选解决方向：各一句话，用户拍板，你不代拍。

## 6. spec 免疫

任何 agent（主 agent、test-writer、test-reviewer、implementer）永不修改 spec.md。循环中发现 spec 与实现或现实冲突：停止转人，回 sddspec 流程处理。devloop 内不修 spec，也不写绕开 spec 的实现。
