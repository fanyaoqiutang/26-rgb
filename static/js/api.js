const baseUrl = "http://127.0.0.1:5000/api";

// 游客对话接口
export function sendChatMsg(text) {
    return fetch(`${baseUrl}/tourist/chat`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({user_input:text})
    }).then(res=>res.json())
}

// 获取数字人配置
export function getHumanConfig() {
    return fetch(`${baseUrl}/tourist/human-config`).then(res=>res.json())
}

// 管理员登录接口
export function adminLogin(username,pwd) {
    return fetch(`${baseUrl}/admin/login`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({username,password:pwd})
    }).then(res=>res.json())
}

