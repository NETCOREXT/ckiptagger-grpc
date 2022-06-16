# CkipTagger gRPC Service

基於 [CkipTagger](https://github.com/ckiplab/ckiptagger) 的 gRPC 服務。
啟動時會檢查 ./data/model_ws 存不存在，不存在會自動下載模型

---

## 自定義資料

### 斷詞參考符號 (./data/delimiter.json)

```json
// "符號", "符號"
[ ",", "。", ":", "?", "!", ";" ]
```

### 斷詞參考詞典與權重 (./data/recommend.json)

```json
// "詞彙": 權重
{
  "仁今": 1,
  "緯來體育台": 1
}
```

### 斷詞強制詞典與權重 (./data/coerce.json)

```json
// "詞彙": 權重
{
  "土地公": 1,
  "土地婆": 1,
  "公有": 2
}
```
