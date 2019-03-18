/**
 * Created by gaoyue on 2018/10/15.
 */

let element;
let questionInfo;
let questionContent;
let questionType;
let questionLimitTime;
let readLimitTime;
// let questionNum = 0;
let readTip = "距离准备结束还剩：";
let answerTip = "距离回答结束还剩：";
let waitTip = "秒后开始作答";
let isWait = false;
let countDownInUse = [];
let isLastQuestion;　　　
let timer;

let nowLockIndex;

let audio_context;
let recorder;

let waitLimitTime = 10;

let canAudioUse = true;

// 先在前端保证每题只传一次
let isUpload = {};

let reTryCount = [0, 0, 0, 0], maxRetry = 10;

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

window.onbeforeunload = function (e) {
    let dialogText = '您确定现在就要结束这道题的解答吗？';
    e.returnValue = dialogText;
    return dialogText;
};


$(function () {
    layui.use('element', function () {
        element = layui.element;
    });
    if (canAudioUse) {
        getNextQuestion();
    }
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

function getNextQuestion() {
    $.post("/api/exam/next-question", {
        "nowQuestionNum": questionNum
    }).done(function (data) {
        console.log('6666');
        console.log(data.data);
        if (data["redirect"]) {
            window.onbeforeunload = null;
            window.location.href = data['url'];
            return;
        }
        questionType = data.data["questionType"];
        questionNum = data.data["questionNumber"];
        questionLimitTime = data.data["questionLimitTime"];
        readLimitTime = data.data["readLimitTime"];
        isLastQuestion = data.data["lastQuestion"];
        questionInfo = data.data["questionInfo"];
        questionContent = data.data["questionContent"];
        isUpload[questionNum] = false;
        setQuestionCover();
        setCountDown();
        countDownInUse.push(false);
        nowLockIndex++;
    }).fail(e => {
        if (reTryCount[0] < maxRetry) {
            reTry(getNextQuestion, null, 0);
        } else {
            errorTip(e);
        }
    });
}

function setQuestionCover() {
    $("#question-info-detail").html(questionInfo["detail"]);
    $("#question-info-tip").html(questionInfo["tip"]);
    $("#detail").html(questionContent);
    $("#title").html("第" + questionNum + "题");
    $("#record-group").css("display", "none");
    $("#question-cover").css("display", "");
    $("#question-content").css("display", "none");
    $("#question-summarize").css("display", "none");
    clearTimer();
}

function setCountDown() {
    $("#read-countdown").html(readTip + readLimitTime + "秒");
    $("#answer-countdown").html(answerTip + questionLimitTime + "秒");
    $("#answer-countdown-2").html(answerTip + questionLimitTime + "秒");
}

function showQuestion() {
    $("#question-cover").css("display", "none");
    $("#question-content").css("display", "");
    if (questionType > 1) {
        // 题型2、3
        $("#question-type-two").css("display", "");
        $("#question-type-one").css("display", "none");
        $("#record-group").css("display", "none");
        clearTimer();
        countDownInUse.push(true);
        nowLockIndex++;
        element.progress('read', "100%");
        isWait = false;
        startTiming(readLimitTime, readTip, 'read', '#read-countdown', nowLockIndex, () => startSummarize("skipCountDown"));
    } else {
        // 题型1
        $("#question-type-two").css("display", "none");
        $("#question-type-one").css("display", "none");
        $("#record-group").css("display", "none");
        $("#end-record").css("display", "none");
        $("#question-one-tip").css("display", "");
        $("#wait-countdown-type-1").text(readLimitTime + waitTip);
        countDownInUse.push(true);
        nowLockIndex++;
        startTimingOfTypeOne(nowLockIndex, answerNow);
    }
}

function startSummarize(arg) {
    arg = arguments[0] ? arguments[0] : 'withCountDown';
    $("#question-content").css("display", "none");
    $("#question-summarize").css("display", "");
    $("#record-group").css("display", "");
    $("#answer-part").css("display", "none");
    $("#wait-part").css("display", "");
    $("#start-record").addClass("layui-btn-disabled").attr('disabled', true);
    $("#end-record").removeClass("layui-btn-disabled").attr('disabled', false);
    clearTimer();
    countDownInUse.push(true);
    nowLockIndex++;
    element.progress('wait', "100%");
    isWait = true;
    if (arg === 'skipCountDown') {
        startRecording();
    } else {
        startTiming(waitLimitTime, waitTip, 'wait', '#wait-countdown', nowLockIndex, startRecording);
    }
}

function startRecording() {
    // 开始录音
    audio_context.resume().then(() => {
        recorder && recorder.record();
        console.log("start recording...");
    });
    // 修改页面样式
    $("#start-record").css("display", "none");
    $("#end-record").css("display", "").removeClass("layui-btn-disabled").attr('disabled', false);
    $("#answer-part").css("display", "");
    $("#wait-part").css("display", "none");

    let mic, fil, sound, answer;
    if (questionType > 1) {
        mic = "#microphone-2";
        fil = "#answer-countdown-2";
        sound = "#sound-2-";
        answer = "answer-2";
    } else {
        mic = "#microphone";
        fil = "#answer-countdown";
        sound = "#sound-";
        answer = "answer";
    }
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
    if (isUpload[questionNum]) {
        console.log(isUpload);
        console.log("end recording: repeat; " + questionNum);
        return;
    }
    // 结束录音
    recorder && recorder.stop();
    console.log("end recording.");
    // 修改样式
    $("#end-record").addClass("layui-btn-disabled").attr('disabled', true);
    $("#microphone").css("color", "white");
    for (let i = 1; i < 10; i++) {
        $("#sound-" + i).css("color", "white")
    }
    $("#microphone-2").css("color", "white");
    for (let i = 1; i < 10; i++) {
        $("#sound-2-" + i).css("color", "white")
    }

    clearTimer();
    // 先存下这题的题号
    let nowQuestionNum = questionNum;
    let lastQuestion = isLastQuestion;
    console.log("question number: " + nowQuestionNum);
    if (!lastQuestion) {
        getNextQuestion();
    } else {
        layer.load(1);
    }
    // 上传音频
    if (!isUpload[nowQuestionNum]) {
        recorder.exportWAV((blob) => uploadVideo(blob, nowQuestionNum, lastQuestion));
        recorder.clear();
        isUpload[nowQuestionNum] = true;
    }
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
        $('#answer-countdown-2').text(answerTip + questionLimitTime + '秒');
        $('#read-countdown').text(readTip + readLimitTime + '秒');
        $('#wait-countdown').text(waitLimitTime + '秒' + waitTip);
    }
    element.progress('read', "100%");
    element.progress('answer', "100%");
    element.progress('answer-2', "100%");
    element.progress('wait', "100%");
}

function uploadVideo(blob, nowQuestionNum, lastQuestion) {
    // 首先向后端拿到上传url
    console.log("question number inner: " + nowQuestionNum);
    console.log("blob: " + blob);
    $.post("/api/exam/get-upload-url", {
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
                $.post("/api/exam/upload-success", {"nowQuestionNum": nowQuestionNum}).done(function (data) {
                    console.log(data);
                    if (lastQuestion) {
                        //layer.closeAll('loading');
                        window.onbeforeunload = null;
                        window.location.href = '/result'
                    }
                }).fail(e => {
                    if (reTryCount[1] < maxRetry) {
                        console.log("innerRetry");
                        reTry(([blob, nowQuestionNum, lastQuestion]) => uploadVideo(blob, nowQuestionNum, lastQuestion), [blob, nowQuestionNum, lastQuestion], 1);
                    } else {
                        errorTip(e);
                        console.log("upload success fail callback");
                        if (lastQuestion) {
                            //layer.closeAll('loading');
                            window.onbeforeunload = null;
                            window.location.href = '/result'
                        }
                    }
                });
            },
            error: e => {
                if (reTryCount[2] < maxRetry) {
                    console.log("outRetry");
                    reTry(([blob, nowQuestionNum, lastQuestion]) => uploadVideo(blob, nowQuestionNum, lastQuestion), [blob, nowQuestionNum, lastQuestion], 2);
                } else {
                    errorTip(e);
                }
            }
        })
    }).fail(e => {
        if (reTryCount[3] < maxRetry) {
            console.log("outRetry");
            reTry(([blob, nowQuestionNum, lastQuestion]) => uploadVideo(blob, nowQuestionNum, lastQuestion), [blob, nowQuestionNum, lastQuestion], 3);
        } else {
            errorTip(e);
        }
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
    // console.log(sound);
    let soundId = questionType > 1 ? "#sound-2-" : "#sound-";
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
        layer.msg("服务器出错了");
    }
}

