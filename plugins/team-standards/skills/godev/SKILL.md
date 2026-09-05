---
name: godev
description: 仅当项目是 Go 或正在写 .go 文件时启用。提供 Google Go 风格指南（命名、格式、错误处理、并发、接口、测试、godoc、模块组织）的指导，并补充团队在错误通道、测试框架、工具链上的具体约定。
---

# godev — 团队 Go 开发规范

## 范围

本 skill 覆盖 [Google Go Style Guide](https://google.github.io/styleguide/go/index) 三页（guide / decisions / best-practices），原文已中文化落到 `references/`，按需加载。**现代 Go 惯用法不在本 skill 内**：由 JetBrains 官方插件 modern-go-guidelines 的 use-modern-go skill 提供（CLI 按 go.mod 版本动态输出条目），本 skill 不复制条目内容，跟随上游更新。

- `references/guide.md` — 主指南（风格原则、核心准则；Canonical + Normative）
- `references/decisions.md` — 风格决策（命名、imports、错误、语言细节；Normative）
- `references/best-practices.md` — 最佳实践（命名细节、错误处理、文档、变量声明、测试技巧；Idiomatic）

触发后 agent 应基于"核心规则"先给出风格判断，复杂场景按主题 `Read references/<file>.md` 找原文。

## 优先级

1. **项目级说明 > godev**。项目根 `AGENTS.md` / `README` 写明偏离 Google 风格的条款时，godev 让位；reviewer 按项目说明走。
2. **team-code-standards 通用条款继续适用**。命名/函数结构/注释/依赖/格式的通用底线不变，godev 只补 Go 专精。
3. **Google styleguide 与团队约定冲突时，按下方"团队加码"小节执行**。
4. **use-modern-go 与 Google styleguide 互补不冲突**：Google 管风格与命名，use-modern-go 管语言特性的新旧写法。版本纪律优先于一切现代条目：版本不满足就不写。

## 核心规则（高频必查）

### 命名

- **包名**：全小写、单词、不带下划线；不用 `util` / `helper` / `common`；避免与常用局部变量名冲突（`count` → `usercount`）。例外：`_test` 后缀、`xxxpb` / `xxxgrpc`。
- **MixedCaps / mixedCaps**：多词命名一律 camel case，不下划线。导出 `MaxLength`，非导出 `maxLength`。初始缩写同字形（`URL` / `url`，绝不 `Url`）；特殊缩写 `ID` / `DB` / `DDoS` / `gRPC` / `iOS` 见表。
- **Getter 不加 `Get`**：`Counts()` 不是 `GetCounts()`；昂贵操作用 `Compute` / `Fetch`。
- **Receiver**：1-2 字母、类型缩写、整包统一、不下划线。
- **局部一致性**：同包同概念用同套命名；与包名/类型名/参数名重复的字段省略（如 `package yamlconfig` 的 `ParseYAMLConfig` 改 `Parse`）。

### 格式

- **`gofmt` + `goimports` 必跑**。CI 必带 `gofmt -l` / `goimports -l` 检查，失败即拒。
- **`golangci-lint` 必带**，至少开启 `errcheck` / `govet` / `staticcheck` / `unused` / `gocritic`。
- 无固定行宽；过长先想拆函数，不要拆行。条件、函数声明处不拆。

### 错误处理（团队加码）

- 函数返回 `error` 放最后；成功返 `nil`。
- 导出函数返回 `error` 类型（接口），不返具体类型。
- 不吞错误：不写 `_, _ = ...`；处理、返回、`log.Fatal` 三选一。
- **业务错误必须可被 `errors.Is` 判等**（不靠字符串匹配）：用哨兵值（`var ErrX = errors.New(...)`）或自定义类型实现 `Is() / As()`。错误码/分类挂类型上，`%w` 包装保留链。
- **不 panic 业务错误**。`log.Exit` 用于启动失败，`log.Fatal` 用于"不可能发生"的 invariant 违反。`MustXYZ` 仅用于 init/test 初始化。
- `%w` 优先放末尾 `[...]: %w`；包装哨兵错误时例外放开头（`%w: ...`）以突出分类。

### 并发

- **Goroutine 生命周期清晰**：启动后必有可见退出条件；优先 `context.Context` + `defer cancel()`；不允许泄漏。
- `context.Context` 始终第一参数（HTTP handler / streaming RPC / 测试 / `main` 入口除外）。
- 不自造 `Context` 类型或接口；用 `context.Context`。
- **Channel 必标方向**（`chan<-` / `<-chan`）；指针 sync.Mutex 不要拷贝。
- 优先同步函数；需要并发由调用方加。`errgroup` 编排相关失败。

### 接口

- **消费者定义接口**，生产者返回具体类型。
- 函数参数接接口，返回具体类型（`accept interfaces, return structs`）。
- 不要为"将来可能"提前抽接口。
- 用 `any`（Go 1.18+）代替 `interface{}`。

### 泛型

- 真有业务复用时用；不发明 DSL；不为泛型而泛型。

### 函数签名

- 避免超长参数列表；选项多时用 option struct 或 functional options。
- 指针 receiver 仅在需要修改、含不可拷贝字段（`sync.Mutex`）、或 struct 很大时用；slice / map / chan / 小数据用值 receiver。
- `switch` 不写冗余 `break`。

### 文档注释（godoc）

- 所有导出的顶层名字都要 doc comment，以被描述的名字开头。
- 完整句、首字母大写、句号结尾；struct 字段片段 OK。
- 同包用 `package <name>` 注释紧贴 `package` 声明一行。
- 用 `ExampleXxx` 写可跑示例（出现在 godoc 同时充当测试）。
- 不可推断的并发安全性、context 行为、清理责任要在 doc 里写清。

### 测试（团队加码）

- **跟团队 ginkgo 规范**：与 `team-test-standards-backend` 对齐；Go 测试统一用 ginkgo（BDD）。`*_test.go` 函数命名仍是 `TestXxx`。
- 不用 assertion 库；断言失败在 `Test` 函数本身（ginkgo 的 `Expect` 视为团队约定，等同 ginkgo spec）。
- table-driven 写法在 ginkgo 里通过 `DescribeTable` / `Entry` 实现，按 ginkgo 文档走。
- 不允许 `t.Fatal` 在非 Test goroutine 里调；`t.Error` 可继续报多条。
- 测试 helper 调用 `t.Helper()` 标注自身。
- 比较优先 `go-cmp`（`cmp.Diff` / `cmp.Equal`），避免 `reflect.DeepEqual`。
- 不做 mock 库，test double 走"`xxx_test`" 独立包，命名 `Stub` / `AlwaysCharges` 等。
- 真实 transport 优先：HTTP/RPC 测集成用真 client 连测试服务端。
- bug 修复先复现测试再改实现。

### 现代写法（use-modern-go skill 提供）

- **版本纪律**：写代码前先看项目 `go.mod` 的 `go` 版本，只写该版本及之前可用的特性。
- 新代码用现代写法；存量旧写法不动，不顺手全局替换。条目适用前提：不改变行为、能编译。
- 条目内容（min/max、slices.Contains、cmp.Or、wg.Go、t.Context、new 表达式、encoding/json/v2 等 55 条）由 use-modern-go 的 CLI 按项目 Go 版本动态列出并给详细解释，本 skill 不复制条目，跟随 JetBrains 上游更新。
- 本会话若没有 use-modern-go 的输出（插件未装或未触发），停下提醒用户安装：`/plugin marketplace add JetBrains/go-modern-guidelines` + `/plugin install modern-go-guidelines@goland-claude-marketplace`，装完 `/reload-plugins`。

### 性能

- slice / map 已知大小时 `make([]T, 0, n)` / `make(map[K]V, n)` 预分配；不要过量。
- 字符串拼接用 `strings.Builder` / `+`（小段），不要反复 `S +=` 同一个串。
- 性能优化代码加注释解释"为什么"；过度优化的复杂代码要测试+示例。

### 模块与项目

- **一个仓库一个 `go.mod`**，避免子目录出现多个 module。
- 复杂 CLI 用 `cobra` 或 `subcommands`；`cobra` 命令用 `cmd.Context()` 拿 context，别自己 `context.Background()`。
- 通用库代码不导出 flag；flag 只能在 `package main` 定义。
- Protobuf 生成包导入别名 `xxxpb` / `xxxgrpc`，不要短到 `pb`。

## 工具链

- **必装**：`gofmt` / `goimports` / `golangci-lint` / `staticcheck`。
- **CI 必跑**：`go test ./...` / `golangci-lint run` / `go mod tidy` 检查（无未用依赖）/ `govulncheck`（扫依赖 CVE，发现已知漏洞即挂）。
- **建议**：`modernize` 分析器扫新代码的过时写法（`go run golang.org/x/tools/gopls/internal/analysis/modernize/cmd/modernize@latest ./...`），修复前过目 diff。

## 触发后流程

1. 读项目 `AGENTS.md` / `README` 看是否有项目级偏离声明。
2. 看项目 `go.mod` 的 `go` 版本，确定语言特性上限。
3. 按本 skill 核心规则出风格判断与写法选择。
4. 复杂/争议场景 `Read references/<file>.md` 查中文化原文（Google 三页）；现代写法以 use-modern-go 的 list/explain 输出为准。
5. 改完跑 `gofmt -l .` / `goimports -l .` / `golangci-lint run` 全绿才算完成。

## 不在范围内

- 业务实现逻辑、API 设计、架构选型 → `team-architecture-standards`。
- 凭据、输入校验、权限、数据脱敏 → `team-code-standards` 安全红线。
- 通用命名/结构/错误/依赖/格式 → `team-code-standards`。
- 后端测试 ginkgo 规范细节 → `team-test-standards-backend`。
