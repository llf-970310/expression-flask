let addTableDetailIdList = [];

function showAddQuestion() {
    $("#add-question").css("display", "");
    $("#question-table").css("display", "none");
    resetAddTable();
}

function resetAddTable() {
    $("#add-raw-text").val('');
    let content = `<div class="word-list">
                [
                <input type="text" required lay-verify="required" class="word-item" placeholder="输入词语"/>
                <i class="delete-tip" onmouseenter="setBg(this)" onmouseleave="removeBg(this)" title="删除词语"
                   onclick="deleteWord(this, true)">&#xe60e;</i><i class="delete-tip-bg">&#xe650;</i>
                <button class="layui-btn layui-btn-primary layui-btn-xs add-tip" onclick="addWord(this, true)">+
                    添加词语
                </button>
                ]
            </div>
            <br/>
            <button class="layui-btn layui-btn-primary layui-btn-xs add-tip" onclick="addWordList(this, true)"
                    style="margin-left: 10px; margin-bottom: 4px; margin-top: 5px;">+ 添加词语列表
            </button>`;

    $("#add-key-words").empty().append(content);
    $("#add-main-words").empty().append(content);
    $("#add-detail-words-1").empty().append(content + `<button class="layui-btn layui-btn-primary layui-btn-xs add-tip delete-btn"
                    onclick="deleteDetailList(this, true)" style="margin-bottom: 4px; margin-top: 7px;">- 删除该组词语
            </button>`);
    let tr = $("#add-table tr");
    if (tr.length > 4) {
        tr.slice(4 - tr.length).remove();
    }
    $("#add-table").append(`<tr>
        <td class="layui-table-header table-head" colspan=2 style="background-color: white">
            <button class="layui-btn layui-btn-primary layui-btn-xs add-tip" onclick="addDetailLine(this, true)">+
                添加detail
            </button>
        </td>
    </tr>`);
    addTableDetailIdList = ['add-detail-words-1'];
    resetPosition_add();
}

function resetPosition_add() {
    let itemList = $("#add-table .word-item");
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

function resetDetail_add(id) {
    let nowIndex = 1;
    let tempList = [];
    for (let i = 0; i < addTableDetailIdList.length; i++) {
        let thisId = addTableDetailIdList[i];
        if (id !== thisId) {
            let td = $(`#${thisId}`);
            td.attr('id', `add-detail-words-${nowIndex}`).prev().text(`detailwords ${nowIndex}`);
            tempList.push(`add-detail-words-${nowIndex}`);
            nowIndex++;
        }
    }
    addTableDetailIdList = tempList;

}

function submitAddQuestion() {
    let text = $("#add-raw-text").val();
    if (text.length === 0) {
        layer.msg("题目原文不能为空");
        return;
    }
    console.log(text);

    let keywords = [];
    let ke = $("#add-key-words .word-list");
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
    let me = $("#add-main-words .word-list");
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
    for (let k = 0; k < addTableDetailIdList.length; k++) {
        let detailwordsInner = [];
        let de = $(`#${addTableDetailIdList[k]} .word-list`);
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

    $.post("/admin/api/add-question", {
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
    });
}