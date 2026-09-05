# Go Style 最佳实践（Best Practices · Idiomatic）

来源：https://google.github.io/styleguide/go/best-practices

**说明：** 本文档是 Google 关于 [Go Style](https://google.github.io/styleguide/go/index) 系列文档的一部分。它**既非 [规范性的](https://google.github.io/styleguide/go/index#normative) 也非 [权威性的](https://google.github.io/styleguide/go/index#canonical)**，而是 [核心风格指南](https://google.github.io/styleguide/go/guide) 的辅助文档。详见 [概览](https://google.github.io/styleguide/go/index#about)。

## 关于

本文档给出**关于如何最佳应用 Go Style 指南的指引**。这些指引针对频繁出现的常见情形，但不适用于所有情况。在可能的情况下，会讨论多种可选方案以及何时该用、何时不该用的考量。

完整风格指南文档集请参见 [概览](https://google.github.io/styleguide/go/index#about)。

## 命名

### 函数和方法命名

#### 避免重复

为函数或方法选择名字时，要考虑这个名字将在什么上下文中被阅读。参考以下建议以避免调用点出现多余的 [重复](https://google.github.io/styleguide/go/decisions#repetition)：

*   通常可以从函数和方法名中省略：
    *   输入和输出的类型（在没有冲突时）
    *   方法接收者的类型
    *   输入或输出是否为指针
*   对于函数，[不要重复包名](https://google.github.io/styleguide/go/decisions#repetitive-with-package)。

        // Bad:
        package yamlconfig

        func ParseYAMLConfig(input string) (*Config, error)

        // Good:
        package yamlconfig

        func Parse(input string) (*Config, error)

*   对于方法，不要重复方法接收者的名字。

        // Bad:
        func (c *Config) WriteConfigTo(w io.Writer) (int64, error)

        // Good:
        func (c *Config) WriteTo(w io.Writer) (int64, error)

*   不要重复作为参数传入的变量名。

        // Bad:
        func OverrideFirstWithSecond(dest, source *Config) error

        // Good:
        func Override(dest, source *Config) error

*   不要重复返回值名和类型。

        // Bad:
        func TransformToJSON(input *Config) *jsonconfig.Config

        // Good:
        func Transform(input *Config) *jsonconfig.Config

当确实需要区分相似名字的函数时，可以在名字中包含额外的可分辨信息。

    // Good:
    func (c *Config) WriteTextTo(w io.Writer) (int64, error)
    func (c *Config) WriteBinaryTo(w io.Writer) (int64, error)

#### 命名约定

为函数和方法命名时还有一些常见的约定：

*   返回某个值的函数，使用名词形式的名字。

        // Good:
        func (c *Config) JobName(key string) (value string, ok bool)

    一个推论是：函数和方法名应该[避免 `Get` 前缀](https://google.github.io/styleguide/go/decisions#getters)。

        // Bad:
        func (c *Config) GetJobName(key string) (value string, ok bool)

*   执行某个动作的函数，使用动词形式的名字。

        // Good:
        func (c *Config) WriteDetail(w io.Writer) (int64, error)

*   仅在涉及类型上有差别的同名函数，应在名字末尾带上类型的名称。

        // Good:
        func ParseInt(input string) (int, error)
        func ParseInt64(input string) (int64, error)
        func AppendInt(buf []byte, value int) []byte
        func AppendInt64(buf []byte, value int64) []byte

    如果存在一个明显的"主"版本，则该版本的类型可以省略：

        // Good:
        func (c *Config) Marshal() ([]byte, error)
        func (c *Config) MarshalText() (string, error)

### 测试替身与辅助包

在为测试辅助（尤其是 [测试替身](https://abseil.io/resources/swe-book/html/ch13.html#basic_concepts)）的包和类型做 [命名](https://google.github.io/styleguide/go/guide#naming) 时，可以采用以下几种规范。测试替身可以是 stub、fake、mock 或 spy。

下面这些示例主要用 stub。如果你的代码使用 fake 或其他种类的测试替身，请相应修改名字。

假设你有一个聚焦良好的生产代码包，类似下面这样：

    package creditcard

    import (
        "errors"

        "path/to/money"
    )

    // ErrDeclined 表示发卡方拒绝了该笔扣款。
    var ErrDeclined = errors.New("creditcard: declined")

    // Card 包含信用卡的相关信息，如发卡方、有效期和额度。
    type Card struct {
        // 已省略
    }

    // Service 允许你通过外部支付处理商执行信用卡相关操作，例如扣款、授权、退款和订阅。
    type Service struct {
        // 已省略
    }

    func (s *Service) Charge(c *Card, amount money.Money) error { /* 已省略 */ }

#### 创建测试辅助包

假设你想为另一个包创建包含测试替身的包。我们以 `package creditcard`（见上）为例：

一种做法是基于生产包，引入一个新的 Go 包用作测试。一个稳妥的选择是在原包名后追加 `test`（`creditcard` + `test`）：

    // Good:
    package creditcardtest

    除非另有说明，以下各小节中的所有示例都在 `package creditcardtest` 中。

#### 简单情形

你想为 `Service` 添加一组测试替身。因为 `Card` 本质上是一个纯数据类型，类似 Protocol Buffer 消息，在测试中无需特殊处理，所以不需要替身。如果预期只为一个类型（如 `Service`）创建测试替身，可以采用简洁的命名方式：

    // Good:
    import (
        "path/to/creditcard"
        "path/to/money"
    )

    // Stub 是 creditcard.Service 的替身，本身不提供任何行为。
    type Stub struct{}

    func (Stub) Charge(*creditcard.Card, money.Money) error { return nil }

这种命名严格优于 `StubService` 或更糟糕的 `StubCreditCardService`，因为包名和领域类型本身已经说明 `creditcardtest.Stub` 是什么。

最后，如果包是用 Bazel 构建的，请确保新包的 `go_library` 规则标记为 `testonly`：

    # Good:
    go_library(
        name = "creditcardtest",
        srcs = ["creditcardtest.go"],
        deps = [
            ":creditcard",
            ":money",
        ],
        testonly = True,
    )

上述做法是约定俗成的，其他工程师也都能很好地理解。

另见：

*   [Go Tip #42: Authoring a Stub for Testing](https://google.github.io/styleguide/go/index.html#gotip)

#### 多种替身行为

当一种 stub 不够用（例如你还需要一个总是失败的版本）时，建议根据替身所模拟的行为来命名。下面把 `Stub` 重命名为 `AlwaysCharges`，并新增一个名为 `AlwaysDeclines` 的 stub：

    // Good:
    // AlwaysCharges 是 creditcard.Service 的替身，模拟扣款成功。
    type AlwaysCharges struct{}

    func (AlwaysCharges) Charge(*creditcard.Card, money.Money) error { return nil }

    // AlwaysDeclines 是 creditcard.Service 的替身，模拟扣款被拒。
    type AlwaysDeclines struct{}

    func (AlwaysDeclines) Charge(*creditcard.Card, money.Money) error {
        return creditcard.ErrDeclined
    }

#### 多类型多个替身

现在假设 `package creditcard` 里有多个类型需要做替身，如下所示的 `Service` 和 `StoredValue`：

    package creditcard

    type Service struct {
        // 已省略
    }

    type Card struct {
        // 已省略
    }

    // StoredValue 管理客户的信用余额。这适用于退回商品时将金额退到客户的本地账户，
    // 而不是经由信用卡组织处理的场景。因此，它被实现为独立的服务。
    type StoredValue struct {
        // 已省略
    }

    func (s *StoredValue) Credit(c *Card, amount money.Money) error { /* 已省略 */ }

在这种情况下，更有明确性的替身命名是合理的：

    // Good:
    type StubService struct{}

    func (StubService) Charge(*creditcard.Card, money.Money) error { return nil }

    type StubStoredValue struct{}

    func (StubStoredValue) Credit(*creditcard.Card, money.Money) error { return nil }

#### 测试中的局部变量

当测试中的变量引用替身时，应选择能最清晰地把替身和其他生产类型区分开来的名字。考虑如下要测试的生产代码：

    package payment

    import (
        "path/to/creditcard"
        "path/to/money"
    )

    type CreditCard interface {
        Charge(*creditcard.Card, money.Money) error
    }

    type Processor struct {
        CC CreditCard
    }

    var ErrBadInstrument = errors.New("payment: instrument is invalid or expired")

    func (p *Processor) Process(c *creditcard.Card, amount money.Money) error {
        if c.Expired() {
            return ErrBadInstrument
        }
        return p.CC.Charge(c, amount)
    }

在测试中，针对 `CreditCard` 的一个名为 "spy" 的测试替身与生产类型并列出现，因此给名字加前缀可以提高清晰度。

    // Good:
    package payment

    import "path/to/creditcardtest"

    func TestProcessor(t *testing.T) {
        var spyCC creditcardtest.Spy
        proc := &Processor{CC: spyCC}

        // 已省略 card 和 amount 的声明
        if err := proc.Process(card, amount); err != nil {
            t.Errorf("proc.Process(card, amount) = %v, want nil", err)
        }

        charges := []creditcardtest.Charge{
            {Card: card, Amount: amount},
        }

        if got, want := spyCC.Charges, charges; !cmp.Equal(got, want) {
            t.Errorf("spyCC.Charges = %v, want %v", got, want)
        }
    }

这比不加前缀的命名更清晰。

    // Bad:
    package payment

    import "path/to/creditcardtest"

    func TestProcessor(t *testing.T) {
        var cc creditcardtest.Spy

        proc := &Processor{CC: cc}

        // 已省略 card 和 amount 的声明
        if err := proc.Process(card, amount); err != nil {
            t.Errorf("proc.Process(card, amount) = %v, want nil", err)
        }

        charges := []creditcardtest.Charge{
            {Card: card, Amount: amount},
        }

        if got, want := cc.Charges, charges; !cmp.Equal(got, want) {
            t.Errorf("cc.Charges = %v, want %v", got, want)
        }
    }

### 变量遮蔽

**说明：** 本节使用两个非正式术语：*stomping*（覆盖）和 *shadowing*（遮蔽）。它们并非 Go 语言规范中的官方概念。

和许多编程语言一样，Go 有可变变量：给一个变量赋值会改变它的值。

    // Good:
    func abs(i int) int {
        if i < 0 {
            i *= -1
        }
        return i
    }

在使用带 `:=` 的 [短变量声明](https://go.dev/ref/spec#Short_variable_declarations) 时，某些情况下不会创建新变量。我们可以称之为 *stomping*（覆盖）。当原值不再需要时，这样做没问题。

    // Good:
    // innerHandler 是某个请求处理器的辅助函数，该处理器本身会向后端发起请求。
    func (s *Server) innerHandler(ctx context.Context, req *pb.MyRequest) *pb.MyResponse {
        // 无条件地为这部分请求处理限定一个截止时间。
        ctx, cancel := context.WithTimeout(ctx, 3*time.Second)
        defer cancel()
        ctxlog.Info(ctx, "Capped deadline in inner request")

        // 这里的代码不再能访问原来的 context。
        // 这是一种好的写法——如果在第一次写这段代码时就预期到：
        // 即使代码不断增长，也没有任何操作应该使用调用者所提供的（可能未设上限的）原始 context。

        // ...
    }

但要小心在新的作用域里使用短变量声明：那样会引入一个新变量。我们可以称之为对原变量的 *shadowing*（遮蔽）。代码块结束之后，引用的又是原来的变量。下面是一段想要有条件地缩短截止时间但有 bug 的尝试：

    // Bad:
    func (s *Server) innerHandler(ctx context.Context, req *pb.MyRequest) *pb.MyResponse {
        // 试图有条件地缩短截止时间。
        if *shortenDeadlines {
            ctx, cancel := context.WithTimeout(ctx, 3*time.Second)
            defer cancel()
            ctxlog.Info(ctx, "Capped deadline in inner request")
        }

        // BUG：这里的 "ctx" 又变回了调用者传入的那个 context。
        // 上面的错误代码之所以能通过编译，是因为 ctx 和 cancel
        // 在 if 语句内部都被使用了。

        // ...
    }

一个正确的版本可能是：

    // Good:
    func (s *Server) innerHandler(ctx context.Context, req *pb.MyRequest) *pb.MyResponse {
        if *shortenDeadlines {
            var cancel func()
            // 注意这里使用的是简单赋值 =，而不是 :=。
            ctx, cancel = context.WithTimeout(ctx, 3*time.Second)
            defer cancel()
            ctxlog.Info(ctx, "Capped deadline in inner request")
        }
        // ...
    }

在我们称为 stomping 的情况下，因为没有新变量，被赋值的类型必须与原变量匹配。而 shadowing 则引入了一个全新的实体，因此可以是不同的类型。有意地使用 shadowing 是一种有用的做法，但只要能提高 [清晰度](https://google.github.io/styleguide/go/guide#clarity)，你随时可以用一个新名字。

不要在极小的作用域之外使用与标准包同名的变量，因为这会让来自那个包的自由函数和值变得不可访问。相反地，在为你的包选名字时，要避免那些可能需要 [import 重命名](https://google.github.io/styleguide/go/decisions#import-renaming) 或在客户端引起良好变量名遮蔽的名字。

    // Bad:
    func LongFunction() {
        url := "https://example.com/"
        // 糟糕，下面的代码就没法用 net/url 了。
    }

### util 包

Go 包的名字由 `package` 声明指定，与 import 路径分开。包名对可读性的影响远大于路径。

Go 包名应该[与它提供的内容相关](https://google.github.io/styleguide/go/decisions#package-names)。把包简单命名为 `util`、`helper`、`common` 之类的通常是糟糕的选择（不过可以用作名字的*一部分*）。信息不足的名字会让代码更难阅读；用得太宽时，还容易引发不必要的 [import 冲突](https://google.github.io/styleguide/go/decisions#import-renaming)。

反过来，可以考虑调用点会是什么样。

    // Good:
    db := spannertest.NewDatabaseFromFile(...)

    _, err := f.Seek(0, io.SeekStart)

    b := elliptic.Marshal(curve, x, y)

即使不看 import 列表（`cloud.google.com/go/spanner/spannertest`、`io` 和 `crypto/elliptic`），你也能大致知道每行在做什么。如果名字不够聚焦，就会变成下面这样：

    // Bad:
    db := test.NewDatabaseFromFile(...)

    _, err := f.Seek(0, common.SeekStart)

    b := helper.Marshal(curve, x, y)

## 包的大小

如果你在想 Go 包应该有多大，以及应该把相关的类型放在同一个包里还是拆成不同的包，可以先看看 [Go 博客上关于包名的文章](https://go.dev/blog/package-names)。尽管标题讲的是命名，但其实并不只讲命名。其中包含了一些有用的提示，并引用了几篇值得一读的文章和演讲。

以下是一些其他的考量和说明。

用户在一个页面里就能看到该包的 [godoc](https://pkg.go.dev/)，而包里类型所导出的方法会按类型分组。Godoc 还会把构造函数与它们返回的类型放在一起。如果 *客户端代码* 很可能需要两个不同类型的值相互交互，把它们放在同一个包里对用户来说会更方便。

包内的代码可以访问包里未导出的标识符。如果你有几个*实现*上紧密耦合的相关类型，把它们放在同一个包里就能实现这种耦合，又不会把这些细节污染到公开 API 上。判断这种耦合是否成立的一个好方法：假想存在一个用户要同时使用两个包，且这两个包覆盖密切相关的主题——如果用户必须 import 两个包才能有意义地使用其中任意一个，那把它们合并通常就是正确的事。标准库通常很好地体现了这种作用域和分层。

话虽如此，把整个项目放在一个包里很可能让那个包变得过大。当某个东西在概念上独立时，给它单独开一个小包会更易用。客户端所知的包短名与导出类型名一起组成了一个有意义的标识符：例如 `bytes.Buffer`、`ring.New`。[包名博客文章](https://go.dev/blog/package-names) 有更多例子。

Go 风格对文件大小是灵活的，因为维护者可以在同一个包内自由地把代码从一个文件移到另一个文件，而不影响调用方。但作为一般性的指导原则：通常不推荐单个文件里有成千上万行，也不推荐有大量很小的文件。不像其他一些语言，Go 并没有"一个类型一个文件"的约定。凭经验而言：文件要聚焦到让维护者能一眼看出哪份文件包含什么，同时又要小到能很容易地找到内容。标准库经常把大包拆成几个源文件，把相关代码按文件归类。[`bytes` 包的源代码](https://go.googlesource.com/go/+/refs/heads/master/src/bytes/) 是一个不错的范例。如果包的文档很长，包可以选择单独用一个叫 `doc.go` 的文件来放 [包文档](https://google.github.io/styleguide/go/decisions#package-comments)、package 声明，不放别的东西，但这不是必需的。

在 Google 代码库内部以及使用 Bazel 的项目中，Go 代码的目录布局与开源 Go 项目不同：可以在单个目录里有多个 `go_library` target。如果预期未来要开源你的项目，那么给每个包安排独立目录就是一个好理由。

下面这些非权威的参考示例，有助于展现这些思路的具体运用：

*   小型包，只包含一个有凝聚力的想法，不多不少：
    *   [`csv` 包](https://pkg.go.dev/encoding/csv)：CSV 数据的编解码，职责分别由 [reader.go](https://go.googlesource.com/go/+/refs/heads/master/src/encoding/csv/reader.go) 和 [writer.go](https://go.googlesource.com/go/+/refs/heads/master/src/encoding/csv/writer.go) 承担。
    *   [`expvar` 包](https://pkg.go.dev/expvar)：白盒式的程序度量，全部集中在 [expvar.go](https://go.googlesource.com/go/+/refs/heads/master/src/expvar/expvar.go) 中。
*   中等大小的包，包含一个较大的领域及其多种职责：
    *   [`flag` 包](https://pkg.go.dev/flag)：命令行 flag 管理，全部包含在 [flag.go](https://go.googlesource.com/go/+/refs/heads/master/src/flag/flag.go) 中。
*   大型包，把若干紧密相关的领域拆分到多个文件里：
    *   [`http` 包](https://pkg.go.dev/net/http)：HTTP 的核心：[client.go](https://go.googlesource.com/go/+/refs/heads/master/src/net/http/client.go) 支持 HTTP 客户端；[server.go](https://go.googlesource.com/go/+/refs/heads/master/src/net/http/server.go) 支持 HTTP 服务端；[cookie.go](https://go.googlesource.com/go/+/refs/heads/master/src/net/http/cookie.go) 管理 cookie。
    *   [`os` 包](https://pkg.go.dev/os)：跨平台操作系统抽象：[exec.go](https://go.googlesource.com/go/+/refs/heads/master/src/os/exec.go) 子进程管理；[file.go](https://go.googlesource.com/go/+/refs/heads/master/src/os/file.go) 文件管理；[tempfile.go](https://go.googlesource.com/go/+/refs/heads/master/src/os/tempfile.go) 临时文件。

另见：

*   [测试替身包](#naming-doubles)
*   [Organizing Go Code（博客文章）](https://go.dev/blog/organizing-go-code)
*   [Organizing Go Code（演讲）](https://go.dev/talks/2014/organizeio.slide)

## Imports

### Protocol Buffer 消息与 Stub

Proto 库的 import 由于其跨语言特性，与标准的 Go import 处理方式不同。重命名 proto import 的约定基于生成该包的规则：

*   `go_proto_library` 规则通常使用 `pb` 后缀。
*   `go_grpc_library` 规则通常使用 `grpc` 后缀。

通常会用一个单词来描述该包：

    // Good:
    import (
        foopb "path/to/package/foo_service_go_proto"
        foogrpc "path/to/package/foo_service_go_grpc"
    )

请遵循 [包名](https://google.github.io/styleguide/go/decisions#package-names) 的风格指南。优先使用完整的单词。短名固然好，但要避免歧义。拿不准时，就用 proto 包名去掉 `_go` 部分，再加上 `pb` 后缀：

    // Good:
    import (
        pushqueueservicepb "path/to/package/push_queue_service_go_proto"
    )

**说明：** 过去的指引曾鼓励用极短的名字，例如 `xpb` 甚至就一个 `pb`。新代码应优先使用更具描述性的名字。使用短名的旧代码不应被当作范例，但也不需要专门去改。

### Import 排序

参见 [Go Style Decisions: Import grouping](https://google.github.io/styleguide/go/decisions#import-grouping)。

## 错误处理

在 Go 中，[errors 是值](https://go.dev/blog/errors-are-values)；它们由代码产生，也由代码消费。错误可以：

*   转换成展示给人类的诊断信息
*   被维护者使用
*   被终端用户解读

错误消息也会出现在各种不同的载体上，包括日志消息、错误转储和呈现的 UI。

处理（产生或消费）错误的代码应该有意识地去做。忽略或盲目向上传递错误的返回值是很诱人的做法。然而，始终值得思考的是：当前调用栈中的函数是否处于能最高效处理该错误的位置。这是一个很大的话题，很难给出绝对的建议。凭你的判断，但请记住以下考量：

*   构造一个错误值时，决定是否给它赋予一定的 [结构](#error-structure)。
*   处理错误时，考虑[补充](#error-extra-info) 那些你有而调用方和/或被调方可能没有的信息。
*   同时参见关于 [错误日志](#error-logging) 的指引。

虽然通常不应该忽略错误，但一个合理的例外是编排相关的操作时，通常只有第一个错误有用。[`errgroup` 包](https://pkg.go.dev/golang.org/x/sync/errgroup) 提供了一个方便的抽象，用来处理一组可以一起失败或取消的操作。

另见：

*   [Effective Go 中关于 errors 的章节](https://go.dev/doc/effective_go#errors)
*   [Go 博客中关于 errors 的文章](https://go.dev/blog/go1.13-errors)
*   [`errors` 包](https://pkg.go.dev/errors)
*   [`upspin.io/errors` 包](https://commandcenter.blogspot.com/2017/12/error-handling-in-upspin.html)
*   [GoTip #89: When to Use Canonical Status Codes as Errors](https://google.github.io/styleguide/go/index.html#gotip)
*   [GoTip #48: Error Sentinel Values](https://google.github.io/styleguide/go/index.html#gotip)
*   [GoTip #13: Designing Errors for Checking](https://google.github.io/styleguide/go/index.html#gotip)

### 错误的结构

如果调用方需要探查错误（例如区分不同的错误情况），那么应赋予错误值结构，以便以编程方式完成这件事，而不是让调用方去做字符串匹配。这条建议既适用于生产代码，也适用于关心不同错误情况的测试。

最简单的结构化错误是无参数的全局值。

    type Animal string

    var (
        // ErrDuplicate 表示该动物已经被见过。
        ErrDuplicate = errors.New("duplicate")

        // ErrMarsupial 出现是因为我们对澳大利亚以外的有袋类过敏。
        // 抱歉。
        ErrMarsupial = errors.New("marsupials are not supported")
    )

    func process(animal Animal) error {
        switch {
        case seen[animal]:
            return ErrDuplicate
        case marsupial(animal):
            return ErrMarsupial
        }
        seen[animal] = true
        // ...
        return nil
    }

调用方可以直接将函数返回的错误值与已知的错误值进行比较：

    // Good:
    func handlePet(...) {
        switch err := process(an); err {
        case ErrDuplicate:
            return fmt.Errorf("feed %q: %v", an, err)
        case ErrMarsupial:
            // 尝试用一个朋友来恢复。
            alternate = an.BackupAnimal()
            return handlePet(..., alternate, ...)
        }
    }

上面使用了 sentinel 值，要求错误与期望值（从 `==` 意义上）相等。在很多场景下这完全够用。如果 `process` 返回的是包装过的错误（下文会讨论），你可以使用 [`errors.Is`](https://pkg.go.dev/errors#Is)。

    // Good:
    func handlePet(...) {
        switch err := process(an); {
        case errors.Is(err, ErrDuplicate):
            return fmt.Errorf("feed %q: %v", an, err)
        case errors.Is(err, ErrMarsupial):
            // ...
        }
    }

不要试图基于错误的字符串形式来区分错误。详见 [Go Tip #13: Designing Errors for Checking](https://google.github.io/styleguide/go/index.html#gotip)。

    // Bad:
    func handlePet(...) {
        err := process(an)
        if regexp.MatchString(`duplicate`, err.Error()) {...}
        if regexp.MatchString(`marsupial`, err.Error()) {...}
    }

如果错误里有调用方需要以编程方式访问的额外信息，理想情况下应当以结构化的方式呈现。例如，[`os.PathError`](https://pkg.go.dev/os#PathError) 类型把失败操作的路径放在一个结构体字段里，调用方可以很方便地读取它。

其他结构也可以酌情使用，例如包含错误码和详情字符串的项目结构体。[`status` 包](https://pkg.go.dev/google.golang.org/grpc/status) 是常用的封装；如果选用这种方式（你并非必须），请使用 [规范码](https://pkg.go.dev/google.golang.org/grpc/codes)。参见 [Go Tip #89: When to Use Canonical Status Codes as Errors](https://google.github.io/styleguide/go/index.html#gotip) 来判断使用 status code 是不是合适的选择。

### 给错误补充信息

给错误补充信息时，避免引入底层错误已经包含的冗余信息。例如 `os` 包已经在它的错误里包含了路径信息。

    // Good:
    if err := os.Open("settings.txt"); err != nil {
      return fmt.Errorf("launch codes unavailable: %v", err)
    }

    // Output:
    //
    // launch codes unavailable: open settings.txt: no such file or directory

这里，"launch codes unavailable" 给 `os.Open` 的错误添加了与当前函数上下文相关的特定含义，又没有重复底层的文件路径信息。

    // Bad:
    if err := os.Open("settings.txt"); err != nil {
      return fmt.Errorf("could not open settings.txt: %v", err)
    }

    // Output:
    //
    // could not open settings.txt: open settings.txt: no such file or directory

如果注解的唯一目的只是表明发生了失败、又没有添加任何新信息，那就不必加。错误的存在本身已经足以向调用方传达失败。

    // Bad:
    return fmt.Errorf("failed: %v", err) // 直接返回 err 即可

在用 `fmt.Errorf` 包装错误时，[选择 `%v` 还是 `%w`](https://go.dev/blog/go1.13-errors#whether-to-wrap) 是个细致但影响重大的决定——它会显著影响错误在你的应用中如何传播、处理、检视和文档化。核心原则是：让错误值对它们的观察者有用，无论观察者是人类还是代码。

1.  **用 `%v` 做简单的注解或构造新错误**

    `%v` 是对任意 Go 值进行字符串格式化时的通用工具，包括错误。当与 `fmt.Errorf` 配合使用时，它会把错误的字符串表示（`Error()` 方法的返回值）嵌入到新的错误值中，丢掉原错误的任何结构化信息。下面这些场景使用 `%v`：

    *   添加有意义的、非冗余的上下文：如上例所示。

    *   记录或展示错误：当主要目标是把人类可读的错误消息呈现到日志里或展示给用户，且你不打算让调用方以编程方式 `errors.Is` 或 `errors.As` 错误时（注意：这里通常不推荐用 `errors.Unwrap`，因为它不处理多错误）。

    *   构造全新的、独立的错误：有时需要把一个错误转换成新的错误消息，从而隐藏原始错误的具体细节。这种做法在系统边界处尤其有益，包括但不限于 RPC、IPC 和存储——在这些地方我们会把领域特定错误翻译到规范的错误空间里。

            // Good:
            func (*FortuneTeller) SuggestFortune(context.Context, *pb.SuggestionRequest) (*pb.SuggestionResponse, error) {
              // ...
              if err != nil {
                return nil, fmt.Errorf("couldn't find fortune database: %v", err)
              }
            }

        我们也可以显式地给上面的例子加上 RPC code `Internal` 的注解。

            // Good:
            import (
              "google.golang.org/grpc/codes"
              "google.golang.org/grpc/status"
            )

            func (*FortuneTeller) SuggestFortune(context.Context, *pb.SuggestionRequest) (*pb.SuggestionResponse, error) {
              // ...
              if err != nil {
                // 如果是故意包装一个供调用方解包的错误，也可以用 fmt.Errorf 配合 %w。
                return nil, status.Errorf(codes.Internal, "couldn't find fortune database", status.ErrInternal)
              }
            }

2.  **`%w`（包装）用于编程方式检视与错误链**

    `%w` 是专门为错误包装设计的。它会创建一个提供 `Unwrap()` 方法的新错误，让调用方可以用 `errors.Is` 和 `errors.As` 编程遍历错误链。下面这些场景使用 `%w`：

    *   在保留原错误以便编程检视的同时添加上下文：这是应用内部辅助函数的主要用例。你希望用额外上下文（比如失败时正在执行什么操作）丰富错误，但仍然允许调用方检查底层错误是否是某个特定的 sentinel 错误或类型。

            // Good:
            func (s *Server) internalFunction(ctx context.Context) error {
              // ...
              if err != nil {
                return fmt.Errorf("couldn't find remote file: %w", err)
              }
            }

        这样一来，即便底层错误被包装过，高层函数仍可以 `errors.Is(err, fs.ErrNotExist)` 进行判断。

        当你的系统与外部系统（如 RPC、IPC 或存储）交互时，往往更适合把领域特定错误翻译到标准化的错误空间（例如 gRPC status code），而不是简单地把底层原始错误用 `%w` 包起来。客户端通常不关心具体的内部文件系统错误，它关心的是规范化的结果（例如 `Internal`、`NotFound`、`PermissionDenied`）。

    *   当你显式记录并测试你所暴露的底层错误时：如果你的包 API 保证了某些底层错误能被调用方解包并检查（例如"这个函数可能返回被包装在更通用错误里的 `ErrInvalidConfig`"），那么 `%w` 就是合适的。这构成了你包契约的一部分。

另见：

*   [错误文档约定](#documentation-conventions-errors)
*   [关于错误包装的博客文章](https://blog.golang.org/go1.13-errors)

### `%w` 在错误中的位置

如果打算用 `%w` 格式化动词进行 [错误包装](https://go.dev/blog/go1.13-errors)，优先把 `%w` 放在错误字符串的末尾。

错误可以用 `%w` 包装，也可以把错误放进实现了 `Unwrap() error` 的 [结构化错误](https://google.github.io/styleguide/go/index.html#gotip) 里（例如 [`fs.PathError`](https://pkg.go.dev/io/fs#PathError)）。

包装过的错误会形成错误链：每一层包装都会在错误链的最前面加一个新节点。错误链可以通过 `Unwrap() error` 方法遍历。例如：

    err1 := fmt.Errorf("err1")
    err2 := fmt.Errorf("err2: %w", err1)
    err3 := fmt.Errorf("err3: %w", err2)

它构成了这样的错误链：

    flowchart LR
      err3 == err3 wraps err2 ==> err2;
      err2 == err2 wraps err1 ==> err1;

无论 `%w` 放在哪里，返回的错误总是代表错误链的最前面，`%w` 是它的下一个子节点。同样，`Unwrap() error` 总是从最新到最旧遍历错误链。

然而 `%w` 的位置确实会影响错误链的打印顺序是从新到旧、从旧到新，抑或两者都不是：

    // Good:
    err1 := fmt.Errorf("err1")
    err2 := fmt.Errorf("err2: %w", err1)
    err3 := fmt.Errorf("err3: %w", err2)
    fmt.Println(err3) // err3: err2: err1
    // err3 是一个从新到旧的错误链，按从新到旧打印。

    // Bad:
    err1 := fmt.Errorf("err1")
    err2 := fmt.Errorf("%w: err2", err1)
    err3 := fmt.Errorf("%w: err3", err2)
    fmt.Println(err3) // err1: err2: err3
    // err3 是一个从新到旧的错误链，但按从旧到新打印。

    // Bad:
    err1 := fmt.Errorf("err1")
    err2 := fmt.Errorf("err2-1 %w err2-2", err1)
    err3 := fmt.Errorf("err3-1 %w err3-2", err2)
    fmt.Println(err3) // err3-1 err2-1 err1 err2-2 err3-2
    // err3 是一个从新到旧的错误链，既不是从新到旧，也不是从旧到新打印。

因此，为了让错误文本与错误链结构一致，请优先把 `%w` 放在末尾，形式为 `[...]: %w`。

#### Sentinel 错误的位置

这条规则有一个例外：在包装 sentinel 错误时。Sentinel 错误是作为失败主要分类的错误。这有助于观察者快速理解失败的性质（比如"未找到"或"无效参数"），而无需解析整条错误消息。越早识别出这种错误类型越好。

Sentinel 错误的例子包括 os 错误（如 [`os.ErrInvalid`](https://pkg.go.dev/os#ErrInvalid)）和包级错误。

在这些情况下，把 `%w` 放在错误字符串的开头能通过立即识别错误分类来提升可读性。

    // Good:
    package parser

    var ErrParse = fmt.Errorf("parse error")

    // 这是另一个可能返回的包错误。
    var ErrParseInvalidHeader = fmt.Errorf("%w: invalid header", ErrParse)

    func parseHeader() error {
      err := checkHeader()
      return fmt.Errorf("%w: invalid character in header: %v", ErrParseInvalidHeader, err)
    }

    err := fmt.Errorf("%w: couldn't find fortune database: %v", ErrInternal, err)

把状态码放在开头可以确保最相关的分类信息最显眼。

    // Bad:
    package parser

    var ErrParse = fmt.Errorf("parse error")

    // 这是另一个可能返回的包错误。
    var ErrParseInvalidHeader = fmt.Errorf("%w: invalid header", ErrParse)

    func parseHeader() error {
      err := checkHeader()
      return fmt.Errorf("invalid character in header: %v: %w", err, ErrParseInvalidHeader)
    }

    var ErrInternal = status.Error(codes.Internal, "internal")
    err2 := fmt.Errorf("couldn't find fortune database: %v: %w", err, ErrInternal)

如果把它放在末尾，当阅读错误文本时，错误分类就会被淹没在具体细节中，更难识别。

另见：

*   [Go Tip #48: Error Sentinel Values](https://google.github.io/styleguide/go/index.html#gotip)
*   [Go Tip #106: Error Naming Conventions](https://google.github.io/styleguide/go/index.html#gotip)

### 记录错误

有时函数需要把错误告诉外部系统，但又不会把它继续向上传递给调用方。日志是显而易见的选择；但要意识到你记的是什么、怎么记。

*   像 [好的测试失败消息](https://google.github.io/styleguide/go/decisions#useful-test-failures) 一样，日志消息应当清楚地说明发生了什么问题，并通过包含相关诊断信息来帮助维护者。

*   避免重复。如果你要返回一个错误，通常更好的是不要自己再记录一遍，而是让调用方来处理。调用方可以选择记录错误，或者使用 [`rate.Sometimes`](https://pkg.go.dev/golang.org/x/time/rate#Sometimes) 进行日志限速。其他选项包括尝试恢复，甚至 [停止程序](#checks-and-panics)。无论如何，把控制权交给调用方有助于避免日志刷屏。

    然而这种做法有一个缺点：所有的日志都会以调用方的代码坐标写入。

*   注意 [PII](https://en.wikipedia.org/wiki/Personal_data)。很多日志汇聚点并不适合存放敏感的终端用户信息。

*   谨慎使用 `log.Error`。ERROR 级别的日志会导致 flush，并且比低级别日志更昂贵。这可能对你的代码性能产生严重影响。在 error 和 warning 之间做选择时，要记住一条最佳实践：error 级别的消息应当是可以采取行动的，而不只是在"严重程度"上高于 warning。

*   在 Google 内部，我们有一些监控系统可以比"写一行日志然后期待有人注意到"提供更有效的告警。这与标准库的 [`expvar` 包](https://pkg.go.dev/expvar) 类似但不完全相同。

#### 自定义详细级别

善用详细日志（[`log.V`](https://pkg.go.dev/github.com/golang/glog#V)）。详细日志在开发和追踪时很有用。在详细级别上建立一个约定是有帮助的，例如：

*   在 `V(1)` 写少量额外信息
*   在 `V(2)` 追踪更多信息
*   在 `V(3)` 倾倒大量内部状态

为了最小化详细日志的成本，应当确保即使在 `log.V` 关闭时也不会意外调用开销昂贵的函数。`log.V` 提供两种 API。比较方便的那种存在这种意外开销的风险。拿不准时，就用稍显啰嗦的写法。

    // Good:
    for _, sql := range queries {
      log.V(1).Infof("Handling %v", sql)
      if log.V(2) {
        log.Infof("Handling %v", sql.Explain())
      }
      sql.Run(...)
    }

    // Bad:
    // 即使这条日志不会被打印，sql.Explain 也照样被调用了。
    log.V(2).Infof("Handling %v", sql.Explain())

### 程序初始化

程序初始化阶段的错误（如 flag 错误、配置错误）应当向上传播给 `main`，由 `main` 调用 `log.Exit`，并附上一条解释如何修复该错误的消息。这种情况下通常不应使用 `log.Fatal`，因为指向检查代码行的栈追踪往往不如一条人类生成的、可执行的错误消息来得有用。

### 程序检查与 panic

正如 [关于反对 panic 的决策](https://google.github.io/styleguide/go/decisions#dont-panic) 中所述，标准的错误处理应当围绕错误返回值来构建。库应当优先把错误返回给调用方，而不是终止程序，尤其是对那些临时性的错误。

偶尔有必要对某个不变量做一致性检查，并在不变量被违反时终止程序。一般来说，只有当不变量检查的失败意味着内部状态已经不可恢复时，才需要这样做。在 Google 代码库里最可靠的做法是调用 `log.Fatal`。在这些情况下使用 `panic` 不可靠，因为 deferred 函数可能死锁，或进一步破坏内部/外部状态。

同样，不要为了避免崩溃而试图 recover panic；这样做可能让受污染的状态继续传播。离 panic 越远，你就越不了解程序的状态——它可能正持有锁或其他资源。程序随后可能发展出其他意料之外的失败模式，让问题更难诊断。与其在代码里试图处理意料之外的 panic，不如使用监控工具把意外失败暴露出来，并优先修复相关 bug。

**说明：** 标准库的 [`net/http` server](https://pkg.go.dev/net/http#Server) 违反了这个建议，它会从请求处理器里 recover panic。有经验的 Go 工程师的共识是这是个历史遗留的错误。如果你去抽样其他语言应用服务器的服务器日志，常常会发现大量未处理的栈追踪。请在你的服务中避开这个坑。

### 何时使用 panic

标准库在 API 被误用时会 panic。例如 [`reflect`](https://pkg.go.dev/reflect) 在很多情况下会以 panic 的方式表示某个值被以一种暗示被误解了的方式访问。这类似于核心语言 bug（比如访问越界切片元素）所引发的 panic。代码评审和测试应该发现这类 bug，因为它们不应出现在生产代码里。这些 panic 充当不变量检查，且不依赖某个库，因为标准库没有 Google 代码库所用的 [分级别 `log`](https://google.github.io/styleguide/go/decisions#logging) 包。

另一种 panic 有用但不常见的情形是：作为包的内部实现细节，且在调用链中总有匹配的 recover。解析器和类似的深度嵌套、内部紧密耦合的函数组可以受益于这种设计：在那里铺设错误返回值会增加复杂性却没多少价值。

这种设计的关键属性是：**这些 panic 永远不允许跨越包边界逃逸**，也不构成包 API 的一部分。通常通过一个顶层的 deferred 函数来实现——它用 `recover` 把传播出来的 panic 在公共 API 边界翻译成返回的错误。它要求 panic 和 recover 的代码能区分自己主动抛出的 panic 和那些不是自己抛出的 panic：

    // Good:
    type syntaxError struct {
      msg string
    }

    func parseInt(in string) int {
      n, err := strconv.Atoi(in)
      if err != nil {
        panic(&syntaxError{"not a valid integer"})
      }
    }

    func Parse(in string) (_ *Node, err error) {
      defer func() {
        if p := recover(); p != nil {
          sErr, ok := p.(*syntaxError)
          if !ok {
            panic(p) // 把不在我们代码领域内的 panic 继续向上抛。
          }
          err = fmt.Errorf("syntax error: %v", sErr.msg)
        }
      }()
      ... // 解析输入，过程中内部调用 parseInt 来解析整数
    }

> **警告：** 使用这种模式的代码必须小心管理在 defer 管理的代码段中所关联的任何资源（例如 close、free 或 unlock）。
>
> 参见：[Go Tip #81: Avoiding Resource Leaks in API Design](https://google.github.io/styleguide/go/index.html#gotip)

当编译器无法识别出不可达代码时，也会用到 panic，例如当使用像 `log.Fatal` 这种不会返回的函数时：

    // Good:
    func answer(i int) string {
        switch i {
        case 42:
            return "yup"
        case 54:
            return "base 13, huh"
        default:
            log.Fatalf("Sorry, %d is not the answer.", i)
            panic("unreachable")
        }
    }

[在 flag 被解析之前不要调用 `log` 函数。](https://pkg.go.dev/github.com/golang/glog#pkg-overview) 如果你必须在包的初始化函数（`init` 或所谓的 [must 函数](https://google.github.io/styleguide/go/decisions#must-functions)）里"死掉"，panic 可以作为致命日志调用的替代。

另见：

*   语言规范中的 [Handling panics](https://go.dev/ref/spec#Handling_panics) 和 [Run-time Panics](https://go.dev/ref/spec#Run_time_panics)
*   [Defer, Panic, and Recover](https://go.dev/blog/defer-panic-and-recover)
*   [On the uses and misuses of panics in Go](https://eli.thegreenplace.net/2018/on-the-uses-and-misuses-of-panics-in-go/)

## 文档

### 约定

本节是对决策文档中 [注释](https://google.github.io/styleguide/go/decisions#commentary) 一节的补充。

以大家熟悉的风格写文档的 Go 代码，比注释不当或根本没有注释的代码更容易读懂、也更不容易被误用。可运行的 [示例](https://google.github.io/styleguide/go/decisions#examples) 会出现在 godoc 和代码搜索中，是展示你的代码如何使用的绝佳方式。

#### 参数和配置

并不是每个参数都要在文档里逐项列出。这适用于：

*   函数和方法参数
*   结构体字段
*   选项 API

要记录那些易出错或非显而易见的字段和参数，解释它们为什么值得关注。

在下面这段代码里，被高亮的注释对读者来说几乎没提供什么有用信息：

    // Bad:
    // Sprintf 根据格式说明符进行格式化，并返回格式化后的字符串。
    //
    // format 是格式，data 是用于插值的数据。
    func Sprintf(format string, data ...any) string

相比之下，下面这段类似情境的代码里，注释则给出了非显而易见或对读者确有助益的内容：

    // Good:
    // Sprintf 根据格式说明符进行格式化，并返回格式化后的字符串。
    //
    // 提供的 data 用于对 format 字符串进行插值。如果 data 与预期的格式动词不匹配，
    // 或者 data 的数量不满足格式规范的要求，函数会按照上文"Format errors"一节的描述，
    // 把格式错误的提示内联到输出字符串中。
    func Sprintf(format string, data ...any) string

在选择要记录什么、记录到什么深度时，请考虑你预期的读者。维护者、新加入团队的成员、外部用户，甚至六个月后的你自己，可能需要的信息会与你最初写文档时脑子里的想法略有不同。

另见：

*   [GoTip #41: Identify Function Call Parameters](https://google.github.io/styleguide/go/index.html#gotip)
*   [GoTip #51: Patterns for Configuration](https://google.github.io/styleguide/go/index.html#gotip)

#### Context

context 参数的取消会中断它所传递到的函数——这一点是隐含的。如果函数会返回错误，约定上就是 `ctx.Err()`。

这一点不需要再次说明：

    // Bad:
    // Run 执行 worker 的运行循环。
    //
    // 该方法会一直处理工作，直到 context 被取消，并相应地返回错误。
    func (Worker) Run(ctx context.Context) error

因为这是隐含的，下面这种写法更好：

    // Good:
    // Run 执行 worker 的运行循环。
    func (Worker) Run(ctx context.Context) error

如果 context 的行为有不同或者不直观，那么在以下任一情况成立时，就应当显式记录。

*   当 context 被取消时，函数返回的不是 `ctx.Err()` 的其他错误：

        // Good:
        // Run 执行 worker 的运行循环。
        //
        // 如果 context 被取消，Run 返回 nil 错误。
        func (Worker) Run(ctx context.Context) error

*   函数有其他可能中断它或影响其生命周期的机制：

        // Good:
        // Run 执行 worker 的运行循环。
        //
        // Run 会在 context 被取消或 Stop 被调用前持续处理工作。
        // 内部以异步方式处理 context 取消：run 可能在所有工作停止之前就返回。
        // Stop 方法是同步的，会等待直到运行循环中的所有操作结束。请使用 Stop
        // 来实现优雅关闭。
        func (Worker) Run(ctx context.Context) error

        func (Worker) Stop()

*   函数对 context 的生命周期、派生关系或附加值有特殊要求：

        // Good:
        // NewReceiver 开始接收发送到指定队列的消息。
        // 该 context 不应带有 deadline。
        func NewReceiver(ctx context.Context) *Receiver

        // Principal 返回发起调用一方的可读名称。
        // 该 context 必须包含由 security.NewContext 附加的值。
        func Principal(ctx context.Context) (name string, ok bool)

    **警告：** 应避免设计那些对调用者提出此类要求（比如 context 不能有 deadline）的 API。上面的例子只是为了说明在无法避免时如何记录这种情况，并不代表赞同这种模式。

#### 并发

Go 用户默认假定概念上只读的操作是并发安全的，不需要额外的同步。

下面这段 godoc 里关于并发的额外说明可以放心删掉：

    // Len 返回缓冲区中未读部分的字节数；b.Len() == len(b.Bytes())。
    //
    // 它可以被多个 goroutine 并发安全地调用。
    func (*Buffer) Len() int

而变更操作则不被假定为并发安全，需要使用者考虑同步。

同样，下面关于并发的额外说明也可以删掉：

    // Grow 增长缓冲区的容量。
    //
    // 它不可以被多个 goroutine 并发调用。
    func (*Buffer) Grow(n int)

在以下任一情况成立时，强烈鼓励加上文档。

*   操作是只读还是变更不明显：

        // Good:
        package lrucache

        // Lookup 从缓存中返回与 key 关联的数据。
        //
        // 此操作不能并发使用。
        func (*Cache) Lookup(key string) (data []byte, ok bool)

    为什么？查找 key 时命中缓存会内部变更 LRU 缓存。实现细节对所有读者来说并不一定显而易见。

*   同步由 API 提供：

        // Good:
        package fortune_go_proto

        // NewFortuneTellerClient 为 FortuneTeller 服务返回一个 *rpc.Client。
        // 它可以被多个 goroutine 同时安全使用。
        func NewFortuneTellerClient(cc *rpc.ClientConn) *FortuneTellerClient

    为什么？Stubby 提供了同步。

    **说明：** 如果 API 是一个类型且 API 整体提供同步，按惯例只在类型定义处记录这些语义。

*   API 使用用户实现类型（接口），且接口的消费方有特定的并发要求：

        // Good:
        package health

        // Watcher 报告某个实体（通常是后端服务）的健康状态。
        //
        // Watcher 的方法可以被多个 goroutine 同时安全使用。
        type Watcher interface {
            // Watch 在被监视对象的状态发生变化时，通过传入的 channel 发送 true。
            Watch(changed chan<- bool) (unwatch func())

            // Health 如果被监视的实体健康则返回 nil，否则返回一个非 nil 错误，
            // 说明实体不健康的原因。
            Health() error
        }

    为什么？API 是否能被多个 goroutine 安全使用是它契约的一部分。

#### 清理

记录 API 要求的任何显式清理动作。否则调用方不会正确使用 API，导致资源泄漏和其他可能的 bug。

标出由调用方负责的清理动作：

    // Good:
    // NewTicker 返回一个新的 Ticker，其中包含一个 channel，channel 会在每个 tick
    // 之后把当前时间发送到该 channel。
    //
    // 用完后请调用 Stop 来释放 Ticker 关联的资源。
    func NewTicker(d Duration) *Ticker

    func (*Ticker) Stop()

如果清理资源的方式可能不直观，请说明清理方式：

    // Good:
    // Get 向指定的 URL 发起一次 GET 请求。
    //
    // 当 err 为 nil 时，resp 总是包含一个非 nil 的 resp.Body。
    // 调用方在读完 resp.Body 后应自行关闭它。
    //
    //    resp, err := http.Get("http://example.com/")
    //    if err != nil {
    //      // 处理错误
    //    }
    //    defer resp.Body.Close()
    //    body, err := io.ReadAll(resp.Body)
    func (c *Client) Get(url string) (resp *Response, err error)

另见：

*   [GoTip #110: Don't Mix Exit With Defer](https://google.github.io/styleguide/go/index.html#gotip)

#### 错误

记录你的函数会返回给调用方的、重要的 sentinel 错误值或错误类型，以便调用方可以预见他们的代码能处理哪些情况。

    // Good:
    package os

    // Read 从 File 中读取最多 len(b) 个字节到 b 中。它返回读取的字节数以及
    // 任何遇到的错误。
    //
    // 在文件末尾，Read 返回 0, io.EOF。
    func (*File) Read(b []byte) (n int, err error) {

当函数返回特定的错误类型时，要正确注明错误是指针接收者还是非指针接收者：

    // Good:
    package os

    type PathError struct {
        Op   string
        Path string
        Err  error
    }

    // Chdir 把当前工作目录改为指定的目录。
    //
    // 如果有错误发生，错误将是 *PathError 类型。
    func Chdir(dir string) error {

记录返回值是指针还是非指针接收者，能让调用方用 [`errors.Is`](https://pkg.go.dev/errors#Is)、[`errors.As`](https://pkg.go.dev/errors#As) 以及 [`cmp` 包](https://pkg.go.dev/github.com/google/go-cmp/cmp) 正确比较错误。这是因为非指针值与指针值并不等价。

**说明：** 在 `Chdir` 例子中，返回类型写作 `error` 而不是 `*PathError`，原因参见 [nil 接口值的工作机制](https://go.dev/doc/faq#nil_error)。

当包内大多数错误都适用同一种行为约定时，把这个错误约定写进 [包的文档](https://google.github.io/styleguide/go/decisions#package-comments)：

    // Good:
    // Package os 提供了一个独立于平台的操作系统的接口。
    //
    // 通常，错误里会包含更多可用信息。例如，某个使用文件名的调用（比如 Open 或 Stat）
    // 失败时，打印出来的错误会包含失败的文件名，并且错误会是 *PathError 类型，
    // 可以被解包以获取更多信息。
    package os

用心地运用这些方法，可以不费太大力气就 [为错误增加额外信息](#error-extra-info)，并帮助调用方避免添加冗余的注解。

另见：

*   [Go Tip #106: Error Naming Conventions](https://google.github.io/styleguide/go/index.html#gotip)
*   [Go Tip #89: When to Use Canonical Status Codes as Errors](https://google.github.io/styleguide/go/index.html#gotip)

### 预览

Go 提供了一个 [文档服务器](https://pkg.go.dev/golang.org/x/pkgsite/cmd/pkgsite)。建议在代码评审之前和过程中，预览你的代码所生成的文档。这有助于验证 [godoc 格式](#godoc-formatting) 是否被正确渲染。

### Godoc 格式

[Godoc](https://pkg.go.dev/) 提供了一些特定的语法来 [格式化文档](https://go.dev/doc/comment)。

*   段落之间需要空一行：

        // Good:
        // LoadConfig 从指定的文件中读取配置。
        //
        // 配置文件格式的细节参见 some/shortlink。

*   测试文件可以包含 [可运行的示例](https://google.github.io/styleguide/go/decisions#examples)，它们会附加在 godoc 中相应文档的后面：

        // Good:
        func ExampleConfig_WriteTo() {
          cfg := &Config{
            Name: "example",
          }
          if err := cfg.WriteTo(os.Stdout); err != nil {
            log.Exitf("Failed to write config: %s", err)
          }
          // Output:
          // {
          //   "name": "example"
          // }
        }

*   在额外缩进两个空格的行会按原样呈现：

        // Good:
        // Update 在一个原子事务中运行该函数。
        //
        // 通常与一个匿名的 TransactionFunc 一起使用：
        //
        //   if err := db.Update(func(state *State) { state.Foo = bar }); err != nil {
        //     //...
        //   }

    但请注意，比起把代码放在注释里，把它放进可运行的示例中往往更合适。

    这种"原样"格式可以用于 godoc 原生不支持的格式，例如列表和表格：

        // Good:
        // LoadConfig 从指定的文件中读取配置。
        //
        // LoadConfig 以特殊方式处理以下键：
        //   "import" 会让该配置从指定文件继承。
        //   "env" 如果存在则会用系统环境进行填充。

*   一个单行：以大写字母开头，除括号和逗号外不含标点，且后面紧跟另一段，会被格式化为标题：

        // Good:
        // 下面的行会被格式化为一个标题。
        //
        // 使用标题
        //
        // 标题会自动生成锚点标签，便于链接。

### 突出信号

有时一行代码看起来像常见的写法，但实际上并非如此。其中一个最好的例子是 `err == nil` 的检查（因为 `err != nil` 常见得多）。下面这两种条件判断很难一眼区分：

    // Good:
    if err := doSomething(); err != nil {
        // ...
    }

    // Bad:
    if err := doSomething(); err == nil {
        // ...
    }

你可以通过加注释来"放大"条件判断中的信号：

    // Good:
    if err := doSomething(); err == nil { // 如果没有错误
        // ...
    }

注释会让读者注意到条件判断中的差异。

## 变量声明

### 初始化

为保持一致，当用一个非零值初始化新变量时，优先使用 `:=` 而不是 `var`。

    // Good:
    i := 42

    // Bad:
    var i = 42

### 用零值声明变量

下面的声明使用的是 [零值](https://golang.org/ref/spec#The_zero_value)：

    // Good:
    var (
        coords Point
        magic  [4]byte
        primes []int
    )

当你想表达一个**准备好供后续使用的**空值时，应该用零值来声明变量。使用带显式初始化的复合字面量会显得啰嗦：

    // Bad:
    var (
        coords = Point{X: 0, Y: 0}
        magic  = [4]byte{0, 0, 0, 0}
        primes = []int(nil)
    }

零值声明的一个常见用途是把变量当作反序列化时的输出：

    // Good:
    var coords Point
    if err := json.Unmarshal(data, &coords); err != nil {

如果你需要一个指针类型的变量，使用如下零值形式也是可以的：

    // Good:
    msg := new(pb.Bar) // 或 "&pb.Bar{}"
    if err := proto.Unmarshal(data, msg); err != nil {

如果你的结构体里需要一个 [不能被拷贝](https://google.github.io/styleguide/go/decisions#copying) 的锁或其他字段，你可以把它做成值类型，从而利用零值初始化的便利。但这也意味着包含它的类型必须通过指针传递，而不是值传递。该类型的方法必须使用指针接收者。

    // Good:
    type Counter struct {
        // 这个字段不必是 "*sync.Mutex"。然而，
        // 用户现在必须用 *Counter 而不是 Counter 来互相传递。
        mu   sync.Mutex
        data map[string]int64
    }

    // 注意这里必须是指针接收者，以避免被拷贝。
    func (c *Counter) IncrementBy(name string, n int64)

对于结构体和数组这样的复合类型的局部变量，即使它们包含这些不可拷贝的字段，用值类型也是可以接受的。但是，如果该复合类型由函数返回，或者对它的所有访问最终都需要取地址，那最好一开始就声明为指针类型。同样地，protobuf 消息应当声明为指针类型。

    // Good:
    func NewCounter(name string) *Counter {
        c := new(Counter) // "&Counter{}" 也可以。
        registerCounter(name, c)
        return c
    }

    var msg = new(pb.Bar) // 或 "&pb.Bar{}"。

这是因为 `*pb.Something` 满足 [`proto.Message`](https://pkg.go.dev/google.golang.org/protobuf/proto#Message)，而 `pb.Something` 不满足。

    // Bad:
    func NewCounter(name string) *Counter {
        var c Counter
        registerCounter(name, &c)
        return &c
    }

    var msg = pb.Bar{}

> **重要：** Map 类型必须显式初始化之后才能修改。但从零值 map 中读取是完全没有问题的。
>
> 对于 map 和 slice 类型，如果代码对性能特别敏感，并且你提前知道大小，请参见 [size hints](#vardeclsize) 一节。

### 复合字面量

下面是一些 [复合字面量](https://golang.org/ref/spec#Composite_literals) 声明：

    // Good:
    var (
        coords   = Point{X: x, Y: y}
        magic    = [4]byte{'I', 'W', 'A', 'D'}
        primes   = []int{2, 3, 5, 7, 11}
        captains = map[string]string{"Kirk": "James Tiberius", "Picard": "Jean-Luc"}
    )

当你已经知道初始元素或成员时，应该用复合字面量来声明值。

反过来，用复合字面量来声明空值或无成员的值，相对于 [零值初始化](#vardeclzero) 来说会显得啰嗦。

当你需要一个指向零值的指针时，有两种选择：空的复合字面量以及 `new`。两者都可以，但 `new` 关键字可以提醒读者：一旦需要非零值，复合字面量就用不了了：

    // Good:
    var (
      buf = new(bytes.Buffer) // 非空 Buffer 用构造函数初始化。
      msg = new(pb.Message) // 非空的 proto 消息用 builder 或逐字段赋值来初始化。
    )

### Size hints

下面的声明通过 size hints 来预分配容量：

    // Good:
    var (
        // 目标文件系统首选 buffer 大小：st_blksize。
        buf = make([]byte, 131072)
        // 通常每轮处理 8-10 条元素（按 16 算比较稳妥）。
        q = make([]Node, 0, 16)
        // 每个分片处理 shardSize（通常 32000+）条元素。
        seen = make(map[string]bool, shardSize)
    )

size hints 和预分配在**与对代码及其集成的经验性分析相结合**时，是构造对性能敏感、资源高效的代码的重要步骤。

大多数代码并不需要 size hint 或预分配，可以让 runtime 在需要时扩容 slice 或 map。当最终大小已知时（比如在 map 和 slice 之间转换）预分配是可以接受的，但这不是可读性方面的要求，且在规模较小时可能不值得为此增加复杂度。

**警告：** 预分配超过实际需要的内存会浪费集群内存，甚至会损害性能。拿不准时，请参见 [GoTip #3: Benchmarking Go Code](https://google.github.io/styleguide/go/index.html#gotip)，默认采用 [零值初始化](#vardeclzero) 或 [复合字面量声明](#vardeclcomposite)。

### Channel 方向

在可能的情况下明确指定 [channel 方向](https://go.dev/ref/spec#Channel_types)。

    // Good:
    // sum 计算所有值的总和。它会从 channel 中读取，直到 channel 被关闭。
    func sum(values <-chan int) int {
        // ...
    }

这能避免在没有指定方向时可能出现的随手编程错误：

    // Bad:
    func sum(values chan int) (out int) {
        for v := range values {
            out += v
        }
        // 要走到这段代码，values 必须已经被关闭，而对已关闭的 channel
        // 再调用 close 会触发 panic。
        close(values)
    }

当方向被指定时，编译器就能像上面这种简单错误一样捕获。这也有助于在类型上表达一定程度的归属感。

另见 Bryan Mills 的演讲 "Rethinking Classical Concurrency Patterns"：[slides](https://drive.google.com/file/d/1nPdvhB0PutEJzdCq5ms6UI58dp50fcAN/view?usp=sharing) [video](https://www.youtube.com/watch?v=5zXAHh5tJqQ)。

## 函数参数列表

不要让函数的签名变得过长。随着参数越来越多，每个参数的角色越来越不清晰，相邻且同类型的参数也更容易混淆。参数过多的函数更不容易记住，在调用点也更难阅读。

设计 API 时，考虑把一个签名已经变得复杂的、高度可配置的函数拆成几个更简单的函数。如果需要，它们可以共享一个（未导出的）实现。

如果某个函数需要很多输入，可以考虑为其中一部分参数引入 [option 结构](#option-structure)，或者采用更高级的 [variadic options](#variadic-options) 技术。选择哪种策略的主要考量，应该是看函数调用在所有预期使用场景下看起来怎么样。

下面的建议主要适用于导出的 API，它们的标准比未导出的 API 更高。这些技术对你的场景可能并不必要。凭你的判断，在 [清晰度](https://google.github.io/styleguide/go/guide#clarity) 和 [最少机制](https://google.github.io/styleguide/go/guide#least-mechanism) 之间做取舍。

另见：[Go Tip #24: Use Case-Specific Constructions](https://google.github.io/styleguide/go/index.html#gotip)

### Option 结构

Option 结构是一个 struct 类型，收集了某个函数或方法的部分或全部参数，然后作为最后一个参数传给该函数或方法。（仅当用于导出函数时，结构体本身才应当导出。）

使用 Option 结构有若干好处：

*   struct 字面量同时包含字段名和值，让参数自文档化、也不容易调换。
*   不相关或取默认值的字段可以省略。
*   调用方可以共享 option 结构，并编写作用于它的辅助函数。
*   struct 在每个字段上的文档比函数参数更整洁。
*   option 结构可以在不改动调用点的情况下随时间扩展。

下面是一个可以被改进的函数示例：

    // Bad:
    func EnableReplication(ctx context.Context, config *replicator.Config, primaryRegions, readonlyRegions []string, replicateExisting, overwritePolicies bool, replicationInterval time.Duration, copyWorkers int, healthWatcher health.Watcher) {
        // ...
    }

上面这个函数可以用 Option 结构重写为：

    // Good:
    type ReplicationOptions struct {
        Config              *replicator.Config
        PrimaryRegions      []string
        ReadonlyRegions     []string
        ReplicateExisting   bool
        OverwritePolicies   bool
        ReplicationInterval time.Duration
        CopyWorkers         int
        HealthWatcher       health.Watcher
    }

    func EnableReplication(ctx context.Context, opts ReplicationOptions) {
        // ...
    }

然后可以在另一个包里这样调用：

    // Good:
    func foo(ctx context.Context) {
        // 复杂调用：
        storage.EnableReplication(ctx, storage.ReplicationOptions{
            Config:              config,
            PrimaryRegions:      []string{"us-east1", "us-central2", "us-west3"},
            ReadonlyRegions:     []string{"us-east5", "us-central6"},
            OverwritePolicies:   true,
            ReplicationInterval: 1 * time.Hour,
            CopyWorkers:         100,
            HealthWatcher:       watcher,
        })

        // 简单调用：
        storage.EnableReplication(ctx, storage.ReplicationOptions{
            Config:         config,
            PrimaryRegions: []string{"us-east1", "us-central2", "us-west3"},
        })
    }

**说明：** [Context 永远不应该被放进 option 结构里](https://google.github.io/styleguide/go/decisions#contexts)。

当以下条件中的一些成立时，通常优先选用这种 Option 结构：

*   所有调用方都需要指定其中一个或多个选项。
*   大量调用方需要提供许多选项。
*   选项在多个用户会调用的函数之间共享。

### Variadic options

使用 variadic options，会创建一批导出函数，它们返回闭包，这些闭包可以传给函数的 [variadic（`...`） 参数](https://golang.org/ref/spec#Passing_arguments_to_..._parameters)。函数以选项的值（如果有）作为参数，返回的闭包接收一个可变引用（通常是指向某个 struct 类型的指针），并基于输入去更新它。

使用 variadic options 有若干好处：

*   不需要配置时，调用点不占空间。
*   选项本身仍然是值，调用方可以共享、编写辅助函数、累积。
*   选项可以接受多个参数（例如 `cartesian.Translate(dx, dy int) TransformOption`）。
*   option 函数可以返回命名类型，把选项在 godoc 里归到一起。
*   包可以允许（或阻止）第三方包自定义选项。

**说明：** 使用 variadic options 需要写大量额外的代码（见下面的示例），所以只有当收益大于代价时才应采用。

下面是一个可以被改进的函数示例：

    // Bad:
    func EnableReplication(ctx context.Context, config *placer.Config, primaryCells, readonlyCells []string, replicateExisting, overwritePolicies bool, replicationInterval time.Duration, copyWorkers int, healthWatcher health.Watcher) {
      ...
    }

上面的示例可以用 variadic options 重写为：

    // Good:
    type replicationOptions struct {
        readonlyCells       []string
        replicateExisting   bool
        overwritePolicies   bool
        replicationInterval time.Duration
        copyWorkers         int
        healthWatcher       health.Watcher
    }

    // A ReplicationOption configures EnableReplication.
    type ReplicationOption func(*replicationOptions)

    // ReadonlyCells adds additional cells that should additionally
    // contain read-only replicas of the data.
    //
    // Passing this option multiple times will add additional
    // read-only cells.
    //
    // Default: none
    func ReadonlyCells(cells ...string) ReplicationOption {
        return func(opts *replicationOptions) {
            opts.readonlyCells = append(opts.readonlyCells, cells...)
        }
    }

    // ReplicateExisting controls whether files that already exist in the
    // primary cells will be replicated.  Otherwise, only newly-added
    // files will be candidates for replication.
    //
    // Passing this option again will overwrite earlier values.
    //
    // Default: false
    func ReplicateExisting(enabled bool) ReplicationOption {
        return func(opts *replicationOptions) {
            opts.replicateExisting = enabled
        }
    }

    // ... other options ...

    // DefaultReplicationOptions control the default values before
    // applying options passed to EnableReplication.
    var DefaultReplicationOptions = []ReplicationOption{
        OverwritePolicies(true),
        ReplicationInterval(12 * time.Hour),
        CopyWorkers(10),
    }

    func EnableReplication(ctx context.Context, config *placer.Config, primaryCells []string, opts ...ReplicationOption) {
        var options replicationOptions
        for _, opt := range DefaultReplicationOptions {
            opt(&options)
        }
        for _, opt := range opts {
            opt(&options)
        }
    }

然后可以在另一个包里这样调用：

    // Good:
    func foo(ctx context.Context) {
        // 复杂调用：
        storage.EnableReplication(ctx, config, []string{"po", "is", "ea"},
            storage.ReadonlyCells("ix", "gg"),
            storage.OverwritePolicies(true),
            storage.ReplicationInterval(1*time.Hour),
            storage.CopyWorkers(100),
            storage.HealthWatcher(watcher),
        )

        // 简单调用：
        storage.EnableReplication(ctx, config, []string{"po", "is", "ea"})
    }

当以下多数条件成立时，优先选用这种 Option：

*   多数调用方不需要指定任何选项。
*   多数选项很少被用到。
*   选项数量很多。
*   选项需要参数。
*   选项可能会失败或被错误设置（这种情况下 option 函数返回 `error`）。
*   选项需要大量文档，难以全部塞进 struct 里。
*   用户或其他包可以提供自定义选项。

这种风格的选项应该接受参数，而不是通过"是否出现"来传达值；后者会让参数的动态组合变得困难得多。例如，二元开关应该接受一个布尔参数（如 `rpc.FailFast(enable bool)` 优于 `rpc.EnableFailFast()`）；枚举型选项应该接受一个枚举常量（如 `log.Format(log.Capacitor)` 优于 `log.CapacitorFormat()`）。否则，那些必须以编程方式选择传入哪些选项的用户将会被迫修改参数的实际构成，而不是仅仅修改选项的参数值。不要假定所有用户都会静态地知道完整的选项集。

一般来说，选项应当按顺序处理。如果出现冲突，或者一个不可累积的选项被传入多次，最后一个参数应该胜出。

在这种模式下，option 函数的参数通常是不导出的，以把选项的定义限定在包内部。这是个不错的默认值，尽管有些时候允许其他包定义选项也是合理的。

更深入的讨论参见 [Rob Pike 的原始博客文章](http://commandcenter.blogspot.com/2014/01/self-referential-functions-and-design.html) 和 [Dave Cheney 的演讲](https://dave.cheney.net/2014/10/17/functional-options-for-friendly-apis)。

## 复杂的命令行接口

一些程序希望给用户提供包含子命令的丰富命令行界面。例如 `kubectl create`、`kubectl run` 以及其他众多子命令都是由 `kubectl` 这个程序提供的。在 Go 中实现这一点至少有下面这些常用库。

如果你没有偏好，或者其他条件相当，推荐使用 [subcommands](https://pkg.go.dev/github.com/google/subcommands)，因为它最简单，也最不容易用错。不过，如果你需要它没有的某些特性，可以在其他选项中挑选。

*   **[cobra](https://pkg.go.dev/github.com/spf13/cobra)**
    *   flag 风格：getopt
    *   在 Google 代码库之外常用。
    *   提供了许多额外的功能。
    *   使用上有一些坑（见下）。
*   **[subcommands](https://pkg.go.dev/github.com/google/subcommands)**
    *   flag 风格：Go
    *   简单且容易用对。
    *   不需要额外功能时推荐。

**警告**：cobra 的命令函数应该用 `cmd.Context()` 获取 context，而不是用 `context.Background` 自己创建一个根 context。使用 subcommands 包的代码会直接以参数的形式收到正确的 context。

你不必把每个子命令都放在独立的包里，通常也不需要这么做。对包边界的判断与在任何 Go 代码库中是一致的。如果你的代码既能作为库使用，也能作为二进制使用，那么把 CLI 代码和库分离开通常是有益的，让 CLI 只是它的众多客户端之一。（这并不是有子命令的 CLI 独有的，但在这里提到是因为它经常出现。）

## 测试

### 把测试断言留给 `Test` 函数

Go 区分 "test helpers"（测试辅助）和 "assertion helpers"（断言辅助）：

*   **Test helpers**（测试辅助）是执行 setup 或 cleanup 任务的函数。在测试辅助中发生的所有失败都应当是环境层面的失败（而非被测代码的失败）——例如测试数据库因为本机没有空闲端口而无法启动。对于这类函数，调用 `t.Helper` 来 [标记它们是测试辅助](https://google.github.io/styleguide/go/decisions#mark-test-helpers) 通常是合适的。详见 [测试辅助中的错误处理](#test-helper-error-handling)。

*   **Assertion helpers**（断言辅助）是检查系统正确性，并在期望不满足时让测试失败的函数。断言辅助在 Go 中 [不被认为是惯用做法](https://google.github.io/styleguide/go/decisions#assert)。

测试的目的是报告被测代码的通过/失败情况。最佳的失败位置是 `Test` 函数内部，因为这样能保证 [失败消息](https://google.github.io/styleguide/go/decisions#useful-test-failures) 和测试逻辑都很清晰。

随着测试代码的增长，可能有必要把一些功能抽取成单独的函数。标准的软件工程考量仍然适用，因为 *测试代码也是代码*。如果该功能与测试框架无关，那么通常的所有规则都适用。当公共代码与框架交互时，必须小心，避免那些会导致失败消息信息不足、测试难以维护的常见陷阱。

如果很多独立的测试用例需要同样的校验逻辑，请用以下方式之一来组织测试，而不是使用 assertion helper 或复杂的校验函数：

*   把逻辑（校验和失败）都内联在 `Test` 函数里，即便有重复。在简单情况下这是最合适的。
*   如果输入相似，可以把它们统一成一个 [表驱动测试](https://google.github.io/styleguide/go/decisions#table-driven-tests)，同时把逻辑内联在循环里。这能避免重复，又把校验和失败保留在 `Test` 里。
*   如果有多个调用者需要同一个校验函数，但表驱动测试又不合适（通常是因为输入不够简单，或者校验是某个操作序列的一部分），那么把校验函数设计成返回一个值（通常是 `error`），而不是接收 `testing.T` 参数并用它让测试失败。在 `Test` 函数内部通过逻辑判断是否失败，并提供 [有用的测试失败消息](https://google.github.io/styleguide/go/decisions#useful-test-failures)。你也可以创建 test helpers 来抽取那些通用的样板式 setup 代码。

最后一种思路的设计保持了正交性。例如，[`cmp` 包](https://pkg.go.dev/github.com/google/go-cmp/cmp) 并不是设计用来让测试失败的，而是用来比较（以及 diff）值的。因此它不需要知道比较发生的上下文，因为调用方可以提供这些。如果你的通用测试代码为你的数据类型提供了一个 `cmp.Transformer`，那通常就是最简单的设计。对于其他校验，考虑返回一个 `error` 值。

    // Good:
    // polygonCmp 返回一个 cmp.Option，用于在一定的浮点误差范围内比较 s2 几何对象。
    func polygonCmp() cmp.Option {
        return cmp.Options{
            cmp.Transformer("polygon", func(p *s2.Polygon) []*s2.Loop { return p.Loops() }),
            cmp.Transformer("loop", func(l *s2.Loop) []s2.Point { return l.Vertices() }),
            cmpopts.EquateApprox(0.00000001, 0),
            cmpopts.EquateEmpty(),
        }
    }

    func TestFenceposts(t *testing.T) {
        // 这是一个针对虚构函数 Fenceposts 的测试，它会在某个 Place 对象周围画一圈篱笆。
        // 具体细节不重要，重要的是结果是一个含有 s2 几何的对象
        // （github.com/golang/geo/s2）。
        got := Fencepost(tomsDiner, 1*meter)
        if diff := cmp.Diff(want, got, polygonCmp()); diff != "" {
            t.Errorf("Fencepost(tomsDiner, 1m) returned unexpected diff (-want+got):\n%v", diff)
        }
    }

    func FuzzFencepost(f *testing.F) {
        // 针对上述函数的 fuzz 测试（https://go.dev/doc/fuzz）。

        f.Add(tomsDiner, 1*meter)
        f.Add(school, 3*meter)

        f.Fuzz(func(t *testing.T, geo Place, padding Length) {
            got := Fencepost(geo, padding)
            // 简单的参考实现：不在生产中使用，但易于推理，因此在随机测试中
            // 适合作为对照。
            reference := slowFencepost(geo, padding)

            // 在 fuzz 测试中，输入和输出可能很大，所以不必打印 diff。
            // cmp.Equal 就够了。
            if !cmp.Equal(got, reference, polygonCmp()) {
                t.Errorf("Fencepost returned wrong placement")
            }
        })
    }

`polygonCmp` 函数对调用方式是无所谓的：它既不接收具体的输入类型，也不会规定当两个对象不匹配时该怎么处理。因此，更多调用方都可以使用它。

**说明：** 测试辅助与普通的库代码之间存在类比。库代码通常[不应该 panic](https://google.github.io/styleguide/go/decisions#dont-panic)，除非极少数情况；从测试里调用的代码也不应该让测试停下来，除非[继续下去没有意义](#t-fatal)。

### 设计可扩展的校验 API

风格指南中关于测试的大多数建议都是关于如何测试你自己的代码。本节是关于如何为其他人提供设施，以便他们测试自己写的代码，从而确保代码符合你的库的要求。

#### 验收测试

这种测试被称为 [验收测试](https://en.wikipedia.org/wiki/Acceptance_testing)。这种测试的前提是：使用该测试的人并不知道测试内部发生的每一个细节；他们只是把输入交给测试设施，让它来完成工作。这可以被看作是一种 [控制反转](https://en.wikipedia.org/wiki/Inversion_of_control)。

在典型的 Go 测试中，测试函数控制程序流程，[不使用 assert](https://google.github.io/styleguide/go/decisions#assert) 和 [测试函数](#test-functions) 的指引也鼓励你保持这种方式。本节将解释如何以一种符合 Go 风格的方式来编写支持这些测试的设施。

在深入了解怎么做之前，先看一个 [`io/fs`](https://pkg.go.dev/io/fs) 中的例子，节选如下：

    type FS interface {
        Open(name string) (File, error)
    }

尽管 `fs.FS` 已经有一些知名实现，但 Go 开发者仍可能需要编写一个。为了帮助校验用户实现的 `fs.FS` 是否正确，[`testing/fstest`](https://pkg.go.dev/testing/fstest) 中提供了一个通用库，叫做 [`fstest.TestFS`](https://pkg.go.dev/testing/fstest#TestFS)。这个 API 把实现当作一个黑盒，以确保它满足 `io/fs` 契约的最基本部分。

#### 编写验收测试

现在我们知道了什么是验收测试以及为什么你可能需要它，下面我们一起看看如何为一个 `package chess`（用来模拟国际象棋对局的包）构建一个验收测试。`chess` 的用户被期望实现 `chess.Player` 接口。这些实现是我们要验证的主要对象。我们的验收测试关心的是玩家的实现是否走出合法的着法，而不是着法是否高明。

1.  为校验行为新建一个包，习惯上是在原包名后追加 `test`（例如 `chesstest`），命名规则参见 [创建测试辅助包](#naming-doubles-helper-package)。

2.  创建执行校验的函数，接收被测实现作为参数并运行它：

        // ExercisePlayer 在单个回合中针对一个棋盘测试一个 Player 实现。
        // 棋盘本身会被抽查其合理性和正确性。
        //
        // 如果 player 在给定棋盘上下文中走出合法的一步，函数返回 nil 错误。
        // 否则 ExercisePlayer 返回本包的一个错误，以指明 player 是如何
        // 以及为什么未能通过校验。
        func ExercisePlayer(b *chess.Board, p chess.Player) error

    测试应当说明哪些不变量被破坏以及是怎么破坏的。你的设计可以在两种失败报告方式之间选择：

    *   **快速失败**：一旦实现违反了不变量，立即返回一个错误。

        这是最简单的方式，如果验收测试预期运行得很快，这种方式很合适。这里可以方便地使用简单的 [sentinel](https://google.github.io/styleguide/go/index.html#gotip) 和 [自定义类型](https://google.github.io/styleguide/go/index.html#gotip)，反过来也让对验收测试的测试变得简单。

            for color, army := range b.Armies {
                // 将帅永远不应离开棋盘，因为游戏在将死时结束。
                if army.King == nil {
                    return &MissingPieceError{Color: color, Piece: chess.King}
                }
            }

    *   **聚合所有失败**：收集所有失败，一并报告。

        这种方式在感觉上类似于 [keep going](https://google.github.io/styleguide/go/decisions#keep-going) 指引，当验收测试预期运行得较慢时可能更可取。

        你如何聚合失败，取决于你是否希望给用户（或你自己）能力去逐个探查各个失败（例如为了测试你的验收测试）。下面演示使用一个 [自定义错误类型](https://google.github.io/styleguide/go/index.html#gotip) 来 [聚合错误](https://google.github.io/styleguide/go/index.html#gotip)：

            var badMoves []error

            move := p.Move()
            if putsOwnKingIntoCheck(b, move) {
                badMoves = append(badMoves, PutsSelfIntoCheckError{Move: move})
            }

            if len(badMoves) > 0 {
                return SimulationError{BadMoves: badMoves}
            }
            return nil

    验收测试应当遵循 [keep going](https://google.github.io/styleguide/go/decisions#keep-going) 指引：除非检测到被测系统的不变量被破坏，否则不应调用 `t.Fatal`。

    例如，`t.Fatal` 应像往常一样留给类似 [setup 失败](#test-helper-error-handling) 这种特殊情况：

        func ExerciseGame(t *testing.T, cfg *Config, p chess.Player) error {
            t.Helper()

            if cfg.Simulation == Modem {
                conn, err := modempool.Allocate()
                if err != nil {
                    t.Fatalf("No modem for the opponent could be provisioned: %v", err)
                }
                t.Cleanup(func() { modempool.Return(conn) })
            }
            // 运行验收测试（一整局棋）。
        }

    这种技术可以帮助你编写简洁、规范的校验。但不要试图用它来绕过 [关于 assertion 的指引](https://google.github.io/styleguide/go/decisions#assert)。

    最终交付给终端用户的代码应该类似下面这样：

        // Good:
        package deepblue_test

        import (
            "chesstest"
            "deepblue"
        )

        func TestAcceptance(t *testing.T) {
            player := deepblue.New()
            err := chesstest.ExerciseGame(t, chesstest.SimpleGame, player)
            if err != nil {
                t.Errorf("Deep Blue player failed acceptance test: %v", err)
            }
        }

### 使用真实的传输

在测试组件集成时，尤其是在组件之间使用 HTTP 或 RPC 作为底层传输的场景下，优先使用真实的底层传输来连接后端的测试版本。

例如，假设你要测试的代码（有时称为"被测系统"或 SUT）会与实现了 [long running operations](https://pkg.go.dev/google.golang.org/genproto/googleapis/longrunning) API 的后端交互。为了测试你的 SUT，请使用一个真实的 [OperationsClient](https://pkg.go.dev/google.golang.org/genproto/googleapis/longrunning#OperationsClient)，让它连接到一个 [测试替身](https://abseil.io/resources/swe-book/html/ch13.html#basic_concepts)（例如 mock、stub 或 fake）形式的 [OperationsServer](https://pkg.go.dev/google.golang.org/genproto/googleapis/longrunning#OperationsServer)。

推荐这样做而非手写一个客户端，原因是要正确模拟客户端行为是复杂的。使用生产客户端配上一个针对测试的服务器，能确保你的测试尽可能多地用到真实的代码。

**提示：** 在可能的情况下，请使用被测服务作者提供的测试库。

### `t.Error` vs. `t.Fatal`

如 [决策](https://google.github.io/styleguide/go/decisions#keep-going) 中所讨论的，测试一般不应当在遇到第一个问题时立刻中止。

然而，有些情况下测试必须中止。当某些 setup 失败时，尤其是在 [测试 setup helper](#test-helper-error-handling) 中，调用 `t.Fatal` 是合适的，没有它你就无法跑剩下的测试。在表驱动测试中，`t.Fatal` 适合用在测试循环之前、为整个测试函数做 setup 的失败上。影响测试表中某一条目的失败，使得该条目无法继续下去，应当按如下方式上报：

*   如果你没有使用 `t.Run` 子测试，用 `t.Error` 后跟 `continue` 语句，进入下一条测试表条目。
*   如果你使用了子测试（且你在 `t.Run` 调用内部），用 `t.Fatal`，它会结束当前子测试，让测试继续进入下一个子测试。

**警告：** 调用 `t.Fatal` 及类似函数并不总是安全的。详见 [这里](#t-fatal-goroutine)。

### 测试辅助中的错误处理

**说明：** 本节讨论的 [测试辅助](https://google.github.io/styleguide/go/decisions#mark-test-helpers) 是 Go 意义下的：执行测试 setup 和 cleanup 的函数，而不是通用的 assertion 工具。详见 [测试函数](#test-functions) 一节。

测试辅助执行的操作有时会失败。例如，在一个目录里 setup 一批文件涉及 I/O，可能失败。当测试辅助失败时，它们的失败通常意味着测试无法继续，因为某个 setup 前置条件没有满足。发生这种情况时，倾向于在该 helper 内调用 `Fatal` 系列函数之一：

    // Good:
    func mustAddGameAssets(t *testing.T, dir string) {
        t.Helper()
        if err := os.WriteFile(path.Join(dir, "pak0.pak"), pak0, 0644); err != nil {
            t.Fatalf("Setup failed: could not write pak0 asset: %v", err)
        }
        if err := os.WriteFile(path.Join(dir, "pak1.pak"), pak1, 0644); err != nil {
            t.Fatalf("Setup failed: could not write pak1 asset: %v", err)
        }
    }

相比让 helper 把错误返回给测试本身，这种做法让调用端更整洁：

    // Bad:
    func addGameAssets(t *testing.T, dir string) error {
        t.Helper()
        if err := os.WriteFile(path.Join(d, "pak0.pak"), pak0, 0644); err != nil {
            return err
        }
        if err := os.WriteFile(path.Join(d, "pak1.pak"), pak1, 0644); err != nil {
            return err
        }
        return nil
    }

**警告：** 调用 `t.Fatal` 及类似函数并不总是安全的。详见 [这里](#t-fatal-goroutine)。

失败消息应当包含对所发生情况的描述。这一点很重要，因为当你为很多用户提供测试 API 时尤其如此，特别是当 helper 中产生错误的步骤增多时。当测试失败时，用户应当知道在哪里、为什么失败。

**提示：** Go 1.14 引入了一个 [`t.Cleanup`](https://pkg.go.dev/testing#T.Cleanup) 函数，可以用来注册测试完成时运行的清理函数。该函数同样适用于测试辅助。关于如何简化测试辅助的指引，参见 [GoTip #4: Cleaning Up Your Tests](https://google.github.io/styleguide/go/index.html#gotip)。

下面这段放在一个假想的 `paint_test.go` 文件里的代码，演示了 `(*testing.T).Helper` 在 Go 测试中如何影响失败报告：

    package paint_test

    import (
        "fmt"
        "testing"
    )

    func paint(color string) error {
        return fmt.Errorf("no %q paint today", color)
    }

    func badSetup(t *testing.T) {
        // 这里应该调用 t.Helper，但没调用。
        if err := paint("taupe"); err != nil {
            t.Fatalf("Could not paint the house under test: %v", err) // 第 15 行
        }
    }

    func goodSetup(t *testing.T) {
        t.Helper()
        if err := paint("lilac"); err != nil {
            t.Fatalf("Could not paint the house under test: %v", err)
        }
    }

    func TestBad(t *testing.T) {
        badSetup(t)
        // ...
    }

    func TestGood(t *testing.T) {
        goodSetup(t) // 第 32 行
        // ...
    }

下面是运行时的输出示例。注意高亮的文本以及它们之间的差异：

    === RUN   TestBad
        paint_test.go:15: Could not paint the house under test: no "taupe" paint today
    --- FAIL: TestBad (0.00s)
    === RUN   TestGood
        paint_test.go:32: Could not paint the house under test: no "lilac" paint today
    --- FAIL: TestGood (0.00s)
    FAIL

`paint_test.go:15` 的错误指向 `badSetup` 内部失败的那一行：

`t.Fatalf("Could not paint the house under test: %v", err)`

而 `paint_test.go:32` 则指向 `TestGood` 里失败的那一行：

`goodSetup(t)`

在以下情况下，正确使用 `(*testing.T).Helper` 能更好地把失败归因到合适的位置：

*   helper 函数变得复杂
*   helper 函数相互调用
*   测试函数中对 helper 的使用越来越多

**提示：** 如果 helper 调用了 `(*testing.T).Error` 或 `(*testing.T).Fatal`，请在格式串里提供一些上下文，便于判断发生了什么、为什么。

**提示：** 如果 helper 所做的事不可能让测试失败，那它就不需要调用 `t.Helper`。可以从函数签名里去掉 `t`，让签名更简洁。

### 不要在独立的 goroutine 里调用 `t.Fatal`

正如 [testing 包的文档](https://pkg.go.dev/testing#T) 所述，在任何非运行 Test 函数（或子测试）的 goroutine 里调用 `t.FailNow`、`t.Fatal` 等都是不正确的。如果你的测试会启动新 goroutine，这些 goroutine 不能在其中调用这些函数。

[Test helpers](#test-functions) 通常不会从新 goroutine 中报告失败，因此它们使用 `t.Fatal` 是没有问题的。如果拿不准，就调用 `t.Error` 并 return。

    // Good:
    func TestRevEngine(t *testing.T) {
        engine, err := Start()
        if err != nil {
            t.Fatalf("Engine failed to start: %v", err)
        }

        num := 11
        var wg sync.WaitGroup
        wg.Add(num)
        for i := 0; i < num; i++ {
            go func() {
                defer wg.Done()
                if err := engine.Vroom(); err != nil {
                    // 这里不能使用 t.Fatalf。
                    t.Errorf("No vroom left on engine: %v", err)
                    return
                }
                if rpm := engine.Tachometer(); rpm > 1e6 {
                    t.Errorf("Inconceivable engine rate: %d", rpm)
                }
            }()
        }
        wg.Wait()

        if seen := engine.NumVrooms(); seen != num {
            t.Errorf("engine.NumVrooms() = %d, want %d", seen, num)
        }
    }

给测试或子测试添加 `t.Parallel` 并不会让调用 `t.Fatal` 变得不安全。

当所有 `testing` API 的调用都在 [测试函数](#test-functions) 内时，通常很容易发现这种错误用法，因为 `go` 关键字一目了然。把 `testing.T` 参数传来传去会让追踪这种用法变得更难。通常传递这些参数的理由是引入测试 helper，而测试 helper 不应依赖于被测系统。因此，如果一个测试 helper [登记了一个致命测试失败](#test-helper-error-handling)，它能够也应该在测试的 goroutine 里登记。

### 在 struct 字面量中使用字段名

在表驱动测试中，初始化测试用例 struct 字面量时，倾向于显式指定字段名。这对未来的维护很有帮助：如果维护者给测试用例 struct 增加或删除了字段，使用键名字面量的测试用例会继续通过编译，而位置字面量则会失败。

此外，使用键名字面量后，容易追踪每个字段对应表里的哪一项。

```go
// Bad:
tests := []struct {
    name           string
    expectedResult string
}{
    {"foo", "bar"},
    {"baz", "qux"},
}
```

```go
// Good:
tests := []struct {
    name           string
    expectedResult string
}{
    {name: "foo", expectedResult: "bar"},
    {name: "baz", expectedResult: "qux"},
}
```

### 表驱动测试

当许多测试用例只在少量输入参数和期望输出值上有差异时，使用表驱动测试。这能让测试更易读、减少重复。例如：

```go
// Good:
func TestParseConfig(t *testing.T) {
    tests := []struct {
        name      string
        input     string
        wantErr   bool
        wantValue string
    }{
        {
            name:      "valid input",
            input:     "key=value",
            wantErr:   false,
            wantValue: "value",
        },
        {
            name:    "missing separator",
            input:   "keyvalue",
            wantErr: true,
        },
    }

    for _, tc := range tests {
        t.Run(tc.name, func(t *testing.T) {
            got, err := ParseConfig(tc.input)
            if (err != nil) != tc.wantErr {
                t.Errorf("ParseConfig(%q) error = %v, wantErr = %v", tc.input, err, tc.wantErr)
            }
            if !tc.wantErr && got != tc.wantValue {
                t.Errorf("ParseConfig(%q) = %q, want %q", tc.input, got, tc.wantValue)
            }
        })
    }
}
```

### 用 `t.Run` 创建子测试

使用 `t.Run` 创建子测试。子测试让从命令行运行指定用例更方便，也提供了隔离，使得一个子测试失败不会阻止其他子测试继续运行。

```go
// Good:
for _, tc := range tests {
    t.Run(tc.name, func(t *testing.T) {
        // 测试体
    })
}
```

### 并行测试

当子测试相互独立、可以并发运行时，使用 `t.Parallel()`。把测试标记为并行后，Go 测试运行器就能把它和其他并行测试一起并发执行，能显著缩短测试运行时间。

```go
// Good:
for _, tc := range tests {
    tc := tc
    t.Run(tc.name, func(t *testing.T) {
        t.Parallel()
        // 测试体
    })
}
```

注意 `tc := tc` 这种遮蔽写法，它是在 goroutine 间正确捕获循环变量所必需的。

### 测试辅助

用 `t.Helper()` 标记执行测试 setup 的函数。这会让失败消息报告调用方的位置，而不是 helper 内部的那一行，让调试更轻松。

```go
// Good:
func setupTestDB(t *testing.T) *sql.DB {
    t.Helper()
    db, err := sql.Open("sqlite3", ":memory:")
    if err != nil {
        t.Fatalf("failed to open test database: %v", err)
    }
    t.Cleanup(func() { db.Close() })
    return db
}
```

### 测试发现

测试应当与它要验证的代码放在同一个包里。如果测试需要访问未导出的标识符，把它放在同一个包里。否则，把它放在 `_test` 包里（例如 `package foo_test`）。

```go
// Good:
package foo_test

import "path/to/foo"

func TestFoo(t *testing.T) {
    // ...
}
```

### 避免测试中的全局状态

测试不应当依赖全局可变状态。使用依赖注入或显式传递状态，让测试是确定性的、易于独立运行。

```go
// Bad:
var defaultClient *http.Client

func TestFetch(t *testing.T) {
    resp, err := defaultClient.Get("http://example.com")
    // ...
}
```

```go
// Good:
func TestFetch(t *testing.T) {
    client := &http.Client{Timeout: 5 * time.Second}
    resp, err := client.Get("http://example.com")
    // ...
}
```
