# rulelist

---


仓库结构

```text
vesper-rule-compiler/
├── source/
│   ├── rules.rsl                # 规则源（你只写这个）
│   └── sets/
│       ├── cn_domains.set       # DOMAIN-SET 示例
│       └── ads_domains.set
│
├── compiler/
│   ├── lexer.py                 # 词法解析
│   ├── parser.py                # AST 构建（AND/OR/NOT）
│   ├── ast.py                   # AST 数据结构
│   ├── validator.py             # 校验 / 能力检测
│   ├── backends/
│   │   ├── surge.py             # Surge / SR / Loon / Stash
│   │   ├── quantumultx.py
│   │   ├── clash.py
│   │   ├── singbox.py
│   │   └── v2rayn.py
│   └── compile.py               # 编译入口
│
├── dist/
│   ├── surge.conf
│   ├── quantumultx.conf
│   ├── clash.yaml
│   ├── sing-box.json
│   └── v2rayn.json
│
├── .github/workflows/
│   └── build.yml
│
└── README.md
```

