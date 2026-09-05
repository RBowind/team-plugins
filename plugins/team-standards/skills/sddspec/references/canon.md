# sddspec canon

## 核心原则：黑盒契约

behaviorspec 只描述可观测边界行为——什么进、什么出、什么副作用从外面可见。不写实现细节。

litmus test（判定一条该不该写）：每条语句问"如果团队换一种语言、框架或基础设施重写这个服务，这条还成立吗？"

- 成立 → 边界行为，留 spec。
- 不成立 → 实现细节，移 design.md。

## spec 纯度

spec.md 是 AI 开发期间的 target——贯穿实现过程的对齐锚点。它只放行为契约（Requirement/Scenario）+ Coverage Gaps。其他内容各有去处：

- Schema Changes → contract.md
- 实现细节 → design.md
- 未决非关键项 → follow-ups 附件

AI 实现时出现分歧，一律回到 spec 对轴。

## 产物结构

spec.md 只放行为契约。schema 变更归 contract.md，不写进 spec。

```markdown
# <Capability Name>
> <一句话：干什么，给谁，为什么>

## Elaborates
- techspec: <pointer to docs/tech-specs/...>

## ADDED Requirements      # 或 MODIFIED / REMOVED
### Requirement: <动词短语描述系统能力>
The system SHALL <一句话行为>

#### Scenario: <自然语言描述>
- **WHEN** <触发器: API 请求 / 定时 Job / Kafka 事件>
- **AND** <前置条件: DB/system 状态>
- **THEN** <可观测变化 1>
- **AND** <可观测变化 2>

#### Scenario: <失败场景>
- **WHEN** <外部调用失败/非法状态>
- **THEN** <可观测的失败处理>

## Coverage Gaps          # 未定行为，只列已知 gap，不编造
```

contract.md（交付 checklist）从 spec 抽取，不重复 spec 正文：

```markdown
# Sprint Contract: <capability>
Source: <spec.md 相对路径>
Status: DRAFT    # 生成即 DRAFT；人评审放行后手改 APPROVED（devloop 只认 APPROVED）

## Behavioral（from spec scenarios）   # B* 与 scenario 1:1
- [ ] B1: <scenario 一句话> — verified by BDD test

## Quality                            # Q* 通用质量
- [ ] Q1: ...

## Schema Changes                     # 契约级，不含索引/迁移
### table_name
- `column` TYPE NOT NULL DEFAULT - 用途

## Follow-ups                         # 未决项指针，空时删节

## Pass Rule                          # ALL B* 断言全过 + ALL Q* + lint/test
```

## 三层信息密度（同一结构服务三读者）

| 层 | 内容 | 谁读 |
|---|---|---|
| Requirement title + description | WHAT/WHY | 人 quick scan |
| Scenario WHEN/AND | 触发器 + 前置 | AI test setup + Evaluator |
| Scenario THEN | 可观测变化 | AI assertions + Evaluator |

## 增量三态

`ADDED` / `MODIFIED` / `REMOVED` 只标 Requirements。Schema Changes 归 contract.md。brownfield 改动多为 MODIFIED/REMOVED，不止 ADDED。

## 该写（可观测边界）

1. **触发器**：三种入口——API 请求 / 定时 Job / 事件消费（如 Kafka 消息）。每个 scenario 第一个 WHEN 必是触发器，不是条件。"系统条件"（如"asset queueable AND today >= IPO date"）是前置，不是触发器。
2. **前置**：DB/system 必须存在的状态，告诉 AI test setup 准备什么数据、mock 什么。
3. **可观测变化**：DB 表+字段变迁（命名表和区分字段）、外部 API 调用带关键入参（命名 service+operation）、Event/Job 产出、API Response 含错误码、通知、业务规则公式（如 `hold_amount = EUR_amount × 1.03`）。
4. **失败场景**：一等公民，不是附注。外部调用失败、非法状态、非法输入都要有 scenario。
5. **幂等/去重**：如适用（如重复事件）。
6. **Schema Changes**：写进 contract.md，不写进 spec——契约级：列名、类型、约束。索引策略、迁移细节进 design.md。

## 不该写（实现细节 → design.md）

| 类别 | 错（实现细节） | 对（边界行为） |
|---|---|---|
| 并发 | "获取分布式锁 (userID + orderID)" | "同一 order 并发只有一个执行能进行" |
| 批处理 | "以 50 一批派发异步任务" | "处理该 IPO 的所有 pending order" |
| 重试 | "指数退避重试，最多 5 次" | "重试直到外部调用成功" |
| 内部命名 | "[ProcessStatusTransitions]" | 描述条件，不描述函数 |
| 数据结构 | "存 map[string]Order" | 描述 DB 状态变化 |
| 缓存 | "缓存汇率 5 分钟" | 描述何时取新汇率 |

## Elaborates

spec 头部 `## Elaborates` 指向 techspec（`docs/tech-specs/...`）。作用：分层追溯（这份 spec 在哪份地基上展开）+ coverage 对齐基准（Evaluator 用 techspec 当准基准对 coverage）。

## 语言约束

- 业务描述中文，结构 keyword 英文（`SHALL`/`WHEN`/`AND`/`THEN`/`Requirement`/`Scenario`/`ADDED`/`MODIFIED`/`REMOVED`）——Evaluator 机器识别 + 业界通用。
- 自然工程语言，不用自造术语。
- 不用 AI 套话词：赋能、抓手、闭环、范式、链路、打通、底座、全链路、一站式、沉淀。
- 缩写首次出现展开全称 + 解释。
- 术语用行业习惯说法。
- 生成后跑 humanizer 复核去 AI 味。

## 可交付自检清单

- 每个 Requirement 至少一个 Scenario。
- 失败场景是一等公民，不是附注。
- WHEN 是触发器（API 请求 / 定时 Job / 事件消费），不是条件。
- AND before THEN 是前置，THEN 是可观测变化。
- 用 `SHALL`/`MUST`，不用 should/may。
- 增量三态标记（ADDED/MODIFIED/REMOVED）。
- Schema Changes 不在 spec（归 contract.md）；索引/迁移进 design.md。
- `## Elaborates` 指向 techspec。
- 无实现细节泄漏（过 litmus test）。
- 语言自然度：无 AI 套话、无自造词；缩写首次出现就展开全称（description 标题下首次出现也要展开，不只 scenario；scenario 里当 DB enum 值用的字面标识符不算）。
- 未定义行为显式标 coverage gap，不编造。
