# JCM Catalogueに検索をかけてcsvに出力します
#### jcmcのインストール
- setup.pyとjcmc.pyをダウンロードし、1つのディレクトリ内に配置します。
- `python setup.py install`を実行してください。

#### jcmcの簡単な使用方法
解析ファイルを作成し、jcmcをインポートして用います。
```python
from jcmc import JCMC
JCMC = JCMC('20190711.csv') #出力ファイル名を決めておきます
JCMC.export('hydrothermal')
JCMC.export('hot,spring') #複数キーワードはカンマで区切る
```
