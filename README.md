# federal-law-chain-anchor

**联邦立法史链·外部锚** — openLLM 联邦治理体系的立法史哈希锚发布点。

本仓库是 [openLLM](https://github.com/zcs366) 联邦（Federation）治理体系的外部见证锚点：联邦的每一次立法（enact）、修法（amend）、废法（repeal）、执法（execution）都记录在一条 append-only 哈希链上。本仓库定期发布该链的**链尾哈希锚**（anchor），使"这条链从未被整体重写"可以被任何第三方独立验证——**即使链本体所在的系统消失，锚的公开时间戳仍证明这套法存在过。**

## 这是什么

一个 agent 治理系统如何证明自己的法律是真实生长而非事后编造？答案是：把每次立法事件的哈希指纹发布到系统控制之外。锚文件本身极小（<500B），但它绑定在 GitHub 的 commit 时间戳上，形成第三级时间证据。

```
锚文件 anchor-latest.json:
{
  "format_version": 1,
  "chain": "federal-legislative-history",
  "tip_event_id": "LH-0019",
  "tip_hash": "3d044e00a4349c58",
  "total_events": 19,
  "type_counts": {"genesis": 1, "enact": 7, "amend": 5, "execution": 6},
  "prev_anchor_hash": "...",   ← 锚自身的链：任何中间删除可被检测
  "generated": "2026-08-28"
}
```

## 三级验证

任何持有历史锚文件 + 对应链文件副本者可验证：

1. **锚自链**：`prev_anchor_hash` 是否衔接上一次发布（删除中间锚会被发现）
2. **哈希重算**：对链副本重算 sha256 链，链尾是否等于 `tip_hash`
3. **时间戳交叉**：GitHub commit 时间 vs 锚内 `tip_date` 是否自洽

## 设计要点

- **锚定"内容+格式版本"而非裸内容**：`format_version` 递增表示链行格式演进；旧锚按旧版验证逻辑仍可验证（向后兼容承诺）
- **发布内容不含法条正文**——锚是法的影子，不是法的主人
- **执行不触发发布**：execution 事件（每6h心跳）只留在链上，立法事件（enact/amend/repeal）才触发锚更新 + 每周一兜底发布

## 姊妹仓库

- [openllm](https://github.com/zcs366/openllm) — 六体架构（IAI/IAX/ISA/IOS/ISN/IKO）
- [openllm-memory](https://github.com/zcs366/openllm-memory) — 记忆系统
- 理论背景：**法的自创生**（autopoiesis, Maturana & Varela）——立法程序规范空间操作封闭；立法史是法的 ISL（身份回忆层）

## 状态

| 项 | 值 |
|----|-----|
| 链 | federal-legislative-history |
| 当前格式版本 | 1 |
| 首事件 | LH-0001 (2026-05-16, 匠石原则) |
| 维护 | openLLM 联邦军师祭酒 · 监督：张成市 |
