let table, form, questionData, element;

let detailIdList = [];

$(function () {
    layui.use(['form', 'table', 'element'], function () {
        table = layui.table;
        form = layui.form;
        element = layui.element;
        //监听提交
        form.on('submit(formGetQuestion)', function (data) {
            initTableFromServer(true, data.field["questionId"]);
            initQuestionChart(data.field["questionId"]);
            return true;
        });

        // table
        table.render({
            elem: '#question-table-page'
            , height: 600
            , url: '/admin/api/get-question-page' //数据接口
            , page: true //开启分页
            , toolbar: true
            , limit: 50
            , title: "题目列表"
            , cols: [[ //表头
                {field: 'questionId', title: '题号', sort: true, width: 70}
                , {field: 'rawText', title: '题目原文'}
                , {field: 'keywords', title: 'keywords'}
                , {field: 'mainwords', title: 'mainwords'}
                , {field: 'detailwords', title: 'detailwords'}
            ]]
        });
    });
});

function initTableFromServer(noBackup, questionId, url) {
    let _url = url || "/admin/api/get-question-content";
    $.get(_url, {"questionId": questionId}).done((data) => {
        console.log(data);
        questionData = data;
        initTable(noBackup);
    }).fail(e => {
        try {
            let response = JSON.parse(e.responseText);
            if (response['needDisplay']) {
                layer.msg(response['tip']);
            } else {
                layer.msg("服务器出错了");
            }
        } catch (e) {
            layer.msg("服务器出错了");
        }
    });
}

