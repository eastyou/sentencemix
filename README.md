# sentencemix

[![CI](https://github.com/eastyou/sentencemix/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/sentencemix/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

句子重排练习纸：把英文单词或中文汉字打乱成词卡，生成可打印的 A4 语序练习与答案页。

## 特性

- 中文按字拆分，英文按词拆分，自动去掉标点
- 打乱结果与原句一定不同，同一随机种子可复现
- 支持每行一句的 UTF-8 文本文件，自动跳过空行与 `#` 注释
- 每题可配置书写行数，答案页独立分页
- 纯标准库，零依赖，跨平台

## 安装

```bash
python -m pip install -e .
```

## 用法

直接用内置例句：

```bash
sentencemix sheet --count 6 --seed 3 --answers -o sheet.html
```

用自己的句子：

```bash
sentencemix sheet -i sentences.txt --seed 3 --answers -o sheet.html
sentencemix sheet --text "Hello world.
今天天气很好。" --seed 3
```

先在终端看打乱效果：

```bash
sentencemix mix "The cat sleeps on the sofa." --seed 1
```

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `-i` / `--text` | 句子来源，二选一 | 内置 11 句 |
| `--count` | 题目数量 | 全部句子 |
| `--seed` | 随机种子 | 无 |
| `--lines` | 每题书写行数 | 1 |
| `--answers` | 追加答案页 | 关闭 |
| `-o` | 输出文件 | 打印到终端 |

## 句子文件格式

```text
# 以 # 开头的是注释，会被忽略
The quick brown fox jumps over the lazy dog.
今天天气非常适合去公园散步。

```

每行一句；中文句子会拆成单字卡片，英文句子会拆成单词卡片。

## 示例

[examples/sentencemix.html](examples/sentencemix.html) 是 6 道中英混合的重排练习，带答案页。

## 测试

```bash
python -m unittest discover -s tests -v
```

## 协议

MIT © 2026 eastyou
