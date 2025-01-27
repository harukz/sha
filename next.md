

問題
prometheusのexportがうまくいかない



次に、cAdvisor コンテナにオプションを添えて起動します：
cadvisor:
    image: "google/cadvisor:0.16.0"
    volumes:
        - "/:/rootfs:ro"
        - "/var/run:/var/run:rw"
        - "/sys:/sys:ro"
        - "/var/lib/docker/:/var/lib/docker:ro"
    links:
        - "InfluxSrv:influxsrv"
    ports:
        - "8080:8080"
    command: "-storage_driver=influxdb -storage_driver_db=cadvisor -storage_driver_host=influxsrv:8086 -storage_driver_user=root -storage_driver_password=root -storage_driver_secure=False"

やり方
1. cAdvisorをそのままつなげられそう
2. prometheusのcustom exporterでやる
3. prometheusのconfig変える

helm upgrade -f datadog-values.yaml <RELEASE NAME> datadog/datadog


メトリクスのフォワード先のストレージバックエンドが必要になります。ストレージバックエンドにはInfluxDBが使われることが多いようです。


```
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: cadvisor
  namespace: kube-system
  labels:
    k8s-app: cadvisor
spec:
  selector:
    matchLabels:
      k8s-app: cadvisor
  template:
    metadata:
      labels:
        k8s-app: cadvisor
    spec:
      containers:
      - name: cadvisor
        image: gcr.io/cadvisor/cadvisor:v0.47.0
        ports:
        - containerPort: 8080
          name: http
        volumeMounts:
        - name: rootfs
          mountPath: /rootfs
          readOnly: true
        - name: var-run
          mountPath: /var/run
          readOnly: true
        - name: sys
          mountPath: /sys
          readOnly: true
        - name: docker
          mountPath: /var/lib/docker
          readOnly: true
        - name: dev-disk
          mountPath: /dev/disk
          readOnly: true
        args:
        - --store_container_labels=true
        - --enable_metrics=memory,cpu,disk,network
        - --housekeeping_interval=30s
        - --storage_driver=influxdb
        - --storage_driver_host=http://localhost:9093
        - --storage_driver_db=cadvisor
        resources:
          requests:
            cpu: 100m
            memory: 300Mi
        securityContext:
          privileged: true
      volumes:
      - name: rootfs
        hostPath:
          path: /
      - name: var-run
        hostPath:
          path: /var/run
      - name: sys
        hostPath:
          path: /sys
      - name: docker
        hostPath:
          path: /var/lib/docker
      - name: dev-disk
        hostPath:
          path: /dev/disk

```

その後cAdvisorのデータベースを作成する


volumeMounts と volumes の項目は、cAdvisor がホストシステム上のリソースを読み取るために必要なマウント設定を行っています。これにより、cAdvisor はコンテナのリソース使用状況やホストシステムの情報を収集できます。

CREATE DATABASE cadvisor;


args:
- --store_container_labels=true
- --enable_metrics=memory,cpu,disk,network
- --housekeeping_interval=30s
- --storage_driver=influxdb
- --storage_driver_host=http://localhost:9093
- --storage_driver_db=cadvisor
- --storage_driver_user=cadvisor_user
- --storage_driver_password=password123

cAdvisorで値を取得する方法
　cAdvisorでは下記のURLにアクセスすることで値を取得できます。

http://<hostname>:<port>/api/<version>/<request>
　例えばVersion 1.3のAPIには、下記のアドレスにアクセスし、さらにそこからmachineを選択して値を表示させます。

http://<hostname>:<port>/api/v1.3
　出力される値はJSON形式です。2015年6月現在、入手できるcAdvisor 0.14ではAPIのv1.0、1.1、1.2、1.3、2.0を使用できます。v2.0はベータ版です



---

評価手法

手作業で評価する際に測る・記録する指標
工程は大きく分けて三つを繰り返す
1. gatling実行
2. 結果確認
3. 値決める

ストップウォッチでそれぞれを測りつつ


終了条件
変更の最小値は1.0で超える最小値を見つける


やった後に、何回繰り返したかなども数えてみる
- コマンドを打った回数とか
- ブラウザを開いて、関心の
- DBなくて、データが流れて行ってしまうから、ずっとcAdvisor見ていなきゃいけない


---

25分くらいのプレゼン

40枚くらい
含める内容
- テーマ概要
- 実施内容（スライドの構成）
  - 1-2日目: 環境構築
  - 2-3日目: テストの実行 
  - 4-5日目: 課題抽出・方式検討
  - 6-7日目: 実装
  - 8日目: 評価
  - 9-10日目: スライド作成
- 2-3日目: テストの実行
  - そもそもテストとは？なぜ必要なのか。
  - 対象のシステム
    - gatling, cAdvisor, prometheus, grafana
  - 実施したテスト内容
    - 最大接続数やアクセス頻度...
  - 簡単な結果の分析
- 4-5日目: 課題抽出・方式検討
  - 感じた課題を列挙
  - 何故、現在のものを選んだのか
  - 現在のものを深堀
  - 方式検討、必要とされる機能は何か？
  - どのようにそれらの要素を組み合わせるか？
  - 研究要素に関して
- 5-7日目: 実装の詳細
  - 全体像の図
    - pythonでの実装を少し載せる
  - 二分探索アルゴリズムの説明
- 8日目: 評価
  - 結果
  - どうなったか
- 結論
- 今後の課題・発展的内容
  - 二分探索のデメリット: 単調増加関数にしか適用できない
  - 多変数関数
    - 一つの変数を固定するとか、組み合わせ最適化として解くか

---

課題抽出の時?
そもそも、自動化はいつ有用となるのか
=> 繰り返しの回数が多いとき
=> 性質的にテストと自動化は相性が良いといえる

---


システム構成の更新？
- cAdvisorをInfluxDBにエクスポートするようにする



プログラムの構造に関して

前提: 初期値が決まっている

繰り返しのコード
1. 決めた値でのgatling実行
2. 実行中の最大CPU使用率取得
3. 結果に基づいて、次の値を決める or 終了


while True:
  run_gatling(value)
  get_cpustats(value)
  decide_next(left, right, value)
  
  if (left <= right):
    break

二分探索のコード: 探索範囲を半分にするのを繰り返す
1. 決めた値でのgatling実行
2. 実行中の最大CPU使用率取得
3. (分岐) CPU使用率が基準より大きいなら..、小さいなら...

探索範囲を半分にしていくのを繰り返す


3の部分が組み換え可能


pythonで実行を考えている
=> 必要とされる機能
- python経由で引数を渡して、gatlingを実行する機能
- cAdvisorの値を保存?取得?する機能
  - やり方は二つあるけど、InfluxDBを選んだ
- 二分探索アルゴリズムの実装

実際のコードを関数レベルで隠してそれぞれまとめる

---


発展
今回の研究の中核の部分は「どのように変数を探索するか」ということ。
実際には、これは注目している指標による。

では、今回の自動化は意味がないのか？
NO

Insight?: 多くの場合、テスト工程は繰り返しの工程を含む + 似た要件に対してのテストを行う

あらかじめ、指標がわかっている
=> それらを分類して、
