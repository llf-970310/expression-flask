## 说明

### analysis-docker

评分子项目，作为submodule引入，**不应依赖于其他模块**，**针对该模块做开发时，应单独打开子项目进行**。



### app

网页flask后台模块，如需在该模块中引用评分模块代码，可参考如下引用方式(已在 `app/__init__.py` 中包含)：

```python
import os
import sys
prj_folder = os.path.abspath(__file__).split('/app/__init__.py')[0]
analysis_docker_folder = (os.path.join(prj_folder, 'analysis-docker'))
sys.path.append(analysis_docker_folder)

# import expression
```





**考虑如何重用代码，不要写重复代码**





## Git子模块的更新

在许多开发项目中,我们通常都希望主项目所集成的始终是子模块的当前最新版本。

git 的子模块不支持这种想法，子模块引用的只是模块版本库中的某一次提交，模块版本库中随后的新提交并不会自动记录到主版本库中，所以需要我们显示的修改更新子模块。

更新子模块后，首先把子模块提交到仓库。

然后在当前项目添加子模块，如 git add analysis-docker，然后commit并提交。

```bash
git add analysis-docker
git commit -m 'New version of analysis-docker'
git push
```

然后即建立起当前项目到新版本子模块的引用，在服务器的当前项目文件夹中使用如下命令即可更新子模块代码：

```bash
git submodule update
```





## Hosts 配置

`expression-flask` 代码中使用助记符号代替ip地址，为保证正常解析，应在系统hosts文件添加如下内容：

(注意：下面仅为示例，需要修改ip为实际部署相应服务的服务器ip)

```
47.98.174.59  redis-server.expression.hosts
47.98.174.59  mongo-server.expression.hosts
47.98.174.59  flask-server.expression.hosts
```

