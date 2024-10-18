ROOT_DIR = "/home/neo/vscodeProjects/chatgpt_auto"
COOKIES = ROOT_DIR + "/cookies.json"
CHATGPT = "https://chatgpt.com/c/670de842-bb50-800b-9cd5-79c5df22a405"

INPUT_TEXT = 'p[data-placeholder="Message ChatGPT"]'
SEND_BUTTON = '//button[@aria-label="Send prompt"]'

WAIT = 30

CHECK_ARTICLES_SCRIPT = """
let chatgptSaid = document.querySelectorAll('h6');
let articleCount = 0;

chatgptSaid.forEach(function(div) {
    if (div.textContent.includes("ChatGPT said:")) {
        const allMessages = div.closest('div');
        const articles = allMessages.querySelectorAll('article');
        articleCount = articles.length; // Get the count of <article> elements
    }
});

return articleCount;
"""

CLEAN_UP_SCRIPT = """
let chatgptSaid = document.querySelectorAll('h6');
let allMessages = null;

chatgptSaid.forEach(function(div) {
    if (div.textContent.includes("ChatGPT said:")) {
        allMessages = div.closest('div');
    }
});

let clonedResponse = null;
let clonedPrompt = null;

if (allMessages) {
    clonedPrompt = allMessages.cloneNode(true).querySelector('article:nth-last-of-type(2)');
    clonedResponse = allMessages.cloneNode(true).querySelector('article:last-of-type');
}

allMessages.innerHTML = '';
allMessages.appendChild(clonedPrompt);
allMessages.appendChild(clonedResponse);

const links = document.querySelectorAll('link[rel="stylesheet"]');
links.forEach(link => link.remove());

const styles = document.querySelectorAll('style');
styles.forEach(style => style.remove());
"""