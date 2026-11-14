# Flatten an `opencode session export` into readable text.
# Output: two sections separated by "@@TOOLS@@" so the caller can split them.
def clip($n): if (length > $n) then .[0:$n] + " …[clipped \(length - $n) chars]" else . end;

([
  .messages[]
  | if .type == "user" then
      "\n===== USER (\(.time.created // 0 | tostring)) =====\n" + ((.text // "") | clip(20000))
    elif .type == "assistant" then
      ([.content[]? | select(.type == "text") | .text] | join("\n")) as $t
      | if ($t | length) > 0 then "\n----- ASSISTANT -----\n" + ($t | clip(12000)) else empty end
    elif .type == "compaction" then
      "\n===== COMPACTION =====\n" + ((.summary // .text // "(compaction)") | tostring | clip(4000))
    elif .type == "agent-switched" or .type == "model-switched" then
      "\n===== \(.type | ascii_upcase): \(.agent // .model // "" | tostring) =====\n"
    elif .type == "synthetic" then empty
    elif .type == "system" then empty
    elif .type == "idle" then empty
    else empty end
] | join("")) + "\n@@TOOLS@@\n" + ([
  .messages[]
  | select(.type == "assistant")
  | .content[]?
  | select(.type == "tool")
  | (.state.input // {} | tostring | clip(400)) as $in
  | if .state.status == "error" then
      "!! FAILED \(.name): \($in)\n   -> \((.state.error // "no error text") | tostring | clip(1200))\n"
    else
      "ok \(.name): \($in)\n"
    end
] | join(""))
