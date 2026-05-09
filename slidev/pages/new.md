---
layout: two-cols
---
# new

## 组件
<!-- ./components/Counter.vue -->
<Counter :count="10" m="t-4" />

<span v-mark.box.red="1"> red box </span>are used to signify strings.

<span v-mark.highlight.yellow="2"> yellow highlight </span><span v-mark.highlight.red="5"> red highlight </span>

<v-click>
show
</v-click>
<v-click>
show1
</v-click>
<v-click>
show2
</v-click>

## 流程图
```mermaid{scale:0.7}
graph TD
B[Text] --> C{Decision}
C -->|One| D[Result 1]
C -->|Two| E[Result 2]
```
::right::
```mermaid
graph TD
B[Text] --> C{Decision}
C -->|One| D[Result 1]
C -->|Two| E[Result 2]
```