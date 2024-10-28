import multiprocessing
from queue import Queue
import re
from gtts import gTTS

text = """Coffee, often hailed as the world’s favorite beverage? has a rich history and a profound cultural significance that transcends borders. Originating from the coffee plant, believed to be native to Ethiopia, coffee has traveled the globe, evolving into a multi-billion dollar industry that is woven into the fabric of daily life for millions. The journey of coffee from bean to cup is not only a testament to agricultural ingenuity but also a narrative that reflects social, economic, and cultural developments throughout history.The story of coffee begins with its discovery in the 9th century by a goat herder named Kaldi, who noticed that his goats became unusually energetic after consuming the berries from a certain tree. Intrigued by this phenomenon, Kaldi tried the berries himself and soon experienced a similar burst of energy. This serendipitous discovery marked the beginning of coffee's long and storied journey. It wasn’t long before coffee beans made their way to the Arabian Peninsula, where they were cultivated and brewed in the form we recognize today.By the 15th century, coffee was being grown in Yemen and served in Sufi shrines. Its popularity spread to Persia, Egypt, and Turkey, where coffeehouses known as qahveh khaneh became social hubs for conversation, music, and intellectual exchange. These establishments laid the groundwork for the modern café culture that thrives in cities around the world today. The 17th century saw coffee’s introduction to Europe, where it quickly became a fashionable drink among the elite. Coffeehouses emerged in major cities like London and Paris, often referred to as "penny universities," where patrons could engage in lively discussions and access news and information.The rise of coffee in Europe paralleled the development of colonialism, with European powers establishing coffee plantations in tropical regions of the Americas, Asia, and Africa. This colonial expansion led to the commodification of coffee, transforming it into a global commodity that fueled economies and shaped trade networks. However, this growth came at a significant cost, as the demand for coffee also contributed to the exploitation of labor, particularly in the context of slavery and indentured servitude.Today, coffee is one of the most traded commodities in the world, with millions of people relying on its cultivation for their livelihoods. The coffee supply chain is complex, involving a myriad of actors from farmers to exporters to roasters and retailers. The sustainability of coffee production is increasingly a topic of discussion, as climate change, deforestation, and economic inequalities pose significant challenges to the industry. Consumers are becoming more aware of the importance of ethical sourcing and fair trade practices, leading to a growing demand for organic and sustainably produced coffee.In addition to its economic impact, coffee also plays a significant role in social rituals and personal routines. The act of brewing and consuming coffee is often a moment of solace, a time for reflection, or a chance to connect with others. The aroma of freshly brewed coffee can evoke feelings of warmth and comfort, making it a beloved beverage in households and workplaces alike. Coffee breaks have become a staple in office culture, promoting camaraderie and collaboration among colleagues.Moreover, coffee has inspired a vast array of culinary creations, from espresso and cappuccino to specialty lattes and coffee-infused desserts. The versatility of coffee allows it to be enjoyed in various forms, whether hot, iced, or blended into refreshing beverages. Baristas have turned coffee preparation into an art form, employing techniques that showcase the nuances of flavor and aroma inherent in different coffee beans.In conclusion, coffee is much more than just a drink; it is a cultural phenomenon that reflects a confluence of history, economics, and social interaction. Its journey from bean to cup encapsulates the spirit of innovation and the interconnectedness of our global society. As we continue to navigate the complexities of coffee production and consumption, it is essential to appreciate the stories and traditions behind each cup, recognizing the myriad ways this beloved beverage enriches our lives. Whether savored in solitude or shared with friends, coffee remains a cherished part of human experience, offering comfort, connection, and inspiration.
"""

sentences = re.split(r'(?<=[?.])\s*', text)
f_sentences = [s.lstrip() for s in sentences if s.strip()]

play_queue = Queue()
lock = multiprocessing.Lock()
base_path = '/home/neo/vscodeProjects/chatgpt_auto/assets/tts'

def gen_tts(text, i):
    audio = gTTS(text=text)
    path = f'{base_path}/audio_{i}.mp3'
    audio.save(path)

def start_gen():
    processes = []
    for i, sentence in enumerate(f_sentences):
        p = multiprocessing.Process(target=gen_tts, args=(sentence, i))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


audios = [audio.path for audio in os.scandir('/home/neo/vscodeProjects/chatgpt_auto/assets/tts/')]

audios = sorted(audios)

for audio in audios:
    subprocess.run(['mpv', '--speed=2.7', audio])