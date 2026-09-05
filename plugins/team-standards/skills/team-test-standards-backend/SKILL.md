---
name: team-test-standards-backend
description: 团队后端测试与 review 规范（Go）。写后端测试、补用例、自查或 review 后端代码改动时使用，让 AI 写出的测试对齐团队口径。含 test guide：BDD（ginkgo）、sddspec 对齐、集成测试断言清单、mutation testing 验收。前端测试用 team-test-standards-frontend。
---

# 团队后端测试与 review 规范（Go）

## 测试怎么写

- 新功能和 bug 修复必须带测试，测试跟代码同一个 PR 提交。
- 一个用例只断言一件事，用例名直接说清场景和预期，例：`拒绝过期 token 返回 401`，不写 `test1`。
- 不许 mock 掉被测对象本身，也不许 mock 数据库；只有外部服务（第三方 HTTP 等）可以 mock。
- bug 修复先写复现测试再改代码，测试红了改，绿了才算修完。

## 后端 Go test guide

本节指导 AI 为后端 Go 系统编写测试文件。与项目已有测试基建冲突时，以项目基建为准，并在改动说明里标出冲突点。

### 测试分层

| 层 | 位置 | 框架 | 写什么 |
|---|---|---|---|
| 单元测试 | 与被测包同置（`internal/**/*_test.go`） | 标准 `testing` 包 | 纯逻辑：计算、解析、转换 |
| 集成测试 | `tests/integration/` | Ginkgo v2 + Gomega | 行为级验证，主力层 |

只有集成测试层用 ginkgo；包内单测继续用标准库，不做存量迁移。

### 从 spec 出发

1. 先读 `specs/<capability>/spec.md` 和 feature 目录下的 sprint contract。找不到 spec 就先问这个测试对应哪个 capability，不凭空写。
2. spec 的 Scenario 和 contract 的 B 编号 1:1。每个 B 编号必须落到恰好一个 `It`，不多不少。
3. 每个 `It` 上方写回链注释：`// spec: B1`。spec 改了，测试跟着改；不允许出现无回链的游离用例。

### BDD 写法

spec 结构到 ginkgo 的映射：`Describe` = capability，`Context` = spec 的 AND 前置，`It` = 一条 Scenario 的 WHEN→THEN。

```go
func TestOrderIntegration(t *testing.T) {
    RegisterFailHandler(Fail)
    RunSpecs(t, "Order Integration Suite")
}

var _ = BeforeSuite(func() {
    // 顶层唯一位置：起 mock server、连真实数据库
})

var _ = Describe("Orders", Label("integration"), func() {
    Context("库存充足且用户已登录", func() { // AND 前置
        It("提交订单成功，库存扣减并写入订单表", func() { // spec: B1
            // WHEN 触发动作 → THEN 断言可观测变化
        })
    })
})
```

规则：

- `It` 名是一句中文，说清"什么前提下做什么发生什么"，直接抄 spec scenario 的措辞。
- `BeforeSuite` 只能放顶层；`BeforeAll` 只能放 `Ordered` 容器内。
- 顶层容器带 `Label("integration")`。子集运行：`go test ./tests/integration/... -ginkgo.label-filter=integration`。ginkgo 参数必须放在包路径之后。
- label 筛不到任何用例时默认假绿；要暴露就加 `-ginkgo.fail-on-empty`。
- ginkgo 用例和标准库用例共存无冲突，`-run TestXxx` 可单独跑标准库用例。

### 集成测试断言清单

每条 scenario 按顺序覆盖四层断言，缺哪层就在注释里说明原因：

1. **端到端响应**：请求走真实路由打到 API，断言状态码和响应体关键字段。
2. **参数 edge case**：每个入参单独覆盖——零值、空字符串、边界值（最小、最大、±1）、null、非法格式、超长。spec 里的失败场景必须逐条有对应用例，不许只测 happy path。
3. **外部服务调用参数**：捕获 mock 收到的请求，逐字段断言（模板见下）。
4. **数据库字段变动**：写操作后直接查表，断言具体字段的值，不只信写方法的返回值。

### 外部服务 mock 模板

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

### 数据库断言

- 用项目已有的真实数据库机制（`TEST_DATABASE_URL` 或一次性 PostgreSQL 容器），集成测试不 mock 数据库。
- 断言到具体字段，包括状态字段、金额、时间戳、关联记录条数：

```go
var order Order
Expect(db.Where("order_no = ?", orderNo).First(&order).Error).To(Succeed())
Expect(order.Status).To(Equal("paid"))
Expect(order.AmountCents).To(Equal(int64(9900)))
```

### Mutation testing（测试有效性验收）

变异测试验证测试真能抓到 bug，不是假绿。交付测试时必须跑。

- 工具：`go-mutesting`。**只能在 Linux/WSL 里跑**（Windows 原生编译失败）。只对本次改动的包跑，不做全量。
- 命令：

```bash
# WSL 内、项目根目录
go install github.com/zimmski/go-mutesting/cmd/go-mutesting@latest
go-mutesting ./internal/<改动包>/...
```

- 报告读法：每个变异体一行 `PASS`（被测试杀掉）或 `FAIL`（存活，附 diff）；汇总行 `The mutation score is X (n passed, m failed)`。
- **注意：有存活变异体时退出码仍是 0**，必须人工看 score 和存活清单，不能只看命令成功失败。
- 交付要求：改动说明附上 mutation score 和存活变异体清单。每个存活变异体要么补测试杀掉，要么写明理由（等价变异、不可达分支）。
- `go-mutesting` 兼容性问题时可换 `ooze`（github.com/gtramontina/ooze，维护中，支持阈值不达标时非零退出）。

## 提交前自查（AI 每次改完代码过一遍）

1. 测试跑过且全绿，命令以项目 README 里写的为准。
2. 改动没有越出任务声明的文件范围；越界了就停下来说明。
3. 新增依赖、环境变量、配置项，在改动说明里单列出来。
4. 接口改动（参数、返回、错误码）在改动说明里标"接口变更"，reviewer 重点看。
5. 新写的测试已按 spec B 编号回链，集成测试已跑 mutation testing 并在改动说明里附结果。

## review 口径（人 review AI 改动时按这个查）

- 先看测试有没有真的覆盖改动，再看实现。
- AI 自己说"已完成"不算数，以测试和运行结果为准。
- 涉及金额、权限、删除数据的代码，必须人工逐行看，AI 不能自己合入。
- 测试 review 对照 spec 查：B 编号是否全覆盖、存活变异体是否有交代。
