![logo](banner.png)

## Overview
Ran Yakumo is a general information utility bot powered by GPT-3!

### Curent Capabilities
- **Polyglot** : Able to translate between 16 different languages.
- **Danbooru Search** : Able to fetch images from Danbooru.
- **Wikipedia Search** : Uses Wikipedia's search API to fetch wikipedia articles based on a search query.
- **YouTube Search** : Uses GPT-3 to classify similarity between search query and video title.
- **Rate Limiting** : Messages are rate limited to 1 message per 10 seconds, or 6 messages per minute. This is to help reduce API costs and spam.

### Setup
1. Add your keys into a file named ``secrets.json``, the keys that are required are the Discord Token and the OpenAI API key. A sample version of the file can be [seen here.](sample_secrets.json)
2. Install docker and run ``docker-compose up``
3. That's it!

### License
[Simplified BSD License](LICENSE)
