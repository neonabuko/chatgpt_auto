allMessages = await getMessages()
messageCount = allMessages.querySelectorAll('article').length

let clonedResponse
let clonedPrompt

if (allMessages) {
    clonedPrompt = allMessages.cloneNode(true).querySelector('article:nth-last-of-type(2)')
    clonedResponse = allMessages.cloneNode(true).querySelector('article:last-of-type')
}

allMessages.innerHTML = ''
allMessages.appendChild(clonedPrompt)
allMessages.appendChild(clonedResponse)

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
    const wait = 2000

    for (let i = 0; i < attempts; i++) {
        chatgptSaid.forEach((div) => {
            if (div.textContent.includes("ChatGPT said:")) {
                allMessages = div.closest('div')
            }
        })

        let articles = allMessages.querySelectorAll('article')
        currentCount = articles.length

        if (currentCount == previousCount && currentCount > 2) {
            if (articles[currentCount - 1].textContent.length > 0 && articles[currentCount - 2].textContent.length > 0) {
                return allMessages
            }
        }

        previousCount = currentCount

        await sleep(wait)
    }

    throw Error("Number of messages unstable for too long")
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }