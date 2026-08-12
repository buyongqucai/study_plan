---
name: exam-pdf-quiz
description: >-
  Converts scanned exercise PDFs into local Chinese practice boards (submit-to-grade),
  wrong-question books, and favorite books for any exam subject (税务师/CPA/中级).
  Use when the user asks for 做题本、错题本、收藏题本、习题看板、合并导出错题/收藏,
  or exam-pdf-quiz workflow.
---

# 教材习题交互（全科目）

## 硬性规则

1. 产物中文命名；脚本在仓库根 `tools/教材习题交互/`（**全局可复用**）。
2. 科目交互唯一入口：`{科目}/06-习题看板/看板.html`。
3. 做题本**交卷前禁止露答案**；交卷后入错题篮；收藏独立导出。
4. 原材料只在 `01-电子教材/`；规则见 `docs/仓库存放与去重规则.md`。

## 目录模板

```
{考试}/{科目}/06-习题看板/
  看板.html
  使用说明.md
  {书名}/
    共用资源/
    题库/第NN章-章名/{题目数据.js,做题本.html}
    错题数据.js / 错题本.html
    收藏数据.js / 收藏题本.html
    导出/
```

## Agent 步骤

### 新章做题本

1. 确认科目、书名、章、PDF、页码映射（示例 `tools/教材习题交互/页码映射-示例.json`）。
2. `渲染PDF页.py` → `识别页面文字.py` → 校对 JSON。
3. `生成章节包.py` 或写入 `题库/第NN章-…/`。
4. `校验题目数据.py`。

### 合并错题 / 收藏

用户话术：

> 按习题册交互技能合并错题：`…/06-习题看板/{书}/导出/错题导出-….json`  
> 按习题册交互技能合并收藏：`…/06-习题看板/{书}/导出/收藏导出-….json`

对应：`合并错题导出.py` / `合并收藏导出.py`（`--书目录` 指向 `{书名}` 目录）。

## 自检

- [ ] 未交卷无答案  
- [ ] 看板三入口可用  
- [ ] 错题/收藏默认不揭层  
