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
GENERATING = "ChatGPT is generating a response..."


CLEAN_UP_PAGE = """
allMessages = await getMessages()
messageCount = allMessages.querySelectorAll('article').length

allMessages.innerHTML = ''

let nav = document.querySelector('nav')
nav.innerHTML = ''

const links = document.querySelectorAll('link[rel="stylesheet"]')
links.forEach(link => link.remove())

const styles = document.querySelectorAll('style')
styles.forEach(style => style.remove())

console.log("Removed", messageCount, "messages")
return messageCount

async function getMessages() {
    let chatgptSaid = document.querySelectorAll('h6')
    let allMessages
    let previousCount = -1
    let currentCount = 0
    const attempts = 10
    const wait = 1000

    for (let i = 0; i < attempts; i++) {
        chatgptSaid.forEach((div) => {
            if (div.textContent.includes("ChatGPT said:")) {
                allMessages = div.closest('div')
            }
        })

        let articles = allMessages.querySelectorAll('article')
        currentCount = articles.length

        if (currentCount == previousCount) {
            return allMessages
        }

        previousCount = currentCount

        await sleep(wait)
    }

    throw Error("Number of messages unstable for too long")
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
"""
