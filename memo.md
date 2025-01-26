やること
- テストのきょうどの縮小版の実行
- CPUサイズの増加
- クエリの方法を理解
  - influx bucket list
  - influx query --raw 'from(bucket:"tochigi") |> range(start:-12h)'
- CPU使用率の計算 Cadvisor

#! /bin/bash
set -eux


