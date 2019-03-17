let element;
let questionInfo;
let questionContent;
let questionType;
let questionLimitTime;
let readLimitTime;
// let questionNum = 0;
let readTip = "距离准备结束还剩：";
let answerTip = "距离回答结束还剩：";
let countDownInUse = [];
let isLastQuestion;
let timer;

let nowLockIndex;

let audio_context;
let recorder;

let canAudioUse = true;

let counter = 0;
let timeLimit = 120 * 1000; // 120秒超时
let queryTime = 500; // 每0.5秒轮询一次

window.onload = function init() {
    try {
        // webkit shim
        window.AudioContext = window.AudioContext || window.webkitAudioContext;
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
        window.URL = window.URL || window.webkitURL;

        audio_context = new AudioContext;
        console.log('Audio context set up.');
        console.log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
        if (!navigator.getUserMedia) {
            canAudioUse = false;
            browserError();
            return;
        }
    } catch (e) {
        canAudioUse = false;
        browserError();
        return;
    }

    try {
        navigator.getUserMedia({audio: true}, startUserMedia, function (e) {
            console.log('No live audio input: ' + e);
        });
    } catch (e) {
        canAudioUse = false;
        browserError();
    }
};

// window.onbeforeunload = function (e) {
//     let dialogText = '您确定现在就要结束这道题的解答吗？';
//     e.returnValue = dialogText;
//     return dialogText;
// };


$(function () {
    layui.use(['form', 'element'], function () {
        let form = layui.form;
        element = layui.element;

        //监听提交
        form.on('submit(formGetQuestion)', function (data) {
            console.log(data);
            console.log(data.field);
            getQuestion(data.field["questionId"]);
            return true;
        });
    });
    nowLockIndex = -1;
});

function startUserMedia(stream) {
    let input = audio_context.createMediaStreamSource(stream);
    console.log('Media stream created.');

    recorder = new Recorder(input, {
        onAudioProcess: onAudioProcess
    });
    console.log('Recorder initialised.');
}

function getQuestion(questionId) {
    $.post("/api/admin/get-question", {
        "questionId": questionId
    }).done(function (data) {
        console.log(data);
        if (data["redirect"]) {
            // window.onbeforeunload = null;
            window.location.href = data['url'];
            return;
        }
        questionType = data["questionType"];
        questionNum = data["questionNumber"];
        questionLimitTime = data["questionLimitTime"];
        readLimitTime = data["readLimitTime"];
        isLastQuestion = data["lastQuestion"];
        questionInfo = data["questionInfo"];
        questionContent = data["questionContent"];
        setCountDown();
        showQuestion();
        countDownInUse.push(false);
        nowLockIndex++;
    }).fail(e => {
        errorTip(e);
    });
}

function setCountDown() {
    $("#read-countdown").html(readTip + readLimitTime + "秒");
    $("#answer-countdown").html(answerTip + questionLimitTime + "秒");
}

function showQuestion() {
    // 恢复result table
    let tr = $("tr");
    if (tr.length > 7) {
        tr.slice(7 - tr.length).remove();
    }

    $("#error-return-tip").css("display", "none");
    $("#empty-tip").css("display", "none");
    $("#question-content").css("display", "");
    $("#read-part").css("display", "");
    $("#summary").css("display", "none");
    $("#record-group").css("display", "none");
    $("#result").css("display", "none");
    $("#detail").html(questionContent);
    clearTimer();
    countDownInUse.push(true);
    nowLockIndex++;
    element.progress('read', "100%");
    isWait = false;
    startTiming(readLimitTime, readTip, 'read', '#read-countdown', nowLockIndex, startSummarize);

}

function startSummarize() {
    $("#error-return-tip").css("display", "none");
    $("#empty-tip").css("display", "none");
    $("#question-content").css("display", "none");
    $("#read-part").css("display", "none");
    $("#summary").css("display", "");
    $("#record-group").css("display", "");
    $("#result").css("display", "none");
    $("#end-record").css("display", "").removeClass("layui-btn-disabled").attr('disabled', false);
    clearTimer();
    countDownInUse.push(true);
    nowLockIndex++;
    startRecording();
}

