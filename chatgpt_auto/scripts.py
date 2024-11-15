from typing import Final


class Scripts:
    GET_ALL_TEXT_LENGTH: Final[str] = """
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

    IS_GENERATING_RESPONSE: Final[str] = """
    let chatgptSaid = document.querySelectorAll('h6')
    let allMessages

    for (let div of chatgptSaid) {
        if (div.textContent.includes("ChatGPT said:")) {
            allMessages = div.closest('div')
            break
        }
    }

    let lastResponse
    if (typeof(allMessages) == 'undefined') {
        return false
    } else {
        let articles = allMessages.querySelectorAll('article')
        lastResponse = articles[articles.length - 1]
    }

    let allDescendants = lastResponse.querySelectorAll('*')

    for (let el of allDescendants) {
        let computedStyle = window.getComputedStyle(el, '::after')
        let afterContent = computedStyle.getPropertyValue('content')
        
        if (afterContent && afterContent !== 'none') {
            return true
        }
    }
    return false
    """

    CLEAN_UP_PAGE: Final[str] = """
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
