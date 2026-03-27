# ch01-3: Multilingual Greeting

Greet in any language — demonstrates parametric context passing via `user_input` and `lang`.

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `user_input` | TEXT | *(required)* | The greeting or message to translate |
| `lang` | TEXT | *(required)* | Target language (e.g. Chinese, French, Japanese, Spanish) |

## Usage

```bash
# Local Ollama
spl run src/recipes/ch01-3-multilingual/multilingual.spl --adapter ollama \
    user_input="Hello Wen-Guang" lang="Chinese"

spl run src/recipes/ch01-3-multilingual/multilingual.spl --adapter ollama \
    user_input="Good morning" lang="French"

spl run src/recipes/ch01-3-multilingual/multilingual.spl --adapter ollama \
    user_input="How are you?" lang="Japanese"

spl run src/recipes/ch01-3-multilingual/multilingual.spl --adapter ollama \
    user_input="See you later" lang="Spanish"

# Momagrid
spl run src/recipes/ch01-3-multilingual/multilingual.spl --adapter momagrid \
    user_input="Hello Wen Gong, what are you cooking today?" lang="Chinese"

spl run src/recipes/ch01-3-multilingual/multilingual.spl --adapter momagrid \
    user_input="Good morning" lang="French"

spl run src/recipes/ch01-3-multilingual/multilingual.spl --adapter momagrid \
    user_input="How are you?" lang="Japanese"

spl run src/recipes/ch01-3-multilingual/multilingual.spl --adapter momagrid \
    user_input="See you later" lang="Spanish"
```
