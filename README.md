# BoardRaid Translation
面向社区的客户端 i18n 语言资源。贡献者直接向本仓库 **master** 提 PR，由项目所有者审核，不使用私人源码仓库的 release 流程。
## 当前四种语言
| 文件 | 语言 |
| --- | --- |
| client/zh_cn.json | 简体中文 |
| client/zh_tw.json | 繁體中文 |
| client/en_us.json | English (US)，键表与回退基准 |
| client/no_no.json | Norsk (Bokmål) |
## 修改现有翻译
编辑对应 client/*.json，只改值，不改键。保留 `%s`、`%d` 等占位符顺序与数量，以及 `%%`、换行和必要的格式代码。运行 `python tools/validate.py`，然后直接提交 PR。
## 新增语言
1. 使用 Minecraft 语言代码，如 ja_jp；不要自行改写成中文文件名。
2. 运行 `python tools/new-language.py ja_jp --name 日本語`，生成空白草稿文件并登记 languages.json。
3. 逐项补充 en_us.json 中的键值。draft 可以只包含已翻译的键，缺失项由英文回退；不得添加不存在的键。
4. 完成后提交 PR，请维护者在语言审阅及完整性检查通过后将状态改为 ready。已有四种 ready 语言不能缺键。
5. 维护者使用私人源码仓库的导入工具预览差异、导入资源并登记 ready 语言菜单，经过客户端验证后随新版本发出。社区贡献者无需进行这一内部操作。
新增 JSON 或合并 PR 不会让已经发布的客户端热加载新语言，也不下载或执行网络代码。
## 本地检查与预览
`python tools/validate.py --self-test` 运行错误键、占位符、重复键和不完整语言的自证。
`python tools/validate.py` 校验全部语言并显示覆盖率。
`python tools/pack.py --output ../translations-preview.zip` 生成 Minecraft 1.16.1 资源包。将它放入未固定模组界面语言的全新测试实例的 resourcepacks 后启用，用对应的游戏语言预览翻译；草稿不一定出现在 BoardRaid 独立语言菜单。
资源包只含本项目语言 JSON，不含游戏文件或可执行代码。请在未进行正式比赛的实例预览，不承诺未经审核资源包能通过竞技自检。
## i18n 边界
语言只改变显示，不改变任务 ID、物品 ID、判定或协议。模组语言独立于原版语言；翻译不完整时显示英文回退，不编造目标或数值。
本仓库是游戏 UI 语言资源，不包含官网 Wiki 的中英文正文；官网文案在各自文档仓库修改。
