# diagram-design 上游索引

## 来源

- 项目：[`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
- Skill 目录：[`skills/diagram-design`](https://github.com/cathrynlavery/diagram-design/tree/main/skills/diagram-design)
- 当前索引提交：`8d8b2993ee2256ee7dfc0eeb3b5713aba3b60792`
- 上游版本：`2.6.22`
- 许可证：MIT，版权声明归 Cathryn Lavery；本地索引不复制上游代码、模板、脚本或素材。

## 按需加载顺序

1. 先读上游 `SKILL.md`，获取选择规则、复杂度预算、输出要求和通用反模式。
2. 涉及行为、状态、治理、风险或安全边界时，再读 `references/semantic-patterns.md`。
3. 按主题只读一个最接近的 `references/type-*.md`；不要为了选择一个图而加载整个目录。
4. 需要品牌适配时读 `references/style-guide.md` 与 `references/onboarding.md`；需要多品牌配置时再读 `references/profiles.md`。
5. 需要导入时读对应的 `references/import-drawio.md`、`references/import-mermaid.md` 或 `references/import-excalidraw.md`，并按 `references/output-spec.md` 记录保真度。
6. 需要动画时读 `references/animation.md`；静态输出仍是默认值。
7. 需要 SVG/PNG 导出或结构化块登记时读 `references/export.md` 或 `references/export-registry.md`。
8. 需要原语时按需读 `references/primitive-annotation.md`、`references/primitive-sketchy.md`、`references/primitive-terminal.md` 或 `references/primitive-icons.md`。
9. 输出后运行上游 `scripts/self_check.py`；只有使用对应能力时才运行导入脚本或几何、动画检查脚本。

## 语义模式 → 视觉类型

| 主要语义 | 优先类型 | 上游参考 |
|---|---|---|
| 组件和连接 | Architecture | `references/type-architecture.md` |
| 旧系统现状和现代化前状态 | IT current-state | `references/type-it-state.md` |
| 决策逻辑和分支 | Flowchart | `references/type-flowchart.md` |
| 按时间排列的消息 | Sequence | `references/type-sequence.md` |
| 状态和转换 | State machine | `references/type-state.md` |
| 实体、字段和关系 | ER / data model | `references/type-er.md` |
| 时间事件 | Timeline | `references/type-timeline.md` |
| 跨职能交接 | Swimlane | `references/type-swimlane.md` |
| 二维定位和优先级 | Quadrant | `references/type-quadrant.md` |
| 多指标比较 | Radar / Spider | `references/type-radar.md` |
| 循环或飞轮 | Loop | `references/type-loop.md` |
| 容器层级 | Nested | `references/type-nested.md` |
| 父子层级 | Tree | `references/type-tree.md` |
| 归属、路由或升级关系 | Org chart | `references/type-org-chart.md` |
| 抽象层 | Layer stack | `references/type-layers.md` |
| 集合重叠 | Venn | `references/type-venn.md` |
| 排名或转化漏斗 | Pyramid / funnel | `references/type-pyramid.md` |
| 分类数量比较 | Bar chart | `references/type-bar.md` |
| 起点到终点的增减桥 | Waterfall | `references/type-waterfall.md` |
| 部分与整体 | Treemap | `references/type-treemap.md` |
| 时间趋势或排名移动 | Line chart | `references/type-line.md` |
| 时间轴上的任务 | Gantt | `references/type-gantt.md` |
| 分布、相关性或气泡 | Scatter plot | `references/type-scatter.md` |
| 端到端数据栈 | High-Level | `references/type-high-level.md` |
| 多角色顺序流程和数据交接 | Process | `references/type-process.md` |
| 多层数据存储和质量等级 | Medallion | `references/type-medallion.md` |
| 角色范围内的数据管道步骤 | Data flow | `references/type-data-flow.md` |
| 数据平台集成拓扑 | DP integration | `references/type-dp-integration.md` |
| 角色或组件权限矩阵 | DP security matrix | `references/type-dp-security-matrix.md` |
| 数量分流和合流 | Sankey | `references/type-sankey.md` |
| 一个结果的分组根因 | Fishbone | `references/type-fishbone.md` |
| 价值链和演化路线 | Wardley map | `references/type-wardley.md` |
| 工作状态、在制品限制和阻塞 | Kanban | `references/type-kanban.md` |
| 用户阶段、行为和感受 | User journey | `references/type-journey.md` |
| 运行区域、主机、副本和端口 | Deployment | `references/type-deployment.md` |
| 依赖、扇入和循环 | Dependency graph | `references/type-dependency.md` |
| 类、操作、继承和组合 | UML class | `references/type-uml-class.md` |
| 发布切线和故事骨架 | Story map | `references/type-story-map.md` |
| 物理数据库表、字段、索引和外键 | Database schema | `references/type-db-schema.md` |

## 上游仓库结构索引

### 入口和参考资料

```text
skills/diagram-design/SKILL.md
skills/diagram-design/references/style-guide.md
skills/diagram-design/references/semantic-patterns.md
skills/diagram-design/references/onboarding.md
skills/diagram-design/references/profiles.md
skills/diagram-design/references/output-spec.md
skills/diagram-design/references/export.md
skills/diagram-design/references/export-registry.md
skills/diagram-design/references/animation.md
skills/diagram-design/references/doctor.md
```

### 类型参考

```text
skills/diagram-design/references/type-architecture.md
skills/diagram-design/references/type-it-state.md
skills/diagram-design/references/type-flowchart.md
skills/diagram-design/references/type-sequence.md
skills/diagram-design/references/type-state.md
skills/diagram-design/references/type-er.md
skills/diagram-design/references/type-timeline.md
skills/diagram-design/references/type-swimlane.md
skills/diagram-design/references/type-quadrant.md
skills/diagram-design/references/type-radar.md
skills/diagram-design/references/type-polar.md
skills/diagram-design/references/type-loop.md
skills/diagram-design/references/type-nested.md
skills/diagram-design/references/type-tree.md
skills/diagram-design/references/type-org-chart.md
skills/diagram-design/references/type-layers.md
skills/diagram-design/references/type-venn.md
skills/diagram-design/references/type-pyramid.md
skills/diagram-design/references/type-bar.md
skills/diagram-design/references/type-waterfall.md
skills/diagram-design/references/type-treemap.md
skills/diagram-design/references/type-line.md
skills/diagram-design/references/type-gantt.md
skills/diagram-design/references/type-scatter.md
skills/diagram-design/references/type-high-level.md
skills/diagram-design/references/type-process.md
skills/diagram-design/references/type-medallion.md
skills/diagram-design/references/type-data-flow.md
skills/diagram-design/references/type-dp-integration.md
skills/diagram-design/references/type-dp-security-matrix.md
skills/diagram-design/references/type-sankey.md
skills/diagram-design/references/type-fishbone.md
skills/diagram-design/references/type-wardley.md
skills/diagram-design/references/type-kanban.md
skills/diagram-design/references/type-journey.md
skills/diagram-design/references/type-deployment.md
skills/diagram-design/references/type-dependency.md
skills/diagram-design/references/type-uml-class.md
skills/diagram-design/references/type-story-map.md
skills/diagram-design/references/type-db-schema.md
```

### 输入、原语和验证

```text
skills/diagram-design/references/import-drawio.md
skills/diagram-design/references/import-mermaid.md
skills/diagram-design/references/import-excalidraw.md
skills/diagram-design/references/primitive-annotation.md
skills/diagram-design/references/primitive-sketchy.md
skills/diagram-design/references/primitive-terminal.md
skills/diagram-design/references/primitive-icons.md
skills/diagram-design/scripts/drawio_extract.py
skills/diagram-design/scripts/mermaid_extract.py
skills/diagram-design/scripts/excalidraw_extract.py
skills/diagram-design/scripts/self_check.py
```

### 模板和示例

```text
skills/diagram-design/assets/template.html
skills/diagram-design/assets/template-dark.html
skills/diagram-design/assets/template-full.html
skills/diagram-design/assets/template-motion.html
skills/diagram-design/assets/template-terminal.html
skills/diagram-design/assets/example-<type>.html
skills/diagram-design/assets/index.html
skills/diagram-design/assets/icons.html
```

## 与现有 techspec 的映射

| 本插件已有约定 | 上游可补充的参考 |
|---|---|
| 数据模型使用 `erDiagram` | `type-er.md` 或 `type-db-schema.md` |
| 主流程使用 `sequenceDiagram` | `type-sequence.md` 或 `type-process.md` |
| 状态变化使用 `stateDiagram-v2` | `type-state.md` |
| 服务或资金流总览使用 `flowchart` | `type-architecture.md`、`type-high-level.md` 或 `type-data-flow.md` |
| 技术规格五段结构 | `SKILL.md` 的选择、删减、布局和可访问性规则 |

上游参考只影响图示表达，不覆盖本插件对技术事实和文档结构的约束。若上游示例与实际需求、techspec 正文或已确认接口冲突，以实际需求和本插件的技术事实为准。