function startRecording() {
    // 开始录音
    audio_context.resume().then(() => {
        recorder && recorder.record();
        console.log("start recording...");
    });

    let mic, fil, sound, answer;
    mic = "#microphone";
    fil = "#answer-countdown";
    sound = "#sound-";
    answer = "answer";
    $(mic).css("color", "#333333");
    for (let i = 1; i < 10; i++) {
        $(sound + i).css("color", "#cdcdcd")
    }
    clearTimer();
    countDownInUse.push(true);
    nowLockIndex++;
    element.progress(answer, "100%");
    isWait = false;
    startTiming(questionLimitTime, answerTip, answer, fil, nowLockIndex, endRecording);
}

function endRecording() {
    console.log("=======end recording========");
    // 结束录音
    recorder && recorder.stop();
    console.log("end recording.");
    // 修改样式
    $("#end-record").addClass("layui-btn-disabled").attr('disabled', true);
    $("#microphone").css("color", "white");
    for (let i = 1; i < 10; i++) {
        $("#sound-" + i).css("color", "white")
    }

    clearTimer();
    // 先存下这题的题号
    let nowQuestionNum = questionNum;
    console.log("question number: " + nowQuestionNum);
    layer.load(1);
    // 上传音频
    recorder.exportWAV((blob) => uploadVideo(blob, nowQuestionNum));
    recorder.clear();
}

function startTiming(countDownTime, tipStr, filter, tipId, index, callback) {
    let _callback = callback || (() => callback);
    layui.use('util', function () {
        let util = layui.util;
        let nowTime = new Date().getTime();
        let endTime = nowTime + 1000 * countDownTime;
        timer = setInterval(() => process(endTime, countDownTime, filter), 80);
        util.countdown(endTime, nowTime, function (date, serverTime) {
            let str = date[2] * 60 + date[3] + '秒';
            if (date[3] < countDownTime && date[3] > 0 && countDownInUse[index]) {
                if (!isWait) {
                    $(tipId).text(tipStr + str);
                } else {
                    $(tipId).text(str + tipStr);
                }
            }
            if (endTime === serverTime && countDownInUse[index]) {
                _callback();
            }
        });
    });
}

function process(endTime, countDownTime, filter) {
    let percent = (endTime - new Date().getTime()) / (1000 * countDownTime) * 100;
    element.progress(filter, percent + "%");
}

function clearTimer() {
    for (let i = 0; i < countDownInUse.length; i++) {
        countDownInUse[i] = false;
    }
    if (timer) {
        clearInterval(timer);
        timer = null;
        console.log(countDownInUse);
    }
    resetCountDown();
}

function resetCountDown() {
    if (questionType > 1) {
        $('#answer-countdown').text(answerTip + questionLimitTime + '秒');
        $('#read-countdown').text(readTip + readLimitTime + '秒');
    }
    element.progress('read', "100%");
    element.progress('answer', "100%");
}

function uploadVideo(blob, nowQuestionNum) {
    // 首先向后端拿到上传url
    console.log("question number inner: " + nowQuestionNum);
    $.post("/api/get-upload-url", {
        "nowQuestionNum": nowQuestionNum
    }).done(function (data) {
        let url = data["url"];
        let fd = new FormData();
        fd.append("video", blob);
        fd.append("nowQuestionNum", nowQuestionNum);
        $.ajax({
            url: url,
            type: 'post',
            processData: false,
            contentType: false,
            data: fd,
            success: function () {
                // stub maybe
                $.post("/api/upload-success", {"nowQuestionNum": nowQuestionNum}).done(function (data) {
                    console.log(data);
                    showResult()
                }).fail(e => {
                    layer.closeAll('loading');
                    $("#error-return-tip").css("display", "");
                    errorTip(e);
                    console.log("upload success fail callback");
                });
            },
            error: e => {
                errorTip(e);
            }
        })
    }).fail(e => {
        errorTip(e);
    });
}

