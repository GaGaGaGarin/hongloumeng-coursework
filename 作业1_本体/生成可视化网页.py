# -*- coding: utf-8 -*-
"""读取 hongloumeng.owl，生成交互式知识图谱网页 hongloumeng.html。"""
import json
import rdflib
from rdflib.namespace import RDF, RDFS, OWL

NS = "http://www.semanticweb.org/hongloumeng#"
g = rdflib.Graph()
g.parse("hongloumeng.owl", format="xml")

# 类 -> 颜色
CLASS_COLOR = {
    "荣国府人物": "#e57373",
    "宁国府人物": "#64b5f6",
    "贾府人物": "#9575cd",
    "外人": "#81c784",
    "府第": "#ffb74d",
    "官职": "#ffd54f",
}

def local(uri):
    return str(uri).replace(NS, "")

# 1. 收集个体的类型（只取最具体的类）
ind_types = {}
for ind in g.subjects(RDF.type, OWL.NamedIndividual):
    types = [t for t in g.objects(ind, RDF.type) if t != OWL.NamedIndividual]
    # 优先取 荣国府/宁国府/外人/府第/官职
    best = None
    for t in types:
        name = local(t)
        if name in CLASS_COLOR and best is None:
            best = name
    if best is None and types:
        best = local(types[0])
    ind_types[local(ind)] = best or "人物"

# 2. 构建节点
nodes = []
seen = set()
for ind, cls in ind_types.items():
    if ind in seen:
        continue
    seen.add(ind)
    color = CLASS_COLOR.get(cls, "#90a4ae")
    nodes.append({
        "id": ind, "label": ind,
        "group": cls,
        "color": {"background": color, "border": "#555"},
        "title": f"{ind}（{cls}）",
        "font": {"size": 16},
    })

# 3. 构建边（对象属性关系）
EDGE_LABEL = {
    "是父亲": "父亲", "是母亲": "母亲", "是丈夫": "丈夫", "是妻子": "妻子",
    "是儿子": "儿子", "是女儿": "女儿", "是外孙女": "外孙女",
    "居住于": "居住于", "任职于": "任职",
}
edges = []
for s, p, o in g:
    if local(p) in EDGE_LABEL and local(s) in ind_types and local(o) in ind_types:
        edges.append({
            "from": local(s), "to": local(o),
            "label": EDGE_LABEL[local(p)],
            "arrows": "to",
            "font": {"size": 11, "color": "#666"},
        })

# 4. 图例（类）
legend = {c: {"color": CLASS_COLOR.get(c, "#90a4ae"), "count": 0} for c in CLASS_COLOR}
for _, cls in ind_types.items():
    if cls in legend:
        legend[cls]["count"] += 1

html = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>红楼梦本体知识库可视化</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body { font-family: "Microsoft YaHei", sans-serif; margin: 0; background:#f7f7f7; }
  header { background:#7e1f1f; color:#fff; padding:14px 20px; }
  header h1 { margin:0; font-size:20px; }
  header p { margin:4px 0 0; font-size:13px; opacity:.85; }
  #legend { display:flex; gap:16px; flex-wrap:wrap; padding:10px 20px; background:#fff; border-bottom:1px solid #ddd; }
  .item { display:flex; align-items:center; gap:6px; font-size:13px; }
  .dot { width:14px; height:14px; border-radius:3px; border:1px solid #555; }
  #net { height: calc(100vh - 130px); }
</style>
</head>
<body>
<header>
  <h1>《红楼梦》本体知识库 · 冷子兴演说荣国府</h1>
  <p>节点=个体/府第/官职，连线=人物关系（可拖拽、缩放、悬停查看）</p>
</header>
<div id="legend">
__LEGEND__
</div>
<div id="net"></div>
<script>
var nodes = new vis.DataSet(__NODES__);
var edges = new vis.DataSet(__EDGES__);
var container = document.getElementById('net');
var data = { nodes: nodes, edges: edges };
var options = {
  layout: { hierarchical: { enabled:false } },
  physics: { solver:'forceAtlas2Based', stabilization:{iterations:250} },
  edges: { smooth:{type:'dynamic'}, color:{color:'#999'} },
  interaction: { hover:true, tooltipDelay:100 }
};
new vis.Network(container, data, options);
</script>
</body>
</html>
"""

legend_html = "\n".join(
    f'<div class="item"><span class="dot" style="background:{v["color"]}"></span>{k}（{v["count"]}）</div>'
    for k, v in legend.items() if v["count"] > 0
)

html = (html
        .replace("__NODES__", json.dumps(nodes, ensure_ascii=False))
        .replace("__EDGES__", json.dumps(edges, ensure_ascii=False))
        .replace("__LEGEND__", legend_html))

with open("hongloumeng.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"生成 hongloumeng.html：{len(nodes)} 个节点，{len(edges)} 条边")
