# Rulelist DSL 规范

>1. 编写 rules/*.list 请遵循此规范
>2. 每条规则写成一行一个表达式。默认以 `,`  分隔

## 1. 基本规则

###### **格式**
```
<TYPE>,<VALUE>[,<OPTION1>[,<OPTION2>...]]
```
###### **支持的 TYPE**  (对大小写不敏感)
> - **DOMAIN**,example.com
> - **DOMAIN-SUFFIX**,example.com
> - **DOMAIN-KEYWORD**,example
> - **DOMAIN-WILDCARD**,*.example.com          
> - **USER-AGENT**,com.google.ios.youtube*
> - **URL-REGEX**,^https?:\/\/(.*\.)?example\.com\/
> - **IP-CIDR**,1.2.3.0/24
> - **IP-ASN**,13335
> - **DST-PORT**,443
> - **GEOIP**,CN
> - **RULE-SET**,https://raw.githubusercontent.com/xxx/yyy.list
> - **DOMAIN-SET**,https://raw.githubusercontent.com/xxx/yyy.txt
> - **SCRIPT**,script/name.js       
###### **可选 OPTION**
- **no-resolve**  
   `用于 IP-CIDR / RULE-SET 等支持 no-resolve 的后端`
- **extended-matching**                       
   `Surge RULE-SET 可用（让域名规则同时匹配 SNI/Host）`
###### **注意事项**
> 1. **VALUE** 中不能包含 未转义的逗号
> 2. 若**URL-REGEX** 中一定要使用逗号，请用 `\` 或改为`不含逗号的正则`
> 3. **注释**：以 `#` 或 `;` 开头



## 2. 逻辑规则（AND / OR / NOT）

###### **格式**
```
AND,((<RULE>),(<RULE>),(<RULE>))
OR,((<RULE>),(<RULE>))
NOT,((<RULE>))
# <RULE> 允许嵌套，既可以是原子规则，也可以是逻辑规则
```
###### **示例**
- **AND**,((NOT,((DOMAIN,tracker.example.com))),(DOMAIN-SUFFIX,example.com))
- **OR**,((DOMAIN-SUFFIX,openai.com),(DOMAIN-KEYWORD,chatgpt))
##### **说明**
> - 该语法与 `Surge Logical Rule` 的写法对齐，Surge 后端可原样输出
> - 其它后端会尝试“降级展开”，无法表达时会跳过




## 3. FINAL
> - rules/FINAL.list 允许写 `FINAL` 或 `FINAL,PROXY`
> - 但在本仓库设计中：FINAL 的“动作”由 **build.py** 按文件名决定，建议只写 `FINAL`


## 4. 策略来源

###### **list 文件名 -> 目标策略（动作）映射**
> - DIRECT.list            -> DIRECT
> - PROXY.list             -> PROXY
> - REJECT.list            -> REJECT
> - PROXY_US.list       -> 节点/策略组
> - PROXY_HK.list       -> 节点/策略组
> - FINAL.list                -> FINAL


## 5. 兼容性现实

###### **差异**
不同客户端对 RULE-SET / DOMAIN-SET / SCRIPT 的支持差异巨大
- **Surge**
    RULE-SET 强, 且 `ruleset` 文件每行不含 policy
- **Clash/mihomo**
     rule-providers 支持 `classical`/`domain`/`ipcidr`
- **sing-box**
     支持外部 `rule-set(JSON)` 与 `route规则`字段
 - **QX/Loon/Surge/Stash** 
     脚本/重写体系差异大，本仓库把 SCRIPT 作为“占位类型”，默认仅在支持且你补齐脚本文件时启用
###### **因此：本工程的目标是**
> 1) 维护一个“主规则源”
> 2) 生成尽可能可导入、可用的多端配置
> 3) 对无法表示的能力做 `清晰降级` 与 `日志输出` 处理

