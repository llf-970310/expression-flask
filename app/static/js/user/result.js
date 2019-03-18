let myChart = echarts.init(document.getElementById('radar'));
let chartData;
let totalScore;
let timer;
let layer;

let counter = 0;

let timeLimit = 120 * 1000; // 120秒超时

let queryTime = 500; // 每0.5秒轮询一次

$(function () {
    layui.use('layer', function () {
        layer = layui.layer;

    });
    layer.load(1);

    queryResult();
});

function queryResult() {
    // 超时就不再轮训
    if (counter * queryTime > timeLimit) {
        errorTip("timeout");
        return;
    }
    $.post("/api/exam/get-result", {}).done(function (data) {
        counter++;
        console.log(counter);
        let status = data['status'];
        if (status === "Success") {
            clearInterval(timer);
            layer.closeAll('loading');
            chartData = data['data'];
            console.log(data);
            console.log(chartData);
            totalScore = data['totalScore'];
            displayChart();
        } else {
            counter++;
            setTimeout(queryResult, queryTime);
        }
    }).fail(e => {
        errorTip(e);
    });
}

function displayChart() {
    $("#total-score").html("总得分：" + totalScore.toFixed(2) + "分");
    let indicator = [];
    let value = [];
    Object.keys(chartData).forEach(function (key) {
        indicator.push({name: key, max: 100});
        value.push(chartData[key].toFixed(2));
    });
    let option = {
        title: {
            text: '各项得分'
        },
        tooltip: {},
        radar: {
            // shape: 'circle',
            name: {
                textStyle: {
                    color: '#fff',
                    backgroundColor: '#999',
                    borderRadius: 3,
                    padding: [3, 5]
                }
            },
            indicator: indicator
        },
        series: [{
            type: 'radar',
            // areaStyle: {normal: {}},
            data: [
                {
                    value: value,
                    name: '得分情况',
                    label: {
                        normal: {
                            show: true,
                            formatter: function (params) {
                                return params.value;
                            }
                        }
                    }
                }
            ]
        }]
    };

    myChart.setOption(option);
}


function returnIndex() {
    window.location.href = "/";
}

function logout() {
    window.location.href = "/";
}

function errorTip(e) {
    try {
        if (e === 'timeout') {
            layer.msg("获取结果超时");
            $("#total-score").html("服务器正忙，请稍后刷新重试");
            clearInterval(timer);
            layer.closeAll('loading');
            return;
        }
        let response = JSON.parse(e.responseText);
        console.log(typeof response);
        if (response['needDisplay']) {
            layer.msg(response['tip']);
            $("#total-score").html("处理出错，请重新测试");
        } else {
            layer.msg("服务器出错了");
            $("#total-score").html("处理出错，请重新测试");
        }
    } catch (e) {
        console.log(e);
        layer.msg("服务器出错了");
        $("#total-score").html("处理出错，请重新测试");
    } finally {
        clearInterval(timer);
        layer.closeAll('loading');
    }
}
