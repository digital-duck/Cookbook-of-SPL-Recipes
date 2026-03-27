```bash
spl run src/recipes/ch02-2-react-agent/react_agent.spl --adapter claude_cli -m claude-sonnet-4-6 --claude-allowed-tools WebSearch country="France"



spl run src/recipes/ch02-2-react-agent/react_agent.spl --adapter claude_cli -m claude-sonnet-4-6 --claude-allowed-tools WebSearch --tools src/recipes/ch02-2-react-agent/tools.py country="China" \
    2>&1 | tee src/recipes/ch02-2-react-agent/out/06_react_agent-$(date +%Y%m%d_%H%M%S).md

```
