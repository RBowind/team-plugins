# Go Style 决策（Decisions · Normative）

来源：https://google.github.io/styleguide/go/decisions

本文档为 Readability Mentors 参考的约定。会随时间增长，不穷尽。与 `guide.md` 冲突时**以 guide 为准**，本文件相应更新。

已从风格决策移到主指南的部分：

- **MixedCaps** → `guide.md#mixedcaps`
- **格式** → `guide.md#格式`
- **行宽** → `guide.md#行长`

---

## 命名（Naming）

### 下划线（Underscores）

允许下划线的三个例外：

1. 包名只被生成代码 import
2. `*_test.go` 里的 Test / Benchmark / Example 函数
3. 低层 cgo / OS 互操作库（罕见）

### 包名（Package names）

- 全小写，不用下划线，多词也不下划线
- 避免与常用局部变量名冲突（用 `usercount` 不用 `count`）
- 例外：`_test` 后缀（test 包）、生成 proto 代码

### Receiver 名

- 短（1-2 字母）
- 类型的缩写
- 整包一致
- 不用下划线

### 常量名

- 用 MixedCaps
- 不加 `K` 前缀
- 按"角色"命名而非"值"

```go
// Good:
const MaxPacketSize = 512
```

### 缩写词（Initialisms）

同字形一致（`URL` / `url`，绝不 `Url`）。特殊大小写混合缩写（`DDoS` / `iOS` / `gRPC`）特殊处理：

| 英文 | 作用域 | 正确 | 错误 |
|------|--------|------|------|
| XML API | 导出 | `XMLAPI` | `XmlApi` |
| iOS | 导出 | `IOS` | `Ios` |
| gRPC | 导出 | `GRPC` | `Grpc` |
| DDoS | 导出 | `DDoS` | `DDOS` |
| ID | 导出 | `ID` | `Id` |
| DB | 导出 | `DB` | `Db` |

### Getter

不加 `Get` 前缀，除非概念本身就含 "get"（HTTP GET）。`Counts()` 不用 `GetCounts()`。昂贵操作用 `Compute` / `Fetch`。

### 变量名

- 长度与作用域成正比，与使用频率成反比
- 省略类名（`users` 不用 `userSlice`）
- 省略上下文已带的信息

**单字母变量名**：仅限明显场景：receiver、`r`/`w` 用作 io.Reader/Writer、循环下标 `i`/`x`/`y`。

### 避免重复（Repetition）

包名/符号名/变量类型名/外部上下文中不要不必要重复。

---

## 注释（Commentary）

### 注释行宽

无固定宽度，~80-100 列常见。避免单条超长行。

### Doc 注释

所有顶层导出的名字都需要 doc 注释。以被描述的名字开头。

### 注释句式

完整句、首字母大写、句号结尾。struct 字段片段 OK。

### 示例（Examples）

在 test 文件里提供可运行示例。

### 命名结果参数

对清晰或 godoc 有用时命名；造成重复时省略。

### Package 注释

紧贴 `package` 子句上方，不空行。每个包一个。

---

## 导入（Imports）

### 重命名

- 避免冲突时重命名
- proto 包去掉下划线，加 `pb` 后缀

### 分组

顺序：标准库 → 第三方 → proto（`fpb`）→ 副作用（`_`）。

### Blank import（`_ "..."`）

仅在 main 包或需要的 test 中。`embed` 例外。

### Dot import（`. "..."`）

Google 代码库不用。

---

## 错误（Errors）

### 返回错误

- `error` 是最后一个返回值
- 成功返 `nil`
- 导出函数返回 `error` 类型（接口），不返具体类型

### 错误字符串

不大写（专有名词除外），不末尾加标点。

### 处理错误

不丢弃（`_`）。三选一：处理、返回、`log.Fatal` / `panic`。

### In-band 错误

不用 `-1` / `null` / `""` 表达错误；用额外返回值（`value, ok`）。

### 错误流缩进

先处理错误，主流程后续行不缩进（无 `else`）。

---

## 语言（Language）

### 字面量格式

#### 字段名

外部类型必填，本地类型可选。

#### 匹配花括号

闭合花括号与开括号同缩进。

#### Cuddled 花括号

仅当缩进匹配且值是字面量/proto builder 时用。

#### 重复类型名

slice / map 字面量可省略。

#### 零值字段

清晰时省略。

### Nil slice

与空 slice 无功能差异。倾向 `var t []string` 而非 `t := []string{}`。API 不强求 nil/空区分。

### 缩进混淆

避免换行让换行后行与缩进块对齐。

### 函数格式

签名单行。call 行不要只基于长度断行。

### 条件与循环

`if` 语句不换行。必要时把布尔运算项抽出来。Yoda 风格避免（`result == "foo"`）。

### 拷贝

不要拷贝含 mutex 或不可拷贝字段的 struct。这样的类型用指针 receiver。

### 不要 panic

用 `error` 返回。`log.Exit` 用于启动失败，`log.Fatal` 用于"不可能"条件。

### Must 函数

`MustXYZ` 命名用于 init / test 设置，panic on error。

### Goroutine 生命周期

退出条件清晰。用 `context.Context` 或同步。避免泄漏。

### 接口

需要时定义，**消费者定义接口**。函数接接口，返回具体类型。

### 泛型

