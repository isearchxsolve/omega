#!/usr/bin/env python3
"""
AUTO-INTEGRATE SOTA QUALITY ENGINE INTO OMEGA NOTEBOOK

This script reads your OMEGA_SOTA_INTEGRATED_WITH_OPTIONS_WINDOWS.ipynb
and automatically patches the key cells (call_llm, run_v7_orchestrator,
Gradio UI) to enable the full SOTA quality assurance system.

Usage:
    python SOTACREATOR2.py

Output:
    OMEGA_SOTA_AUTO_PATCHED.ipynb
"""

import json
import re
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
INPUT_NOTEBOOK = "OMEGA_SOTA_INTEGRATED_WITH_OPTIONS_WINDOWS.ipynb"
OUTPUT_NOTEBOOK = "OMEGA_SOTA_AUTO_PATCHED.ipynb"

# ----------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------
def load_notebook(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_notebook(notebook, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)

def is_code_cell(cell):
    return cell.get('cell_type') == 'code'

def get_source_text(cell):
    return ''.join(cell['source'])

def set_source_text(cell, text):
    cell['source'] = text.splitlines(keepends=True)

# ----------------------------------------------------------------------
# PATCH 1: call_llm function – inject domain detection & SOTA enhancement
# ----------------------------------------------------------------------
def patch_call_llm(cell):
    source = get_source_text(cell)
    if 'def call_llm' not in source:
        return False

    pattern = r'(\s+)(response\s*=\s*await\s+client\.messages\.create\()'
    match = re.search(pattern, source)
    if not match:
        return False

    indent = match.group(1)
    inject_code = f'''
{indent}# --- SOTA integration: detect domain and enhance system prompt ---
{indent}try:
{indent}    domain_keywords = {{
{indent}        'frontend': ['react', 'vue', 'angular', 'html', 'css', 'javascript', 'web'],
{indent}        'backend': ['node', 'python', 'fastapi', 'flask', 'express', 'api', 'database'],
{indent}        'devops': ['kubernetes', 'docker', 'terraform', 'aws', 'gcp', 'k8s'],
{indent}        'data_science': ['model', 'ml', 'train', 'sklearn', 'tensorflow', 'pandas'],
{indent}        'blockchain': ['solidity', 'ethereum', 'contract', 'web3', 'crypto']
{indent}    }}
{indent}    prompt_lower = prompt.lower()
{indent}    detected_domain = None
{indent}    for dom, kw in domain_keywords.items():
{indent}        if any(k in prompt_lower for k in kw):
{indent}            detected_domain = dom
{indent}            break
{indent}    if detected_domain and 'enhance_system_prompt_with_sota' in globals():
{indent}        system_prompt = enhance_system_prompt_with_sota(system_prompt, detected_domain)
{indent}except Exception:
{indent}    pass   # fallback to original prompt
'''
    new_source = source[:match.start()] + inject_code + source[match.start():]
    set_source_text(cell, new_source)
    return True

# ----------------------------------------------------------------------
# PATCH 2: run_v7_orchestrator – wrap execution with SOTA guarantee
# ----------------------------------------------------------------------
def patch_run_v7_orchestrator(cell):
    source = get_source_text(cell)
    if 'def run_v7_orchestrator' not in source:
        return False

    func_def_match = re.search(r'(async\s+def\s+run_v7_orchestrator\([^)]*\):)', source)
    if not func_def_match:
        return False

    indent = '    '  # default
    new_body = f'''{func_def_match.group(1)}
{indent}    enable_sota_guarantee: bool = True):
{indent}    """Execute goal with optional SOTA quality guarantee"""
{indent}    if not enable_sota_guarantee:
{indent}        # Original execution path
{indent}        try:
{indent}            domain = detect_domain(goal)
{indent}            system_prompt = get_system_prompt(domain)
{indent}            output = await call_llm(prompt=goal, system_prompt=system_prompt)
{indent}            filepath = save_output(output, domain)
{indent}            return {{
{indent}                'success': True,
{indent}                'output': output,
{indent}                'output_path': filepath,
{indent}                'error': None
{indent}            }}
{indent}        except Exception as e:
{indent}            return {{
{indent}                'success': False,
{indent}                'output': None,
{indent}                'output_path': None,
{indent}                'error': str(e)
{indent}            }}
{indent}    # --- SOTA‑guaranteed execution (Points 1‑2) ---
{indent}    try:
{indent}        detected_domain = detect_domain(goal)
{indent}        async def base_executor(goal_input, creds, domain):
{indent}            system_prompt = get_system_prompt(domain)
{indent}            output = await call_llm(prompt=goal_input, system_prompt=system_prompt)
{indent}            filepath = save_output(output, domain)
{indent}            return {{
{indent}                'success': True,
{indent}                'output': output,
{indent}                'output_path': filepath,
{indent}                'content': output
{indent}            }}
{indent}        if 'execute_goal_with_sota_guarantee' in globals():
{indent}            result = await execute_goal_with_sota_guarantee(
{indent}                goal=goal,
{indent}                credentials=credentials,
{indent}                base_executor_fn=base_executor,
{indent}                max_retries=3,
{indent}                verbose=True
{indent}            )
{indent}        else:
{indent}            result = await base_executor(goal, credentials, detected_domain)
{indent}            result['attempts'] = 1
{indent}            result['status'] = 'FALLBACK_MODE'
{indent}        if 'execution_tracker' in globals() and 'validation' in result:
{indent}            try:
{indent}                execution_tracker.record_execution(
{indent}                    domain=detected_domain,
{indent}                    goal=goal,
{indent}                    validation=result.get('validation', {{}}),
{indent}                    success=result.get('success', False),
{indent}                    attempts=result.get('attempts', 1)
{indent}                )
{indent}            except Exception:
{indent}                pass
{indent}        return result
{indent}    except Exception as e:
{indent}        return {{
{indent}            'success': False,
{indent}            'output': None,
{indent}            'output_path': None,
{indent}            'error': str(e),
{indent}            'status': 'FAILED - Exception',
{indent}            'attempts': 0
{indent}        }}
'''
    lines = source.splitlines(keepends=True)
    def_line_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith('def run_v7_orchestrator'):
            def_line_idx = i
            break
    if def_line_idx is None:
        return False

    indent_level = len(lines[def_line_idx]) - len(lines[def_line_idx].lstrip())
    end_idx = len(lines)
    for j in range(def_line_idx+1, len(lines)):
        if lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= indent_level and lines[j].lstrip().startswith('def '):
            end_idx = j
            break

    new_lines = new_body.splitlines(keepends=True)
    lines = lines[:def_line_idx] + new_lines + lines[end_idx:]
    set_source_text(cell, ''.join(lines))
    return True

# ----------------------------------------------------------------------
# PATCH 3: Gradio interface – add metrics display and learning recorder
# ----------------------------------------------------------------------
def patch_gradio_ui(cell):
    source = get_source_text(cell)
    if 'gr.Blocks' not in source:
        return False

    pattern = r'(with\s+gr\.Blocks\([^)]*\)\s+as\s+\w+:)'
    match = re.search(pattern, source)
    if not match:
        return False

    metrics_code = '''
        # --- SOTA quality metrics display (Point 3) ---
        def create_metrics_display():
            with gr.Group():
                gr.Markdown("### 📊 Quality Metrics")
                with gr.Row():
                    sota_score = gr.Textbox(label="SOTA Score", value="0/100", interactive=False)
                    attempts = gr.Textbox(label="Attempts", value="0", interactive=False)
                    status = gr.Textbox(label="Status", value="Ready", interactive=False)
                with gr.Row():
                    correctness = gr.Textbox(label="Correctness", value="0%", interactive=False)
                    security = gr.Textbox(label="Security", value="0%", interactive=False)
                    performance = gr.Textbox(label="Performance", value="0%", interactive=False)
                with gr.Row():
                    accessibility = gr.Textbox(label="Accessibility", value="0%", interactive=False)
                    documentation = gr.Textbox(label="Documentation", value="0%", interactive=False)
                recovery = gr.Textbox(label="Recovery Actions", lines=3, interactive=False)
            return {
                'sota_score': sota_score, 'attempts': attempts, 'status': status,
                'correctness': correctness, 'security': security,
                'performance': performance, 'accessibility': accessibility,
                'documentation': documentation, 'recovery': recovery
            }
        metrics = create_metrics_display()
'''
    insert_pos = match.end()
    new_source = source[:insert_pos] + metrics_code + source[insert_pos:]

    # Modify submit button click handler to include metrics outputs
    # We'll replace the old click binding with a new wrapper that returns all metrics.
    # Since the exact structure varies, we inject a complete new click handler.
    click_pattern = r'(submit_btn\.click\()([^)]*)\)'
    def replace_click(m):
        # The new wrapper function that returns all outputs
        wrapper_code = '''
        async def sota_submit_wrapper(goal):
            result = await run_v7_orchestrator(goal, {})
            # Extract validation data
            val = result.get('validation', {})
            sota = int((val.get('correctness', {}).get('score', 0) +
                        val.get('security', {}).get('score', 0) +
                        val.get('performance', {}).get('score', 0) +
                        val.get('accessibility', {}).get('score', 0) +
                        val.get('documentation', {}).get('score', 0)) / 5 * 100)
            sota_str = f"{sota}/100"
            attempts_str = str(result.get('attempts', 1))
            status_str = result.get('status', 'COMPLETED')
            correctness_str = f"{val.get('correctness', {}).get('score', 0)*100:.0f}%"
            security_str = f"{val.get('security', {}).get('score', 0)*100:.0f}%"
            performance_str = f"{val.get('performance', {}).get('score', 0)*100:.0f}%"
            accessibility_str = f"{val.get('accessibility', {}).get('score', 0)*100:.0f}%"
            documentation_str = f"{val.get('documentation', {}).get('score', 0)*100:.0f}%"
            recovery_actions = "\\n".join([v.get('recovery', '') for v in val.values() if isinstance(v, dict) and not v.get('passed')])
            return (result.get('output', 'No output'),
                    result.get('error', ''),
                    status_str,
                    sota_str,
                    attempts_str,
                    correctness_str,
                    security_str,
                    performance_str,
                    accessibility_str,
                    documentation_str,
                    recovery_actions)
        submit_btn.click(sota_submit_wrapper, inputs=[goal_input], outputs=[output, error_output, metrics['status'], metrics['sota_score'], metrics['attempts'], metrics['correctness'], metrics['security'], metrics['performance'], metrics['accessibility'], metrics['documentation'], metrics['recovery']])
        '''
        # Insert the wrapper and new click binding before the original click
        return wrapper_code
    new_source = re.sub(click_pattern, replace_click, new_source)

    set_source_text(cell, new_source)
    return True

# ----------------------------------------------------------------------
# MAIN: Apply all patches to the notebook
# ----------------------------------------------------------------------
def main():
    if not Path(INPUT_NOTEBOOK).exists():
        print(f"Error: {INPUT_NOTEBOOK} not found in current directory.")
        sys.exit(1)

    print(f"Loading notebook: {INPUT_NOTEBOOK}")
    nb = load_notebook(INPUT_NOTEBOOK)

    patches_applied = {'call_llm': False, 'run_v7_orchestrator': False, 'gradio': False}

    for idx, cell in enumerate(nb['cells']):
        if not is_code_cell(cell):
            continue
        source = get_source_text(cell)

        if 'def call_llm' in source and not patches_applied['call_llm']:
            if patch_call_llm(cell):
                patches_applied['call_llm'] = True
                print(f"✓ Patched call_llm in cell {idx}")

        if 'def run_v7_orchestrator' in source and not patches_applied['run_v7_orchestrator']:
            if patch_run_v7_orchestrator(cell):
                patches_applied['run_v7_orchestrator'] = True
                print(f"✓ Patched run_v7_orchestrator in cell {idx}")

        if 'gr.Blocks' in source and not patches_applied['gradio']:
            if patch_gradio_ui(cell):
                patches_applied['gradio'] = True
                print(f"✓ Patched Gradio UI in cell {idx}")

    save_notebook(nb, OUTPUT_NOTEBOOK)
    print(f"\n✅ Auto‑integration complete. Saved as {OUTPUT_NOTEBOOK}")
    print("\nSummary of applied patches:")
    for k, v in patches_applied.items():
        print(f"  {k}: {'✓' if v else '✗ (not found)'}")

    if not all(patches_applied.values()):
        print("\n⚠️ Some patches were not applied. You may need to manually adjust the affected cells.")
        print("   Refer to BEFORE_AFTER_CODE.md for guidance.")

if __name__ == "__main__":
    main()