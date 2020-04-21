# 概要
本プロジェクトはFlaskをAzure Functions上で動かすためのもの

Azure Functions
https://azure.microsoft.com/ja-jp/services/functions/

## Requirements
#### node
参考:  
https://qiita.com/kyosuke5_20/items/c5f68fc9d89b84c0df09

#### Azure CLI / Azure Functions Core Tools
参考:  
https://qiita.com/tworks55/items/281beeea5fd6c105b0b1

#### PowerShell Core
参考:  
https://github.com/powershell/powershell

#### Azure アカウント
ターミナル上で
```
$ az login
```
と入力すると認証が可能

## プロジェクト開始手順
参考記事
https://kapiecii.hatenablog.com/entry/2019/08/10/110000

#### プロジェクトの作成
```
$ func init SampleProject

Select a number for worker runtime:
1. dotnet
2. node
3. python
4. powershell
Choose option: 3 # Python なので3を指定
python
Found Python version 3.6.9 (python).
Writing .gitignore
Writing host.json
Writing local.settings.json
Writing /Users/radius5/workspace/azure_functions_flask_sample/SampleProject/.vscode/extensions.json
```

SampleProjectが作成される
```
$ tree
.
├── README.md
└── SampleProject
    ├── host.json
    ├── local.settings.json
    └── requirements.txt

1 directory, 4 files
```

#### プロジェクトにFunctionを追加

```
cd SampleProject
func new

Select a number for template:
1. Azure Blob Storage trigger
2. Azure Cosmos DB trigger
3. Azure Event Grid trigger
4. Azure Event Hub trigger
5. HTTP trigger
6. Azure Queue Storage trigger
7. Azure Service Bus Queue trigger
8. Azure Service Bus Topic trigger
9. Timer trigger
Choose option: 5 # Flask の Webサーバーを立てたいので5を指定
HTTP trigger
Function name: [HttpTrigger] SampleAPI # Function名を指定
Writing /Users/radius5/workspace/azure_functions_flask_sample/SampleProject/SampleAPI/__init__.py
Writing /Users/radius5/workspace/azure_functions_flask_sample/SampleProject/SampleAPI/function.json
The function "SampleAPI" was created successfully from the "HTTP trigger" template.
```

フォルダ構成
```
tree
.
├── SampleAPI
│   ├── __init__.py
│   └── function.json
├── host.json
├── local.settings.json
└── requirements.txt
```
requirements.txt には pythonで使用するライブラリを入力
ローカルではローカルのpythonが使われるが、デプロイ時はrequirements.txtに記載したライブラリがインストールされてからプログラムが実行される


```__init__.py
import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello {name}!")
    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )
```


#### ローカルでFunctionを起動する
```
func host start
```
アクセスするURLがターミナルに表示される

Now listening on: http://0.0.0.0:7071
Application started. Press Ctrl+C to shut down.

Http Functions:

	SampleAPI: [GET,POST] http://localhost:7071/api/SampleAPI

このURLにアクセスすると、 `__init__.py` が実行される

#### __init__.pyをFlaskを利用した形に書き換え
クエリ文字列で渡されたuriを参照して、Flaskを使ってroutingするようにする
```
import logging
import azure.functions as func
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/hi')
def hi():
    return 'Hi World!'

@app.route('/hello')
@app.route('/hello/<name>', methods=['POST', 'GET'])
def hello(name=None):
    return name != None and 'Hello, '+name or 'Hello, '+request.args.get('name')

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    uri=req.params['uri']
    with app.test_client() as c:
        doAction = {
            "GET": c.get(uri).data,
            "POST": c.post(uri).data
        }
        resp = doAction.get(req.method).decode()
        return func.HttpResponse(resp, mimetype='text/html')
```

アクセス用URL
http://localhost:7071/api/SampleAPI?uri=/
http://localhost:7071/api/SampleAPI?uri=/hi
http://localhost:7071/api/SampleAPI?uri=/hello/hoge

#### デプロイ
デプロイするにはデプロイ先のアカウントを指定するために認証が必要
```
$ az login
```
と起動すると、Terminalからブラウザが立ち上がり認証ができる。


事前に関数AppをWebUI上から作成しておき、以下のように入力
(azure-function-app-nameは作成した関数Appの名前)
```
func azure functionapp publish azure-function-app-name
```
このコマンドで、カレントディレクトリのプロジェクトの内容を、
azure-function-app-name にデプロイができる

#### デプロイ時のURLの確認
WebUIからAzure FunctionsのURLを確認
アクセスするときに認証コードがいるため、認証コード付きのURLを確認する
認証コードもクエリ文字列として渡すので、`&` で `uri` と一緒に渡す必要があることに注意

▼URL
https://azure-function-app-name.azurewebsites.net/api/SampleAPI?code=[認証コード]&uri=/
https://azure-function-app-name.azurewebsites.net/api/SampleAPI?code=[認証コード]&uri=/hi
https://azure-function-app-name.azurewebsites.net/api/SampleAPI?code=[認証コード]&uri=/hello/hoge