ROOT_DIR = "/home/neo/vscodeProjects/chatgpt_auto"
COOKIES = ROOT_DIR + "/cookies.json"
CHAT = "https://chatgpt.com/c/6713eccc-05cc-800b-83ee-67841c2c91d4"

DRIVER_OPTIONS = [
    "--log-level=3",
    "--disable-extensions",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-gpu",
    "--blink-settings=imagesEnabled=false",
]

INPUT_TEXT = '//*[@id="prompt-textarea"]/p'
SEND_BUTTON = '//button[@aria-label="Send prompt"]'

WAIT = 30

COUNT_ARTICLES = """
let chatgptSaid = document.querySelectorAll('h6')
let articleCount = 0

chatgptSaid.forEach((div) => {
    if (div.textContent.includes("ChatGPT said:")) {
        const allMessages = div.closest('div')
        const articles = allMessages.querySelectorAll('article')
        articleCount = articles.length // Get the count of <article> elements
    }
})

return articleCount
"""

CLEAN_UP_PAGE = """
let chatgptSaid = document.querySelectorAll('h6')
let allMessages = chatgptSaid
let articlesToCleanup = 0

chatgptSaid.forEach((div) => {
    if (div.textContent.includes("ChatGPT said:")) {
        allMessages = div.closest('div')
    }
})

let clonedResponse = null
let clonedPrompt = null

if (allMessages) {
    clonedPrompt = allMessages.cloneNode(true).querySelector('article:nth-last-of-type(2)')
    clonedResponse = allMessages.cloneNode(true).querySelector('article:last-of-type')
}

articlesToRemove = allMessages.querySelectorAll('article').length
if (articlesToRemove > 2) {
    allMessages.innerHTML = ''
    allMessages.appendChild(clonedPrompt)
    allMessages.appendChild(clonedResponse)
}

const links = document.querySelectorAll('link[rel="stylesheet"]')
links.forEach(link => link.remove())

const styles = document.querySelectorAll('style')
styles.forEach(style => style.remove())

return articlesToRemove
"""

GENERATING = "ChatGPT is generating a response..."
