# Extract Reddit Gems Directive

## Goal
Extract "Gemini Gems" (custom system instructions/prompts) shared on the `r/GeminiAI` subreddit during **January 2026**.

## Inputs
- **Source**: `r/GeminiAI` subreddit.
- **Timeframe**: Jan 1, 2026 - Jan 31, 2026.
- **Keywords**: "Gem", "Prompt", "Instruction", "System Prompt".

## Execution Tool
- `execution/fetch_reddit_gems.py`

## Output
- **Directory**: `gems/` (created in project root).
- **Format**: Markdown files named `<sanitized_title>.md`.
- **Content per file**:
    - Title
    - Author
    - Date
    - URL
    - Description (Post body)
    - Instructions (Extracted prompt text)

## Edge Cases
- **No API Credentials**: Script will fail. User needs to provide `.env` keys.
- **No Gems Found**: Script should exit gracefully with a message.
- **Rate Limits**: `praw` handles this automatically, but large scrapes might take time.