真满足业务需求时用。避免过早用。不发明 DSL。

### 传值

不传 `*string` / `*io.Reader`；直接传值。例外：大型 / proto 类型。

### Receiver 类型

需要修改、含不可拷贝字段、struct 很大时用指针。slice / map / chan / 小数据用值。

### `switch` 和 `break`

`switch` 子句末尾不写冗余 `break`。

### 同步函数

倾向同步而非异步；调用方可加并发。

### Type aliases

`type T1 = T2` 谨慎用，主要用于迁移。

### 用 `%q`

`fmt.Printf("%q", s)` 而非手动加引号。

### 用 `any`

Go 1.18+ 新代码倾向 `any` 而非 `interface{}`。

---

## 公共库（Common libraries）

### Flags

Google 内部 flag 包。flag 名 snake_case，变量名 camelCase。

### 日志

Google 内部 `log` / `glog`。`log.Fatal` 带 stacktrace 退出；`log.Exit` 不带。

### Contexts

`context.Context` 始终第一参数。例外：HTTP handler / streaming RPC / test / 入口函数。

#### 自定义 context

不要自造 context 类型或用非 `context.Context` 接口。

### crypto/rand

用 `crypto/rand` 而非 `math/rand` 生成密钥。

---

## 有用的测试失败（Useful test failures）

### Assertion 库

不造 assertion 库；用 `cmp` / `fmt`。

### 标识函数

失败信息包含函数名：`MyFunc(%v) = %v, want %v`。

### 标识输入

信息中包含函数输入或测试用例描述。

### Got before want

格式：`YourFunc(%v) = %v, want %v`（实际在前，期望在后）。

### 完整结构比较

用深度比较（`cmp`）而非逐字段。

### 比较稳定结果

不比较精确序列化输出；比较语义内容。

### 继续（Keep going）

用 `t.Error` 而非 `t.Fatal` 报多个失败。

### 相等比较与 diff

用 `cmp.Equal` / `cmp.Diff`。新代码不写 `reflect.DeepEqual`。

### 详细级别

常规失败信息适合大多数 Go 测试：`YourFunc(%v) = %v, want %v`。例外：

- 复杂交互测试应描述交互本身
- 大输出时用 diff 而非全量打印

### 打印 diff

大输出对比时，用 `cmp.Diff` 产生聚焦输出。`cmp.Diff` 分两部分：`-want +got` 头和增删列表。

```go
// Good:
if diff := cmp.Diff(want, got); diff != "" {
    t.Errorf("Foo() mismatch (-want +got):\n%s", diff)
}
```

---

## 测试函数（Test functions）

### 避免臃肿的 test helper

helper 专注且轻量。避免造 "assertion library" 或 DSL。

### 标记 test helper

helper 函数开头调 `t.Helper()`。这让失败信息归因到调用方行而非 helper 内部行。

```go
// Good:
func mustMarshalAny(t *testing.T, m proto.Message) *anypb.Any {
    t.Helper()
    any, err := anypb.New(m)
    if err != nil {
        t.Fatalf("mustMarshalAny(t, m) = %v; want %v", err, nil)
    }
    return any
}
```

### Table-driven tests

多个测试用例仅几字段不同时用 table-driven + `t.Run` 子测试。

结构：

- header 描述共同输入输出
- cases 列表，每个 struct 实现共同接口

子测试名要描述场景：

```go
// Good:
func TestParse(t *testing.T) {
    tests := []struct {
        desc  string
        input string
        want  int64
        err   error
    }{
        {desc: "empty", input: "", want: 0, err: errEmpty},
        {desc: "single digit", input: "1", want: 1},
    }
    for _, test := range tests {
        t.Run(test.desc, func(t *testing.T) {
            got, err := Parse(test.input)
            if got != test.want || !errors.Is(err, test.err) {
                t.Errorf("Parse(%q) = %d, %v; want %d, %v",
                    test.input, got, err, test.want, test.err)
            }
        })
    }
}
```

#### 子测试（Subtests）

适合场景：与父测试共享 setup/cleanup/helpers；同组相似用例。

不适合时（用例差异大、需要独立 setup/cleanup、归组会模糊关系）写独立顶级测试。

#### 子测试 helpers

仅单个用例用到的 helper 直接定义在该 case 里。父测试仍可调它提供的 helpers。

### 并行测试

慢或贵 setup 的测试用 `t.Parallel()`。

注意：

- 每个并行测试跑在自己的 goroutine
- 不按指定顺序跑，不依赖其他测试顺序
- 并行测试调 `t.Fatal` / `t.Fatalf` 整个 suite 最终标记失败，但其他并行测试继续跑
- 父测试等所有并行子测试结束

---

## 公共库（续）

### Logging（补充）

- 错误日志用 `log.Error` 节制，ERROR 触发 flush 比低级日志贵；message 应是 actionable 而非"比 warning 更严重"
- 用 `log.V(1)` / `V(2)` / `V(3)` 建立 verbose 等级约定
- 注意 PII

### crypto/rand

```go
// Good:
import (
    "crypto/rand"
    "fmt"
)

func Key() string {
    buf := make([]byte, 16)
    if _, err := rand.Read(buf); err != nil {
        log.Fatalf("Out of randomness, should never happen: %v", err)
    }
    return fmt.Sprintf("%x", buf)
}
```
