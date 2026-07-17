import {adminLogin} from "./api.js";

// 知识库页面加载数据
async function loadKbList(){
    const res = await fetch("/api/admin/kb/list");
    const data = await res.json();
    const tbody = document.getElementById("kbTableBody");
    tbody.innerHTML = "";
    data.data.forEach(item=>{
        tbody.innerHTML += `
        <tr>
            <td>${item.id}</td>
            <td>${item.title}</td>
            <td>
                <button class="btn btn-sm btn-danger del-kb" data-id="${item.id}">删除</button>
            </td>
        </tr>`;
    })
    // 绑定删除事件
    document.querySelectorAll(".del-kb").forEach(btn=>{
        btn.onclick = async ()=>{
            const id = btn.dataset.id;
            await fetch(`/api/admin/kb/delete/${id}`, {method:"DELETE"});
            loadKbList();
        }
    })
}

// 新增知识库
document.getElementById("addKbBtn")?.addEventListener("click", async ()=>{
    const title = document.getElementById("kbTitle").value.trim();
    const content = document.getElementById("kbContent").value.trim();
    if(!title || !content) return alert("标题和内容不能为空");
    await fetch("/api/admin/kb/add",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({title,content})
    })
    alert("新增成功");
    loadKbList();
    document.getElementById("kbTitle").value = "";
    document.getElementById("kbContent").value = "";
})

// 数字人配置保存
document.getElementById("saveHumanBtn")?.addEventListener("click", async ()=>{
    const payload = {
        config_name: document.getElementById("humanName").value,
        voice_type: document.getElementById("voiceType").value,
        costume_style: document.getElementById("costumeStyle").value,
        is_default: document.getElementById("isDefault").checked ? 1 : 0
    }
    await fetch("/api/admin/human/save",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(payload)
    })
    alert("数字人配置保存完成");
})

// 页面初始化
window.onload = ()=>{
    if(document.getElementById("kbTableBody")) loadKbList();
}