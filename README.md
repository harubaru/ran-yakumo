![logo](banner.png)

## Overview
Ran Yakumo is a general information utility bot powered by [Sukima](https://github.com/hitomi-team/sukima) which uses GPT-J to power various functions!

### Curent Capabilities
- **Chatbot** : Able to talk to anyone who pings Ran or mentions its name.
- **Question and Answering**: Answers any question presented to Ran.
- **GPT-J Dictionary**: Is able to retrieve a definition on any term.
- **Polyglot** : Able to translate between 16 different languages.
- **Danbooru Search** : Able to fetch images from Danbooru.
- **Wikipedia Search** : Uses Wikipedia's search API to fetch wikipedia articles based on a search query.
- **YouTube Search** : Queries the YouTube API for videos.
- **Rate Limiting** : Messages are rate limited to 1 message per 10 seconds, or 6 messages per minute. This is to help reduce API costs and spam.

### Setup
1. Add your keys into a file named ``secrets.json``, the keys that are required are the Discord Token and the OpenAI API key. A sample version of the file can be [seen here.](sample_secrets.json)
2. Install docker and run ``docker-compose up``
3. That's it!

### License
[Simplified BSD License](LICENSE)
