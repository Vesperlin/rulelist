# rulelist

### GitHub Raw 导入方式

###### Surge/Loon/Stash
    直接订阅 dist/.conf 或 rules/.list
###### Clash/mihomo
    使用 dist/clash.yaml
###### sing-box
    方法一：导入 dist/sing-box.json
    方法二：把里面 route.rules 合并进你现有 config
###### v2rayN
    方法一：导入 dist/v2rayn.json
    方法二：把 routing.rules 合并


### 生成 dist

```bash
python3 build.py --base-raw-url "https://raw.githubusercontent.com/<user>/<repo>/main/rulelist"

### 仓库结构

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





