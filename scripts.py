GET_RESPONSE_LENGTH = """
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

lastResponse.querySelectorAll('button').forEach((button) => {
    let aria_label = button.getAttribute('aria-label')
    if (aria_label != null && aria_label != "") {
        button.remove()
    }
})

document.querySelector('nav').innerHTML = ''
document.querySelectorAll('svg').forEach((svg) => {
    svg.remove()
})

document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
    link.remove()
})

document.querySelectorAll('style').forEach(style => {
    style.remove()
})

document.querySelector('div').innerHTML = ''
document.querySelector('div').appendChild(lastResponse)

console.log("Removed", messageCount, "messages")
return messageCount
"""
