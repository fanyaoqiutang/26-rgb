import {sendChatMsg, getHumanConfig} from "./api.js";

const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const humanAvatar = document.getElementById("humanAvatar");
const humanStatus = document.getElementById("humanStatus");

// 页面加载时加载数字人形象
window.onload = async ()=>{
    let res = await getHumanConfig();
    if(res.code===200){
        humanAvatar.src = res.data.face_image_path;
    }
}

// 发送文本消息
sendBtn.addEventListener("click",async ()=>{
    let text = userInput.value.trim();
    if(!text) return;
    // 渲染用户消息
    chatBox.innerHTML += `<div class="user-message text-end mt-2">${text}</div>`;
    userInput.value = "";
    humanStatus.innerText = "正在回答...";

    // 请求后端问答接口
    let resp = await sendChatMsg(text);
    humanStatus.innerText = "待机中";
    // 渲染AI回答
    chatBox.innerHTML += `<div class="ai-message mt-2">${resp.data.ai_reply}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
})

// 语音输入按钮（预留whisper语音识别接口，你关闭whisper可注释此功能）
document.getElementById("voiceBtn").addEventListener("click",()=>{
    alert("语音识别功能待接入Whisper接口");
})