function initTable(noBackup) {
    // 恢复result table
    let tr = $("#question-table tr");
    if (tr.length > 3) {
        tr.slice(3 - tr.length).remove();
    }

    $("#qn").text(`题号：${questionData['questionId']}`);

    $("#search-tip").css("display", "none");
    $("#question-table").css("display", "");
    $("#add-question").css("display", "none");

    // text
    $("#raw-text").val(questionData['rawText']);

    // keywords
    let keywords = ``;
    for (let i = 0; i < questionData['keywords'].length; i++) {
        let wordList = questionData['keywords'][i];
        keywords += `<div class="word-list">[`;
        for (let j = 0; j < wordList.length; j++) {
            keywords += `<input type="text" required lay-verify="required" class="word-item" value="${wordList[j]}" placeholder="输入词语"/>
                    <i class="delete-tip" onmouseenter="setBg(this)" onmouseleave="removeBg(this)" title="删除词语" onclick="deleteWord(this)">&#xe60e;</i><i class="delete-tip-bg">&#xe650;</i>`;
        }
        keywords += `<button class="layui-btn layui-btn-primary layui-btn-xs add-tip" onclick="addWord(this)">+ 添加词语</button>]</div><br />`;
    }
    keywords += `<button class="layui-btn layui-btn-primary layui-btn-xs add-tip" onclick="addWordList(this)" style="margin-left: 10px; margin-bottom: 4px; margin-top: 5px;">+ 添加词语列表</button>`;
    $("#keywords").empty().append(keywords);

    // mainwords
    let mainwords = ``;
    for (let i = 0; i < questionData['mainwords'].length; i++) {
        let wordList = questionData['mainwords'][i];
        mainwords += `<div class="word-list">[`;
        for (let j = 0; j < wordList.length; j++) {
            mainwords += `<input type="text" required lay-verify="required" class="word-item" value="${wordList[j]}" placeholder="输入词语"/>
                    <i class="delete-tip" onmouseenter="setBg(this)" onmouseleave="removeBg(this)" title="删除词语" onclick="deleteWord(this)">&#xe60e;</i><i class="delete-tip-bg">&#xe650;</i>`;
        }
        mainwords += `<button class="layui-btn layui-btn-primary layui-btn-xs add-tip" onclick="addWord(this)">+ 添加词语</button>]</div><br />`;
    }
    mainwords += `<button class="layui-btn layui-btn-primary layui-btn-xs add-tip" onclick="addWordList(this)" style="margin-left: 10px; margin-bottom: 4px; margin-top: 7px;">+ 添加词语列表</button>`;
    $("#mainwords").empty().append(mainwords);

    // detail
    let detailwords = '';
    detailIdList = [];
    for (let i = 0; i < questionData['detailwords'].length; i++) {
        let detailBar = questionData['detailwords'][i];
        detailwords += `<tr><td class="layui-table-header table-head">detailwords ${i + 1}</td><td id="detailwords${i + 1}">`;
        detailIdList.push(`detailwords${i + 1}`);
        for (let j = 0; j < detailBar.length; j++) {
            let detailList = detailBar[j];
            detailwords += `<div class="word-list"">[`;
            for (let k = 0; k < detailList.length; k++) {
                detailwords += `<input type="text" required lay-verify="required" class="word-item" value="${detailList[k]}" placeholder="输入词语"/>
                    <i class="delete-tip" onmouseenter="setBg(this)" onmouseleave="removeBg(this)" title="删除词语" onclick="deleteWord(this)">&#xe60e;</i><i class="delete-tip-bg">&#xe650;</i>`;
            }
            detailwords += `<button class="layui-btn layui-btn-primary layui-btn-xs add-tip" onclick="addWord(this)">+ 添加词语</button>]</div><br />`;
        }
        detailwords += `<button class="layui-btn layui-btn-primary layui-btn-xs add-tip" onclick="addWordList(this)" style="margin-left: 10px; margin-bottom: 4px; margin-top: 7px;">+ 添加词语列表</button>
                        <button class="layui-btn layui-btn-primary layui-btn-xs add-tip delete-btn" onclick="deleteDetailList(this)" style="margin-bottom: 4px; margin-top: 7px;">- 删除该组词语</button>`;
    }
    detailwords += `</td></tr>`;
    // add detail
    let addDetail = `<tr><td class="layui-table-header table-head" colspan=2 style="background-color: white">
                    <button class="layui-btn layui-btn-primary layui-btn-xs add-tip" onclick="addDetailLine(this)">+ 
                    添加detail</button></td></tr>`;

    $("#result-body").append(detailwords).append(addDetail);

    resetPosition();

    // revert
    if (questionData['backup']) {
        let revert = '<select name="revert" lay-filter="revert"  lay-search><option value="">最新版本</option>';
        for (let i = 0; i < questionData['backup'].length; i++) {
            revert += `<option value="${questionData['backup'][i]['backupId']}">${questionData['backup'][i]['label']}</option>`;
        }
        revert += '</select>';
        $("#revert-selector").empty().append(revert);
    } else if (noBackup) {
        $("#revert-selector").empty().append(`<select name="revert" lay-filter="revert"  lay-search><option value="">最新版本</option></select>`);
    }
    form.render();
    form.on('select(revert)', function (data) {
        if (data.value === '') {
            initTableFromServer(true, questionData["questionId"]);
        } else {
            initTableFromServer(false, data.value, "/admin/api/get-question-backup");
        }
    });

}

function deleteDetailList(deleteTip, isAdd) {
    let toDelete = $(deleteTip).parent().parent();
    let id = $(deleteTip).parent().attr("id");
    toDelete.remove();
    if (isAdd) {
        resetDetail_add(id);
    } else {
        resetDetail(id);
    }
}

function addDetailLine(lastLine, isAdd) {
    let id = isAdd ? addTableDetailIdList.length + 1 : detailIdList.length + 1;
    let idStr = isAdd ? `add-detail-words-${id}` : `detailwords${id}`;
    $(lastLine).parent().parent().before(`<tr><td class="layui-table-header table-head">detailwords ${id}</td><td id="${idStr}">
                  <div class="word-list">[<input type="text" required lay-verify="required" class="word-item" placeholder="输入词语"/><i class="delete-tip" onmouseenter="setBg(this)" onmouseleave="removeBg(this)" title="删除词语" onclick="deleteWord(this)">&#xe60e;</i><i class="delete-tip-bg">&#xe650;</i>
                  <button class="layui-btn layui-btn-primary layui-btn-xs add-tip" onclick="addWord(this, ${isAdd})">+ 添加词语</button>]
                  </div>
                  <br />
                  <button class="layui-btn layui-btn-primary layui-btn-xs add-tip" onclick="addWordList(this, ${isAdd})"style="margin-left: 10px; margin-bottom: 4px; margin-top: 7px;">+ 添加词语列表</button>
                  <button class="layui-btn layui-btn-primary layui-btn-xs add-tip delete-btn" onclick="deleteDetailList(this, ${isAdd})" style="margin-bottom: 4px; margin-top: 7px;">- 删除该组词语</button></td></tr>`);
    if (isAdd) {
        addTableDetailIdList.push(idStr);
        resetDetail_add();
        resetPosition_add();
    } else {
        detailIdList.push(idStr);
        resetPosition();
        resetDetail();
    }
}

