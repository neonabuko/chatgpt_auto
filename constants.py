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

RULES = "RULES: ChatGPT_AUTO is for automatically running code in my terminal. Python and Bash Code: You can send Python and Bash code separately, but if I request code and execution together, you should send them in separate blocks. First Line of Python Code: Every Python script you send must start with a comment containing the filename. Unique Filenames: Every filename must be unique to avoid overwriting existing files. You can check the existing files in my project folder before writing the new Python script. No Manual Confirmation: Commands you send to my terminal should not require manual confirmation. If a command needs confirmation, you should add a pre-execution step to handle it. Code Execution Flow: When sending Python code, you can also send the command to execute the file after creating it."

HEADER = "CHATGPT_AUTO"

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


let messageCount = allMessages.querySelectorAll('article').length

allMessages.innerHTML = ''

let nav = document.querySelector('nav')
nav.innerHTML = ''

const links = document.querySelectorAll('link[rel="stylesheet"]')
links.forEach(link => {
    if (link.hasChildNodes()) {
        link.remove()            
    }
})

const styles = document.querySelectorAll('style')
styles.forEach(style => {
    if (style.hasChildNodes()) {
        style.remove()   
    }
})

console.log("Removed", messageCount, "messages")
return messageCount
"""
