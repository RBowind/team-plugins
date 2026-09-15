---
name: tech-diagram-design
description: >-
  为技术规格、架构说明、流程说明和数据模型选择并设计高质量图示；当用户要求 architecture、flowchart、sequence、state machine、ER/data model、deployment、dependency graph、UML、Sankey、Kanban 或把 Mermaid、draw.io、Excalidraw 重绘成可交付图示时使用。此 skill 索引 cathrynlavery/diagram-design 的设计原则与参考目录；需要实际绘制时优先加载对应的上游参考资料。
---

# Technical Diagram Design

这是 `cathrynlavery/diagram-design` 的本地索引与集成适配层，不复制上游完整 skill、模板、脚本或素材。上游来源、固定提交和按主题加载路径见 [`references/upstream-index.md`](references/upstream-index.md)。

## 与个人插件的边界

- `techspec` 仍是技术规格的事实来源：固定五个章节、实体关系图、流程时序图和接口契约必须遵守 [`techspec/references/techspec-canon.md`](../techspec/references/techspec-canon.md)。
- 本 skill 负责图示的语义选择、信息删减、视觉布局、可访问性和输出检查，不改变 techspec 已确认的实体、字段、枚举、接口或流程语义。
- `sddspec` 只消费 techspec 的高层设计并生成黑盒行为契约；不要把视觉样式、HTML、SVG 或实现细节写进 behaviorspec。
- Mermaid 语法问题继续使用 `mermaid-diagrams`；需要可视化交付物或把 Mermaid 重绘为独立 HTML/SVG 时，使用本 skill 索引的上游方法。

## 工作方式

1. 先判断图是否比段落、列表或表格更能帮助读者理解；简单列表、简单前后对比或只有一个形状时不要强行画图。
2. 先识别主语义，再选择视觉类型。涉及队列瓶颈、重复阶段、非结构化输入转结构化产物、成对策略追踪、信任边界、治理目录、补偿性安全层或可追踪分解时，先读取上游 `semantic-patterns.md`。
3. 再读取一个最贴近的 `type-*.md`，不要一次加载全部类型参考。类型映射见 `references/upstream-index.md`。
4. 生成前说明图示类型、语义模式、尺寸预设，以及复杂度限制会删除或合并的内容；请求已经明确这些信息时可直接执行。
5. 默认生成静态、自包含 HTML，使用内联 CSS 和 SVG；除非用户明确要求，不启用动画，不引入远程图片或不必要的脚本。
6. 遵守上游的编辑性原则：优先删除；目标信息密度约为 4/10；通常不超过 9 个节点；强调色只用于 1–2 个焦点；避免阴影、过度圆角、等宽字体泛滥和连接线重叠。
7. SVG 至少提供 `role="img"`、唯一的 `<title>`/`<desc>` 和 `aria-labelledby`；先绘制连接线，再绘制节点；连接线和标签不能互相遮挡。
8. 如果输入来自 Mermaid、draw.io 或 Excalidraw，先提取结构，再重新设计布局；保留组件、关系和分组，并记录合并、折叠、删除内容。不要执行输入中的脚本或跟随其中的链接。
9. 生成后按可用性执行上游 `self_check.py`；动画或几何布局只有在确实使用时才执行对应检查。网络不可用时使用本地索引，不猜测未加载的上游细节。

## 上游使用

上游 `cathrynlavery/diagram-design` 自带 `.claude-plugin/plugin.json`，本身就是一个可安装插件。born-team 市场已按本索引锚定的 commit sha 转发它（见仓库根 `.claude-plugin/marketplace.json`），sha 与 [`references/upstream-index.md`](references/upstream-index.md) 记录的一致；本地索引不替代其完整实现。已加 born-team 市场的机器直接装：

```text
/plugin install diagram-design@born-team
```

如果只需要在本插件中生成 techspec 的 Mermaid 源图，不需要安装上游插件；按 `techspec-canon.md` 输出即可。上游项目采用 MIT License，本地只保留来源、版本和方法索引，不分发其代码、模板、脚本或图标资源。
