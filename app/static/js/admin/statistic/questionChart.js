let questionScoreChart = echarts.init(document.getElementById('question-score-chart'), "macarons");

function fillHist(obj, num) {
    for (let key in obj) {
        if (num <= parseInt(key) + 10) {
            obj[key]++;
            console.log("num: " + num + ", key: " + key + ", obj: " + obj);
            return;
        }
    }
}

function initQuestionChartData(data) {
    let detail, main, total;
        detail = {"10": 0, "30": 0, "50": 0, "70": 0, "90": 0};
        main = {"10": 0, "30": 0, "50": 0, "70": 0, "90": 0};
        total = {"10": 0, "30": 0, "50": 0, "70": 0, "90": 0};
        for (let i = 0; i < data.length; i++) {
            fillHist(detail, data[i]["detail"]);
            fillHist(main, data[i]["main"]);
            fillHist(total, data[i]["total"]);
        }

        let detailBin = [], mainBin = [], totalBin = [];
        for (let key in detail) {
            detailBin.push(detail[key]);
        }
        for (let key in main) {
            mainBin.push(main[key]);
        }
        for (let key in total) {
            totalBin.push(total[key]);
        }

        let option = {
            title: {
                text: '得分频率分布图',
                left: 'center',
                top: 20
            },
            legend: {
                data: ['细节', '主旨', '总分']
            },
            tooltip: {
                trigger: 'axis'
            },
            calculable: true,
            xAxis: [{
                type: 'category',
                scale: true,
                data: ['0 ~ 20分', '20 ~ 40分', '40 ~ 60分', '60 ~ 80分', '80 ~ 100分']
            }],
            yAxis: [{
                type: 'value',
                axisLabel: {
                    formatter: '{value} 人'
                }
            }],
            toolbox: {
                show: true,
                feature: {
                    mark: {show: true},
                    dataView: {show: true, readOnly: false},
                    magicType: {show: true, type: ['line', 'bar']},
                    restore: {show: true},
                    saveAsImage: {show: true}
                }
            },
            series: [{
                name: '细节',
                type: 'line',
                label: {
                    normal: {
                        show: true,
                        position: 'insideTop',
                        formatter: function (params) {
                            return params.value[1];
                        }
                    }
                },
                data: detailBin
            },
                {
                    name: '主旨',
                    type: 'line',
                    label: {
                        normal: {
                            show: true,
                            position: 'insideTop',
                            formatter: function (params) {
                                return params.value[1];
                            }
                        }
                    },
                    data: mainBin
                },
                {
                    name: '总分',
                    type: 'line',
                    label: {
                        normal: {
                            show: true,
                            position: 'insideTop',
                            formatter: function (params) {
                                return params.value[1];
                            }
                        }
                    },
                    data: totalBin
                }]
        };
        questionScoreChart.setOption(option);
}

function initQuestionChart(questionId) {
    $.get("/admin/api/get-question-score", {
        questionId: questionId
    }).done(function (data) {
        initQuestionChartData(data);
    });


}