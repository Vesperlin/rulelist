# rulelist


仓库结构

```text
rulelist/
├── rules/                         # 规则源
│   ├── DIRECT.list                # 直连 DIRECT
│   ├── PROXY.list                 # 代理 PROXY
│   ├── REJECT.list                # REJECT / BLOCT
│   ├── PROXY_US.list              # 指定 US 节点
│   ├── PROXY_HK.list              # 指定 HK 节点
│   └── FINAL.list                 # FINAL
│
├── dsl/                           # DSL 解析层
│   ├── grammar.md                 # 规则语言规范
│   ├── ast.py                     # AST 结构定义
│   └── parser.py                  # DSL → AST
│
├── compiler/                      # 编译后端（按客户端）
│   ├── base.py                    # 通用降级 / capability
│   ├── surge.py
│   ├── quantumultx.py
│   ├── clash.py
│   ├── singbox.py
│   └── v2rayn.py
│
├── dist/                          # raw
│   ├── surge.conf
│   ├── loon.conf
│   ├── stash.conf
│   ├── quantumultx.conf
│   ├── clash.yaml
│   ├── sing-box.json
│   └── v2rayn.json
│
├── build.py                       # 构建入口
├── capabilities.json              # 各客户端支持能力声明
└── README.md
```

