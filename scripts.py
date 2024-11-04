GET_ALL_TEXT_LENGTH = """
let chatgptSaid = document.querySelectorAll('h6')
let allMessages

for (let div of chatgptSaid) {
    if (div.textContent.includes("ChatGPT said:")) {
        allMessages = div.closest('div')
        break
    }
}

let articles = allMessages.querySelectorAll('article')

let totalLength = 0

articles.forEach((article) => {
    totalLength += article.textContent.length
})

return totalLength
"""

GET_LAST_RESPONSE_LENGTH = """
let chatgptSaid = document.querySelectorAll('h6')
let allMessages

for (let div of chatgptSaid) {
    if (div.textContent.includes("ChatGPT said:")) {
        allMessages = div.closest('div')
        break
    }
}

if (typeof(allMessages) == 'undefined') {
    return 0
} else {
    let articles = allMessages.querySelectorAll('article')
    let lastResponse = articles[articles.length - 1]
    return lastResponse.textContent.length
}
"""

COUNT_MESSAGES = """
let chatgptSaid = document.querySelectorAll('h6')
let allMessages

for (let div of chatgptSaid) {
    if (div.textContent.includes("ChatGPT said:")) {
        allMessages = div.closest('div')
        break
    }
}

if (typeof(allMessages) == 'undefined') {
    return 0
} else {
    return allMessages.querySelectorAll('article').length
}
"""

CLEAN_UP_PAGE = """
let chatgptSaid = document.querySelectorAll('h6')
let allMessages

for (let div of chatgptSaid) {
    if (div.textContent.includes("ChatGPT said:")) {
        allMessages = div.closest('div')
        break
    }
}

let allArticles = allMessages.querySelectorAll('article')
let messageCount = allArticles.length
let lastResponse = allArticles[messageCount - 1]

if (typeof(lastResponse) != 'undefined') {
    lastResponse.querySelectorAll('button').forEach((button) => {
        let aria_label = button.getAttribute('aria-label')
        if (aria_label != null && aria_label != "") {
            button.remove()
        }
    })
    
    allMessages.innerHTML = ''
    allMessages.appendChild(lastResponse)    
}

let trashNames = ['nav', 'svg', 'link[rel="stylesheet"]', 'style']
for (let junk of trashNames) {
    let allJunk = document.querySelectorAll(junk)
    if (allJunk.length > 0) {
        allJunk.forEach((j) => {
            j.remove()
            console.log('removed', junk)
        })
    }
}

console.log("Removed", messageCount, "messages")
return messageCount
"""
