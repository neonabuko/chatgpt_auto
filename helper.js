let chatgptSaid = document.querySelectorAll('h6')
let allMessages = null

chatgptSaid.forEach(function(div) {
    if (div.textContent.includes("ChatGPT said:")) {
        allMessages = div.closest('div')
    }
})

let clonedResponse = null
let clonedPrompt = null
let clonedInput = null
let container = document.createElement('body')

if (allMessages) {
    clonedPrompt = allMessages.cloneNode(true).querySelector('article:nth-last-of-type(2)')
    clonedResponse = allMessages.cloneNode(true).querySelector('article:last-of-type')
    container.appendChild(clonedPrompt)
    container.appendChild(clonedResponse)
}

allMessages.innerHTML = ''
allMessages.appendChild(container)

const links = document.querySelectorAll('link[rel="stylesheet"]');
links.forEach(link => link.remove());

const styles = document.querySelectorAll('style');
styles.forEach(style => style.remove());