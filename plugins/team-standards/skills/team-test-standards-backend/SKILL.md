---
name: team-test-standards-backend
description: 团队后端测试与 review 规范（Go）。写后端测试、补用例、自查或 review 后端代码改动时使用，让 AI 写出的测试对齐团队口径。含 test guide：BDD 分层、sprint contract 行为回链、集成测试四层断言清单、真实数据库断言、可选 mutation testing 验收；覆盖 ADDED/MODIFIED/REMOVED 三类变更。前端测试用 team-test-standards-frontend。
---

# 团队后端测试与 review 规范（Go）

## 测试怎么写

- 新功能和 bug 修复必须带测试，测试跟代码同一个 PR 提交。
- 前端改动另见 team-test-standards-frontend；本文件只覆盖后端 Go。
- 一个用例只断言一件事，用例名直接说清场景和预期，例：`拒绝过期 token 返回 401`，不写 `test1`。
- 不许 mock 掉被测对象本身，也不许 mock 数据库；只有外部服务（第三方 HTTP 等）可以 mock。
- bug 修复先写复现测试再改代码，测试红了改，绿了才算修完。
- 财务相关逻辑（金额、账本、退款）：断言落库状态，不验 mock 调用次数。

## 后端 Go test guide

本节指导 AI 为后端 Go 系统编写测试文件。与项目已有测试基建冲突时，以项目基建为准，并在改动说明里标出冲突点。

### 测试分层

| 层 | 位置 | 框架 | 写什么 |
|---|---|---|---|
| 单元测试 | 与被测包同置（`internal/**/*_test.go`） | 标准 `testing` 包 + testify | 纯逻辑：计算、解析、转换 |
| 集成测试 | 项目的集成测试目录（如 `apps/<app>/test/<domain>/` 或 `tests/integration/`，以项目现状为准） | 推荐 Ginkgo v2 + Gomega（BDD 是核心，框架可降级） | 行为级验证，主力层 |

BDD 是核心，Ginkgo 是推荐框架：

- 项目已有 ginkgo 基建 → 用 ginkgo 写，沿用项目现有的套件入口和 helper。
- 项目没有 ginkgo 基建 → 不引入新框架，用标准库表驱动 + 真实数据库写行为级测试，同样遵守下文四层断言清单。
- 包内单测继续用标准库，不做存量迁移。

### 从 spec 和 contract 出发

1. 先读 sddspec 产出的 behaviorspec 和 feature 目录下的 sprint contract。spec 路径跟随项目现有约定；整个 capability 已移除时允许 spec 不存在，但 contract 必须明确标为 REMOVED。
2. contract 的每个 Behavioral Changes 条目必须落到恰好一个测试用例：Ginkgo 用一个 `It`，标准库用一个 `t.Run`。ADDED/MODIFIED 的预期来自当前 spec Scenario；REMOVED 的预期来自 contract 中的旧行为和移除后结果。
3. 每个用例上方写回链注释：`// contract: B1`。contract 改了，测试跟着改；不允许出现无回链的游离用例。
4. REMOVED 条目的 Reason/Migration 只有在描述可观测兼容行为时才进入断言；纯实施说明不进入测试。
5. 使用 Ginkgo 时，已分析并确认不适用的场景用 `PIt("N/A: <原因>")` 留痕；使用标准库时用 `t.Skip("N/A: <原因>")`。

### BDD 写法

spec/contract 结构到 ginkgo 的映射：`Describe` = capability（API 场景用 `METHOD /path [变体]`），`Context` = 前置条件，`It` = 一条 Behavioral Changes 的触发与预期结果。

```go
func TestOrder(t *testing.T) {
    RegisterFailHandler(Fail)
    RunSpecs(t, "Order Suite")
}

var _ = BeforeSuite(func() {
    // 顶层唯一位置：起测试容器、装配被测服务
})

var _ = Describe("POST /api/v1/orders [限价买入]", func() {
    Context("库存充足且用户已登录", func() { // AND 前置
        // contract: B1
        It("提交订单成功，库存扣减并写入订单表", func() {
            // WHEN 触发动作 → THEN 断言可观测变化
        })
    })
})
```

规则：

- `It` 名是一句中文，说清"什么前提下做什么发生什么"，直接对应 contract 条目及其目标 spec scenario（如有）的措辞。
- `BeforeSuite` 只能放顶层；`BeforeAll` 只能放 `Ordered` 容器内。
- 只跑子集时用 `-ginkgo.focus="keyword"`，或项目已有的 label 过滤；ginkgo 参数必须放在包路径之后。
- label/focus 筛不到任何用例时默认假绿；要暴露就加 `-ginkgo.fail-on-empty`。
- ginkgo 用例和标准库用例共存无冲突，`-run TestXxx` 可单独跑标准库用例。

### 集成测试断言清单

每条目标 scenario 或 REMOVED 行为按顺序覆盖四层断言，缺哪层就在注释里说明原因：

1. **端到端响应**：请求走真实路由打到 API，断言状态码和响应体关键字段。
2. **参数 edge case**：每个入参单独覆盖——零值、空字符串、边界值（最小、最大、±1）、null、非法格式、超长。spec 里的失败场景必须逐条有对应用例，不许只测 happy path。
3. **外部服务调用参数**：捕获 mock 收到的请求，逐字段断言（模板见下）。
4. **数据库字段变动**：写操作后直接查表，断言具体字段的值，不只信写方法的返回值。

### 外部服务 mock 模板

集成测试优先用项目已有 mock 设施（如 ghttp、helper 封装的 WebMock）；没有时用标准库：

```go
var captured *http.Request
var capturedBody []byte
mock := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    captured = r
    capturedBody, _ = io.ReadAll(r.Body)
    w.WriteHeader(http.StatusOK)
    w.Write([]byte(`{"ok":true}`))
}))
defer mock.Close()

// 把 mock.URL 注入被测服务的客户端配置，执行业务调用后断言：
Expect(captured.URL.Path).To(Equal("/v1/charge"))
Expect(captured.Header.Get("Authorization")).To(Equal("Bearer test-key"))
var payload ChargePayload
Expect(json.Unmarshal(capturedBody, &payload)).To(Succeed())
Expect(payload.Amount).To(Equal(100))
```

单元测试 mock 外部依赖用项目生成的 mock（如 gomock）。gomock 纪律：

- `gomock.Any()` 只许用在 context 参数上，业务参数给具体值。
- 每条 expectation 必须写 `.Times(n)`。

### 数据库断言

- 集成测试连真实数据库：项目已有机制优先（dockertest 一次性容器、`TEST_DATABASE_URL`、公司公共测试库），不 mock 数据库。
- 断言到具体字段，包括状态字段、金额、时间戳、关联记录条数。用项目现有的查询方式（sqlc、ORM、原生 SQL 均可）：

```go
var order Order
Expect(db.Where("order_no = ?", orderNo).First(&order).Error).To(Succeed())
Expect(order.Status).To(Equal("paid"))
Expect(order.AmountCents).To(Equal(int64(9900)))
```

### Mutation testing（可选验收，非门禁）

变异测试验证测试能否抓到实现偏差。只有项目已经配置变异测试，或用户明确要求时才运行；agent 不自行安装工具。

- 使用仓库已有命令，只跑本次改动的包。
- 不能只看退出码，必须读取 mutation score 和存活变异体清单。有些工具在存在存活变异体时仍返回 0。
- 改动说明附上 mutation score 和存活清单。每个存活变异体要么补测试杀掉，要么给出等价变异、不可达分支等候选理由，交给用户确认。

## 提交前自查（AI 每次改完代码过一遍）

1. 测试跑过且全绿，命令以项目 README 里写的为准。改动影响多个包时，本地跑全受影响的包，不只跑直接改动的那个——本地验证要与 CI 等价。
2. 改动没有越出任务声明的文件范围；越界了就停下来说明。
3. 新增依赖、环境变量、配置项，在改动说明里单列出来。
4. 接口改动（参数、返回、错误码）在改动说明里标"接口变更"，reviewer 重点看。
5. 新写的测试已按 sprint contract 行为编号回链；启用了 mutation testing 的项目，集成测试结果一并附在改动说明里。

## review 口径（人 review AI 改动时按这个查）

- 先看测试有没有真的覆盖改动，再看实现。
- AI 自己说"已完成"不算数，以测试和运行结果为准。
- 涉及金额、权限、删除数据的代码，必须人工逐行看，AI 不能自己合入。
- 测试 review 对照 spec 和 contract 查：行为项是否全覆盖、断言是否落到具体值、有没有游离用例。
