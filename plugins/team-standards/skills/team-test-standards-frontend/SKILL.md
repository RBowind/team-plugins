---
name: team-test-standards-frontend
description: 团队前端测试与 review 规范。写前端测试、补用例、自查或 review 前端代码改动时使用，让 AI 写出的测试对齐团队口径。测试奖杯模型：单元（Vitest）、组件集成（Testing Library + MSW）、e2e（Playwright）、sddspec 回链。后端测试用 team-test-standards-backend。
---

# 团队前端测试与 review 规范

## 测试怎么写

- 新功能和 bug 修复必须带测试，测试跟代码同一个 PR 提交。
- 一个用例只断言一件事，用例名直接说清用户场景和预期，例：`提交失败时显示错误提示`，不写 `test1`。
- 不许 mock 被测组件本身；只许 mock 网络层（MSW）和浏览器 API。
- bug 修复先写复现测试再改代码，测试红了改，绿了才算修完。
- 测用户行为，不测实现细节：不断言组件内部 state，不数渲染次数，不依赖 DOM 结构。
- 不追覆盖率数字，信心优先；快照测试慎用，只用于输出真正稳定的场景。

## 测试分层（测试奖杯）

集成测试是主力层，不是 e2e，也不是单测。

| 层 | 工具 | 写什么 |
|---|---|---|
| 静态分析 | tsc / ESLint | 类型和语法兜底，CI 必跑 |
| 单元测试 | Vitest | 只测纯函数：工具函数、转换、状态逻辑 |
| 组件集成（主力） | Testing Library + MSW | 组件/页面级：渲染 → 交互 → 断言可见变化 |
| E2E | Playwright | 只测关键用户旅程（登录、下单），真浏览器 |

## 从 spec 出发

1. 先读 `specs/<capability>/spec.md` 和 feature 目录下的 sprint contract。找不到 spec 就先问这个测试对应哪个 capability，不凭空写。
2. spec 的 Scenario 和 contract 的 B 编号 1:1。每个 B 编号必须落到恰好一个用例，不多不少。
3. 每个用例上方写回链注释：`// spec: B1`。spec 改了，测试跟着改；不允许出现无回链的游离用例。

## 组件集成测试写法（主力层）

查询优先级：`getByRole` > `getByLabelText` > `getByText` > `getByTestId`。禁止 `querySelector('.class')` 这类按样式选择器的查法。

交互用 `user-event`（模拟真实点击/输入），不用 `fireEvent` 裸事件。

网络请求统一走 MSW 拦截，不 mock fetch 本身、不 mock 组件内的数据层：

```tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from 'test/mocks/server'

it('提交失败时显示错误提示', () => { // spec: B3
  server.use(
    http.post('/api/orders', () => HttpResponse.json(
      { message: '库存不足' }, { status: 409 },
    )),
  )
  render(<OrderForm />)

  const user = userEvent.setup()
  await user.click(screen.getByRole('button', { name: '提交订单' }))

  expect(screen.getByRole('alert')).toHaveTextContent('库存不足')
})
```

断言的是用户看得见的变化（文案、可见性、跳转），不是组件内部状态。

## E2E 写法（Playwright）

- 打真实后端 + 确定性 seed 数据，不 stub 数据链路。这是前端对应后端"数据库不许 mock"的规则。
- 只覆盖关键用户旅程；每个旅程独立，不依赖其他用例的残留状态。
- flaky 测试隔离出来修，不许靠重试硬扛进 CI。

```ts
test('登录后能下单成功', async ({ page }) => { // spec: B1
  await page.goto('/login')
  await page.getByLabel('用户名').fill('buyer-test')
  await page.getByLabel('密码').fill('S3cret-pass!')
  await page.getByRole('button', { name: '登录' }).click()
  // ... 下单流程，断言订单页可见订单号
})
```

## 提交前自查（AI 每次改完代码过一遍）

1. 测试跑过且全绿，命令以项目 README 里写的为准。
2. 改动没有越出任务声明的文件范围；越界了就停下来说明。
3. 新增依赖、环境变量、配置项，在改动说明里单列出来。
4. 接口改动（参数、返回、错误码）在改动说明里标"接口变更"，reviewer 重点看。
5. 新写的测试已按 spec B 编号回链。

## review 口径（人 review AI 改动时按这个查）

- 先看测试有没有真的覆盖改动，再看实现。
- AI 自己说"已完成"不算数，以测试和运行结果为准。
- 涉及金额、权限、删除数据的代码，必须人工逐行看，AI 不能自己合入。
- 测试 review 对照 spec 查：B 编号是否全覆盖。
- 查实现细节测试：有没有断言内部 state、按 class 选择器、数渲染次数，有就打回。
