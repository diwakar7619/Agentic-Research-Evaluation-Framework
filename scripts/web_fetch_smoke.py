from collector.web import fetch_webpage


url = "https://github.com/rohitg00/ai-engineering-from-scratch"

text = fetch_webpage(url)

if text is None:
    raise RuntimeError("No usable content extracted")

print(f"Extracted characters: {len(text)}")
print("\n--- PREVIEW ---\n")
print(text[:2000])