function reTry(func, arg, index) {
    reTryCount[index]++;
    console.log(func);
    console.log(arg);
    console.log(reTryCount);
    setTimeout(() => func(arg), 500);
}

function browserError() {
    layer.open({
        title: ['提示信息', 'font-size:16px;'],
        type: 1,
        content: "<div style='padding: 30px 20px; font-size: 16px'>您的浏览器暂不支持录音，请更换到最新版本的chrome浏览器。</div>",
        btn: '我知道了',
        yes: function () {
            window.onbeforeunload = null;
            window.location.href = '/user';
        },
        closeBtn: 0,
        resize: false,
        scrollbar: false,
        move: false,
    });
}

function answerNow() {
    clearTimer();
    // 题型1
    $("#question-type-two").css("display", "none");
    $("#question-type-one").css("display", "");
    $("#question-one-tip").css("display", "none");
    $("#record-group").css("display", "");
    startRecording();

}

function startTimingOfTypeOne(index, callback) {
    let _callback = callback || (() => callback);
    let countDownTime = readLimitTime;
    layui.use('util', function () {
        let util = layui.util;
        let nowTime = new Date().getTime();
        let endTime = nowTime + 1000 * readLimitTime;
        util.countdown(endTime, nowTime, function (date, serverTime) {
            let str = date[2] * 60 + date[3] + "";
            if (date[3] < countDownTime && date[3] > 0 && countDownInUse[index]) {
                $("#wait-countdown-type-1").text(str + waitTip);
            }
            if (endTime === serverTime && countDownInUse[index]) {
                _callback();
            }
        });
    });
}