function deleteWord(deleteTip, isAdd) {
    let toDelete1 = $(deleteTip).prev();
    let toDelete2 = $(deleteTip).next();
    let father = $(deleteTip).parent();
    if (father.children().length <= 4) {
        if (father.parent().children().length <= 3 && father.parent().attr('id').indexOf('detail') >= 0) {
            let id = father.parent().attr('id');
            father.parent().parent().remove();
            resetDetail(id);
        } else {
            father.next().remove();
            father.remove();
        }

    } else {
        deleteTip.remove();
        toDelete1.remove();
        toDelete2.remove();
    }

    if (isAdd) {
        resetPosition_add();
    } else {
        resetPosition();
    }
}

function resetDetail(id) {
    let nowIndex = 1;
    let tempList = [];
    for (let i = 0; i < detailIdList.length; i++) {
        let thisId = detailIdList[i];
        if (id !== thisId) {
            let td = $(`#${thisId}`);
            td.attr('id', `detailwords${nowIndex}`).prev().text(`detailwords ${nowIndex}`);
            tempList.push(`detailwords${nowIndex}`);
            nowIndex++;
        }
    }
    detailIdList = tempList;
}

function addWord(addTip, isAdd) {
    $(addTip).before(
        `<input type="text" required lay-verify="required" class="word-item" placeholder="输入词语"/>
        <i class="delete-tip" onmouseenter="setBg(this)" onmouseleave="removeBg(this)" onclick="deleteWord(this, ${isAdd})" title="删除词语">&#xe60e;</i><i class="delete-tip-bg">&#xe650;</i>`);
    if (isAdd) {
        resetPosition_add();
    } else {
        resetPosition();
    }
}

function addWordList(addTip, isAdd) {
    $(addTip).before(
        `<div class="word-list">[
            <input type="text" required lay-verify="required" class="word-item" placeholder="输入词语"/>
            <i class="delete-tip" onmouseenter="setBg(this)" onmouseleave="removeBg(this)" onclick="deleteWord(this, ${isAdd})" title="删除词语">&#xe60e;</i>
            <i class="delete-tip-bg">&#xe650;</i>
            <button class="layui-btn layui-btn-primary layui-btn-xs add-tip" onclick="addWord(this, ${isAdd})">+ 添加词语</button>]
        </div><br />`);
    if (isAdd) {
        resetPosition_add();
    } else {
        resetPosition();
    }
}

function setBg(tip) {
    $(tip).css("color", "white");
    $(tip).next().css("color", "#999");
}

function removeBg(tip) {
    $(tip).css("color", "#999");
    $(tip).next().css("color", "white");
}

function resetPosition() {
    let itemList = $("#result-body .word-item");
    for (let i = 0; i < itemList.length; i++) {
        let offset = $(itemList[i]).position();
        let tip = $(itemList[i]).next();
        let tipBg = tip.next();
        tip.css("top", `${offset.top + 1}px`);
        tip.css("left", `${offset.left + 101}px`);
        tipBg.css("top", `${offset.top}px`);
        tipBg.css("left", `${offset.left + 98}px`);
    }
}

