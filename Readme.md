## 说明

### analysis-docker

评分子项目，作为submodule引入，**不应依赖于其他模块**，**针对该模块做开发时，应在原项目中进行**。



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

