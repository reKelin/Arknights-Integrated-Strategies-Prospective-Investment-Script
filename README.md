# 明日方舟 集成战略 前瞻性投资系统 自动投资脚本

## 使用说明

1.   在 Airtest 官网上下载 AirtestIDE 并解压（[下载链接](https://airtest.netease.com/changelog.html)）。

1.   下载脚本源码并解压。

1.   打开 AirtestIDE ，点击文件，点击打开脚本

     <img src="https://github.com/reKelin/Arknights-Integrated-Strategies-Prospective-Investment-Script/blob/main/readme_files/文件-打开脚本.png" />

     点击对应肉鸽的 .air 文件夹，点击 OK 载入脚本。

     <img src="https://github.com/reKelin/Arknights-Integrated-Strategies-Prospective-Investment-Script/blob/main/readme_files/选择脚本.png"/>

1.   打开模拟器，找到模拟器对应的序列号，如 "emulator-xxxx" ，点击 connect 连接模拟器。

     <img src="https://github.com/reKelin/Arknights-Integrated-Strategies-Prospective-Investment-Script/blob/main/readme_files/连接模拟器.png" />

     如果没有序列号，可以尝试点击下方的“重启ADB”。

1.   打开肉鸽界面，难度选择普通难度（如“波涛迭起 0”，”正式调查“），确保有”开始探索“，如下图所示

     <img src="https://github.com/reKelin/Arknights-Integrated-Strategies-Prospective-Investment-Script/blob/main/readme_files/肉鸽主界面示例.png" />

1.   可以在 .air 目录下查看默认配置文件 default_setting.json ，包含默认编队和默认等待时间，如下图所示：

     <img src="https://github.com/reKelin/Arknights-Integrated-Strategies-Prospective-Investment-Script/blob/main/readme_files/默认配置1.png">

     默认等待时间表示一次点击后的等待时间，单位为秒。如果设备比较卡，建议调大一点，比如 1 。

     由于实际上第一层普通难度非常简单，正常情况下单近卫即可通关，所以实际上默认配置为

     <img src="https://github.com/reKelin/Arknights-Integrated-Strategies-Prospective-Investment-Script/blob/main/readme_files/默认配置2.png">

     如果无需修改编队，可以直接跳到下一点阅读。

     可以自己对编队进行调整，但是**请务必确保编队**为 **[近卫, 辅助, 医疗]** 或 **[近卫, 辅助]** 或 **[近卫]** 。其中目前所有支持选用的干员都在 operator.json 中，目前仅支持：

     1.   近卫：山2技能，耀骑士临光1技能，煌2技能，百炼嘉维尔2技能，羽毛笔1技能，海沫1技能
     2.   辅助：梓兰
     3.   医疗：安赛尔

     如需添加或调整，可以根据 json 中的格式修改，**请务必确保格式一致**，并在 images 文件夹中添加干员在**招募界面**和**助战界面**的**名字截图**（尽量保证和现有的格式一致，以提高识别准确率）。

1.   点击“运行脚本”或按 F5 运行脚本。

     <img src="https://github.com/reKelin/Arknights-Integrated-Strategies-Prospective-Investment-Script/blob/main/readme_files/运行脚本.png">

     遇到脚本卡死或者其他特殊情况，点击“停止脚本”或按 Shift+F5 停止运行脚本。

     <img src="https://github.com/reKelin/Arknights-Integrated-Strategies-Prospective-Investment-Script/blob/main/readme_files/停止运行.png"/>

## 注意事项

1.   分辨率太奇怪了（超宽屏，超窄屏）作战中的定位点会出错，目前主流的模拟器的默认分辨率都能够较好的支持。

2.   如果出现 BUG ，可以按如下方式点击或按 Ctrl+L 生成报告。

     <img src="https://github.com/reKelin/Arknights-Integrated-Strategies-Prospective-Investment-Script/blob/main/readme_files/打开报告.png"/>

     然后将报告中的错误信息截图，提交 issues ，截图示例如下：

     <img src="https://github.com/reKelin/Arknights-Integrated-Strategies-Prospective-Investment-Script/blob/main/readme_files/BUG截图示例.png"/>
