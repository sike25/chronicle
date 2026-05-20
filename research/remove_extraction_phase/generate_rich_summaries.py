'''
generate_rich_summaries.py
 
For each document ID in collected_ids.json, find the matching entry in the
archive data dump, generate a richer LLM summary from its raw OCR extract,
and write the result to enriched_dump.jsonl.

Execution Results:
Loading IDs from collected_ids.json...
  1589 IDs loaded.
Loading data dump from formatted_dump.jsonl...
  70482 documents in dump.
  1589 documents matched.
'''

import anthropic
import json
import time
from pathlib import Path

COLLECTED_IDS_PATH  = "collected_ids.json"
DATA_DUMP_PATH      = "formatted_dump.jsonl"
OUTPUT_PATH         = "enriched_dump.jsonl"

MODEL               = "claude-haiku-4-5"
MAX_TOKENS          = 500
RETRY_LIMIT         = 3
RETRY_DELAY_SECONDS = 5

SYSTEM_PROMPT = (
    "You are an archivist summarizing historical Nigerian newspaper articles. "
    "Write dense, factual summaries that preserve names, dates, numbers, and specific events."
)


def build_user_prompt(document: dict) -> str:
    s = document.get("structData", {})
    return f"""
      Document: {s.get('filename', 'unknown')}
      Publication: {s.get('publication', 'unknown')}, {s.get('publication_date', 'unknown')}
      Text: {s.get('extract', '')}
 
      Task: This is an OCR extract of a Nigerian newspaper image. 
      Write a detailed summary of it.

      If the extract contains several stories, summarize each, one after the other.

      Include all named people, places, organizations, dates, statistics, and specific events mentioned. 
      Be thorough — this summary will be used for historical research. 
      Do not add information not present in the text. 
      """



client = anthropic.Anthropic()

def generate_rich_summary(document: dict):
   prompt = build_user_prompt(document)

   for attempt in range(1, RETRY_LIMIT + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                temperature=0,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"  [attempt {attempt}/{RETRY_LIMIT}] Error: {e}")
            if attempt < RETRY_LIMIT:
                time.sleep(RETRY_DELAY_SECONDS)
 
   return None

def main():
   print(f"Loading IDs from {COLLECTED_IDS_PATH}...")
   with open(COLLECTED_IDS_PATH) as f:
      collected_ids: set[str] = set(json.load(f)["all_ids"])
   print(f"  {len(collected_ids)} IDs loaded.")

   print(f"Loading data dump from {DATA_DUMP_PATH}...")
   with open(DATA_DUMP_PATH) as f:
      data_dump: list[dict] = [json.loads(line) for line in f if line.strip()]
   print(f"  {len(data_dump)} documents in dump.")

   # filter to matched documents
   matched = [doc for doc in data_dump if doc.get("id") in collected_ids]
   print(f"  {len(matched)} documents matched.\n")

   if not matched:
      print("No matches found. Check that IDs in collected_ids.json align with 'id' fields in data_dump.jsonl.")
      return
   

   # generate rich summaries, write to JSONL as we go (safe against crashes mid-run)
   output_path = Path(OUTPUT_PATH)
   succeeded = 0
   failed    = 0
 
   with open(output_path, "w") as out:
      for idx, document in enumerate(matched, start=1):
         document_id = document.get("id", "unknown")
         filename    = document.get("structData", {}).get("filename", "unknown")
         print(f"[{idx}/{len(matched)}] {document_id} | {filename}")
 
         rich_summary = generate_rich_summary(document)
 
         if rich_summary:
            succeeded += 1
            print(f"  ✓ summary generated ({len(rich_summary)} chars)")
         else:
            failed += 1
            rich_summary = ""
            print(f"  ✗ failed after {RETRY_LIMIT} attempts — empty string written")
 
         result = {**document, "structData": {**document.get("structData", {}), "rich_summary": rich_summary}}
         out.write(json.dumps(result) + "\n")
 
   print(f"\nDone. {succeeded} succeeded, {failed} failed.")
   print(f"Results written to {output_path.resolve()}")
 
 
if __name__ == "__main__":
    main()