function submitQuestion() {
    let text = $("#raw-text").val();
    if (text.length === 0) {
        layer.msg("题目原文不能为空");
        return;
    }
    console.log(text);

    let keywords = [];
    let ke = $("#keywords .word-list");
    for (let i = 0; i < ke.length; i++) {
        let list = $(ke[i])[0].childNodes;
        let wordList = [];
        for (let j = 0; j < list.length; j++) {
            let word = $(list[j]);
            if (word.attr("type") === 'text' && word.val() !== '') {
                wordList.push(word.val());
            }
        }
        if (wordList.length !== 0)
            keywords.push(wordList);
    }
    if (keywords.length === 0) {
        layer.msg("keywords不能为空");
        return;
    }
    console.log(keywords);

    let mainwords = [];
    let me = $("#mainwords .word-list");
    for (let i = 0; i < me.length; i++) {
        let list = $(me[i])[0].childNodes;
        let wordList = [];
        for (let j = 0; j < list.length; j++) {
            let word = $(list[j]);
            if (word.attr("type") === 'text' && word.val() !== '') {
                wordList.push(word.val());
            }
        }
        if (wordList.length !== 0)
            mainwords.push(wordList);
    }
    if (mainwords.length === 0) {
        layer.msg("mainwords不能为空");
        return;
    }
    console.log(mainwords);

    let detailwords = [];
    for (let k = 0; k < detailIdList.length; k++) {
        let detailwordsInner = [];
        let de = $(`#${detailIdList[k]} .word-list`);
        for (let i = 0; i < de.length; i++) {
            let list = $(de[i])[0].childNodes;
            let wordList = [];
            for (let j = 0; j < list.length; j++) {
                let word = $(list[j]);
                if (word.attr("type") === 'text' && word.val() !== '') {
                    wordList.push(word.val());
                }
            }
            if (wordList.length !== 0)
                detailwordsInner.push(wordList);
        }
        if (detailwordsInner.length !== 0)
            detailwords.push(detailwordsInner);
    }
    if (detailwords.length === 0) {
        layer.msg("detailwords不能为空");
        return;
    }
    console.log(detailwords);

    // submit
    $.post("/admin/api/modify-question-content", {
        "questionId": questionData['questionId'],
        "keywords": JSON.stringify(keywords),
        "mainwords": JSON.stringify(mainwords),
        "detailwords": JSON.stringify(detailwords),
        "rawText": text
    }).done((data) => {
        questionData = data;
        initTable();
        layer.msg("修改成功");
    }).fail(e => {
        try {
            let response = JSON.parse(e.responseText);
            if (response['needDisplay']) {
                layer.msg(response['tip']);
            } else {
                layer.msg("服务器出错了");
            }
        } catch (e) {
            layer.msg("服务器出错了");
        }
    });
}

function deleteQuestion() {
    // layer.open({
    //     title: "警告",
    //     type: 0,
    //     content: '<div style="width: 100%;text-align: center;font-size: 18px;margin-top: 36px;">确定要删除该题目吗？</div>',
    //     area: ['360px', '200px'],
    // });

    layer.confirm('确定要删除该题目吗？', {
        btn: ['确认', '取消'],
        title: "警告",
    }, function (index) {
        $.post("/admin/api/delete-question", {
            "questionId": questionData['questionId'],
        }).done(() => {
            layer.close(index);
            hideTable();
            layer.msg("删除成功");
        }).fail(e => {
            layer.close(index);
            try {
                let response = JSON.parse(e.responseText);
                if (response['needDisplay']) {
                    layer.msg(response['tip']);
                } else {
                    layer.msg("服务器出错了");
                }
            } catch (e) {
                layer.msg("服务器出错了");
            }
        });
    });
}

function hideTable() {
    $("#search-tip").css("display", "");
    $("#question-table").css("display", "none");
    $("#add-question").css("display", "none");
}

function reAnalysis() {
    layer.load(1);
    $.post("/admin/api/analysis-question", {"questionId": questionData['questionId']}).done(function (data) {
        console.log(data);
        layer.closeAll('loading');
        layer.msg("分析成功");
        initQuestionChartData(data);
    }).fail(e => {
        layer.closeAll('loading');
        try {
            let response = JSON.parse(e.responseText);
            if (response['needDisplay']) {
                layer.msg(response['tip']);
            } else {
                layer.msg("服务器出错了");
            }
        } catch (e) {
            layer.msg("服务器出错了");
        }
    });
}