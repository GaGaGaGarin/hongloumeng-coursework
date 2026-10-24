# 作业仓库：本体知识库 + 信息论

本仓库包含两次作业的完整成果。

## 目录结构

```
├── 作业完成手册.md          # 完整的作业完成手册（目标、步骤、检查标准、常见问题）
├── 作业1_本体/
│   ├── hongloumeng.owl      # 《红楼梦》本体（OWL/RDF-XML，Protege 可直接打开）
│   ├── 简答题答案.md          # 简答题（Class/Object/Data property、Individual、结构理解）
│   ├── 本体设计说明.md        # 论述题设计说明（类/属性/关系/实例）
│   ├── hongloumeng.html     # 交互式知识图谱网页（可选加分项）
│   └── 生成可视化网页.py      # 读取 OWL 生成网页的脚本
└── 作业2_信息论/
    ├── homework.py          # 完整可运行代码（信息熵/KL/交叉熵/点互信息）
    ├── data/                # 语料库：children/hsk/news/yuwen.txt
    ├── 运行结果.txt          # 程序运行输出
    └── 规律发现.md           # 实验规律总结
```

## 作业1：本体知识库（Protege）

**用 Protege 打开本体**：
1. 启动 Protege（`D:\【Protege-5.2.0-win` 下的 `run.bat`）。
2. `File → Open`，选择 `作业1_本体/hongloumeng.owl`。
3. 查看 Classes / Object Properties / Individuals 标签页。
4. `Window → Tabs → OntoGraf` 查看本体结构图并截图。

**本体规模**：7 个类、25 个个体、9 个对象属性、2 个数据属性，184 条三元组。

**交互式网页**：直接双击打开 `作业1_本体/hongloumeng.html`（需联网加载 vis.js）。

## 作业2：信息论

**运行**：
```bash
cd 作业2_信息论
python homework.py
```

**内容**：对 hsk / yuwen / children / news 四个语料库计算：
- 信息熵（9.40 ~ 10.76 bits）
- 共同词典概率分布
- KL 散度（含不对称性演示）与交叉熵
- 点互信息矩阵（词语共现）

详细规律见 `规律发现.md`。