function onAudioProcess(data) {
    let avg = 0;
    let max_data = 0;
    for (let i = 0; i < data.length; i++) {
        let temp = Math.abs(data[i]);
        avg += temp;
        max_data = Math.max(max_data, temp)
    }
    avg /= data.length;
    let sound = avg * 80;
    let soundId = "#sound-";
    for (let i = 1; i < 10; i++) {
        if (i < sound) {
            $(soundId + i).css("color", "rgb(95, 169, 249)");
        } else {
            $(soundId + i).css("color", "#cdcdcd");
        }
    }
}

function errorTip(e) {
    try {
        let response = JSON.parse(e.responseText);
        console.log(typeof response);
        if (response['needDisplay']) {
            layer.msg(response['tip']);
        } else {
            layer.msg("服务器出错了");
        }
    } catch (e) {
        console.log(e);
        layer.msg("服务器出错了");
    }
}

function browserError() {
    layer.open({
        title: ['提示信息', 'font-size:16px;'],
        type: 1,
        content: "<div style='padding: 30px 20px; font-size: 16px'>您的浏览器暂不支持录音，请更换到最新版本的chrome浏览器。</div>",
        btn: '我知道了',
        yes: function () {
            // window.onbeforeunload = null;
            window.location.href = '/user';
        },
        closeBtn: 0,
        resize: false,
        scrollbar: false,
        move: false,
    });
}

function showResult() {
    if (counter * queryTime > timeLimit) {
        errorTip("timeout");
        return;
    }
    // stub maybe
    $.post("/api/admin/get-result", {}).done(function (data) {
        counter++;
        console.log(counter);
        let status = data['status'];
        if (status === "Success") {
            layer.closeAll('loading');
            displayTable(data['result']);
        } else {
            counter++;
            setTimeout(showResult, queryTime);
        }
    }).fail(e => {
        errorTip(e);
    });
}

function displayTable(tableData) {
    $("#error-return-tip").css("display", "none");
    $("#empty-tip").css("display", "none");
    $("#question-content").css("display", "none");
    $("#read-part").css("display", "none");
    $("#summary").css("display", "none");
    $("#record-group").css("display", "none");
    $("#result").css("display", "");
    $("#main-score").text(tableData["main"].toFixed(2));
    $("#detail-score").text(tableData["detail"].toFixed(2));
    $("#score").text(tableData["total"].toFixed(2));
    $("#rcg-text").text(tableData["rcgText"]);
    $("#raw-text").text(tableData["text"]);
    // 击中词库的显示
    $("#keywords").html(wrapHitItem(tableData["keyWords"], tableData["rcgKeyWords"]));
    $("#main-words").html(wrapHitItem(tableData["mainWords"], tableData["rcgMainWords"]));
    let detail = tableData["detailWords"];
    let rcgDetail = tableData["rcgDetailWords"];
    let detailHtml = "";
    for (let i = 0; i < detail.length; i++) {
        detailHtml += `<tr><td class="layui-table-header">${"detailwords" + (i + 1) + "<br/>击中情况"}</td><td>${wrapHitItem(detail[i], rcgDetail[i])}</td></tr>`;
    }
    $("#result-body").append(detailHtml);
}

function wrapHitItem(rawWords, hitWords) {
    let res = '';
    for (let i = 0; i < hitWords.length; i++) {
        if (i > 0) {
            res += '，';
        }
        for (let j = 0; j < rawWords[i].length; j++) {
            if (j === 0) {
                res += '[ ';
            }
            if (hitWords[i] === rawWords[i][j]) {
                res += `<i class="hit">${hitWords[i]}</i>`;
            } else {
                res += `<i class="no-hit">${rawWords[i][j]}</i>`;
            }
            if (j === rawWords[i].length - 1) {
                res += ' ]';
            } else {
                res += ' ';
            }
        }
    }
    return res;
}