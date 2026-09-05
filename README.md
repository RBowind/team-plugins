# born-team 插件库

团队的 Claude Code 插件库：规范打成 skills，高频动作打成 commands，随 git 分发，评审后合并。所有人装同一个 marketplace，本地就是同一套配置。

装完后 AI 干活的默认行为变了：写代码过编码规范（含安全红线），动结构走架构规范，写测试 review 走测试规范，写 Go 代码过 godev，大改动先出 techspec / sddspec，开发用 `/team-standards:devloop` 按 contract 逐条交付（测试先行、独立评审、绿灯收敛），提测用 `/team-standards:test-ready`。

复杂 feature 的完整链路：techspec → sddspec（人审放行出 APPROVED 的 sprint contract）→ `/team-standards:devloop`（循环到全绿 + mutation 验收）→ `/team-standards:test-ready`（出口人工检查）。

## 目录结构

```
team-plugins/
├── .claude-plugin/
│   └── marketplace.json        # 市场清单：声明这个库里有哪些插件
├── plugins/
│   └── team-standards/         # 一个插件
│       ├── .claude-plugin/
│       │   └── plugin.json     # 插件清单
│       ├── skills/
│       │   ├── team-code-standards/
│       │   │   └── SKILL.md    # 编码规范（含安全红线）：命名、结构、错误处理、格式 + 凭据、注入、权限、数据、供应链
│       │   ├── team-architecture-standards/
│       │   │   └── SKILL.md    # 架构规范（Go）：分层口径、层间契约、改动范围、数据模型、选型
│       │   ├── team-test-standards-backend/
│       │   │   └── SKILL.md    # 后端测试与 review 规范（Go：ginkgo、sddspec 回链、mutation testing）
│       │   ├── team-test-standards-frontend/
│       │   │   └── SKILL.md    # 前端测试与 review 规范（Vitest、Testing Library、Playwright）
│       │   ├── godev/
│       │   │   ├── SKILL.md    # Go 开发规范：Google Go Style + 团队加码；现代 Go 惯用法引用 JetBrains 官方插件
│       │   │   └── references/ # guide / decisions / best-practices 中文化
│       │   ├── techspec/
│       │   │   ├── SKILL.md    # PRD → techspec（带 references/canon、reviewer）
│       │   │   └── references/
│       │   └── sddspec/
│       │       ├── SKILL.md    # PRD + techspec → 行为契约 spec（带 references/canon、evaluator）
│       │       └── references/
│       ├── commands/
│       │   ├── test-ready.md    # /test-ready 提测检查命令
│       │   └── devloop.md       # /devloop 按 sprint contract 交付循环
│       └── agents/              # devloop 的三个交付角色，口径可单独评审
│           ├── test-writer.md   # 把一个 B 编号写成失败测试，不碰业务代码
│           ├── test-reviewer.md # 独立评审测试：对 spec、对规范、红因验证，只读
│           └── implementer.md   # 把业务代码写到全绿，不碰测试不改 spec
├── CONTEXT.md                  # 术语表：devloop、B 编号、回链等定名
└── README.md
```

注意：`commands/`、`skills/`、`agents/` 都放在插件根目录，`.claude-plugin/` 里只放清单文件，别把组件塞进去。

## 安装（新成员三步）

```
/plugin marketplace add RBowind/team-plugins
/plugin install team-standards
/plugin marketplace add JetBrains/go-modern-guidelines
/plugin install modern-go-guidelines@goland-claude-marketplace
```

前两步装团队规范；后两步装 JetBrains 官方「现代 Go 惯用法」插件，godev 引用它但不含它的内容——上游更新自动跟随。装完建议开一次自动更新：`/plugin` → Marketplaces → 选 `goland-claude-marketplace` → Enable auto-update。

装完后自动生效：AI 会在写测试、review 时遵守团队规范，写 Go 代码时同时过 godev（风格）和 use-modern-go（现代写法）；输入 `/team-standards:devloop <capability>` 对已放行（contract Status: APPROVED）的 feature 开交付循环；输入 `/team-standards:test-ready` 走统一提测检查。插件命令带 `/team-standards:` 前缀调用，裸名不可用。

## 怎么改

- 改规范 = 改 `skills/` 里的 SKILL.md，走 PR 评审，和改代码一个流程。
- 加新命令 = 在 `commands/` 下加一个 `.md` 文件，文件名就是命令名。
- 改交付角色口径 = 改 `agents/` 里对应的 `.md`，reviewer 的评审维度是规范文本，按规范流程评审。
- 术语定名先进 `CONTEXT.md` 再进文件，避免同一个东西两个名字。
- 改完合并后，其他人 `/plugin marketplace update` 拉最新。
