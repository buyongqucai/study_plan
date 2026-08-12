# 习题册交互 · 参考

## 题目对象字段

| 字段 | 说明 |
|------|------|
| `id` | 题号（数字） |
| `type` | 题型文案；含「多选」则按多选 UI |
| `source` | 来源页码 |
| `stem` | 题干 |
| `options` | `{A,B,C,D,E?}` |
| `answer` | 正解字母串，如 `ABCE`（全对才得分） |
| `analysis` | 解析 |
| `knowledge` | 字符串数组 |
| `lecture` | 讲义出处（可选） |
| `hooks` | 记忆钩子（可选） |
| `wrongPick` | 错题本：上次错选；做题全量题可空 |
| `whyWrong` | 可选 |
| `fromSubmit` | 可选，交卷来源说明 |

## 导出错题 JSON

```json
{
  "book": "必刷550",
  "subject": "税法一",
  "chapterId": "第01章",
  "chapterTitle": "税法基本原理",
  "exportedAt": "2026-08-12T15:00:00+08:00",
  "questions": [ { "id": 18, "wrongPick": "ABC", "...": "完整题字段" } ]
}
```

合并规则：按 `id` 去重；新导出覆盖同题号的 `wrongPick` 与来源时间。

## 做题本评分

- 单选：选中字母 == `answer`
- 多选：排序后字母串全等才得分（少选/多选/错选均不得分）
