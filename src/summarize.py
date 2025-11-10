import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_text(ocr_text):
    """Send OCR result to LLM and return step-by-step documentation."""
    prompt = f"""
You are an assistant turning raw OCR text into step-by-step procedural documentation.
Write concise numbered steps describing what the user did,
based only on this OCR text:

{ocr_text}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    summary = response.choices[0].message.content.strip()
    return summary


def summarize_commands(command_history, include_screenshots=True, session_base_path=None):
    """
    Generate documentation from a list of captured commands.
    
    Args:
        command_history: List of tuples (command, timestamp, screenshot_path)
        include_screenshots: Whether to reference screenshots in documentation
        session_base_path: Optional base path for session (used to create relative paths)
    
    Returns:
        Formatted markdown documentation
    """
    if not command_history:
        return "# Command Session\n\nNo commands were captured.\n"
    
    def get_relative_path(full_path, base_path):
        """Convert absolute path to relative path if within session folder."""
        if not base_path or not full_path:
            return full_path
        try:
            from pathlib import Path
            full = Path(full_path)
            base = Path(base_path)
            try:
                relative = full.relative_to(base)
                return str(relative)
            except ValueError:
                # Path is not within base, return original
                return full_path
        except Exception:
            return full_path
    
    # Build command list for LLM
    commands_text = ""
    for i, (command, timestamp, screenshot_path) in enumerate(command_history, 1):
        commands_text += f"Step {i} ({timestamp.strftime('%H:%M:%S')}): {command}\n"
        if include_screenshots and screenshot_path:
            # Use relative path if session_base_path is provided
            rel_path = get_relative_path(screenshot_path, session_base_path)
            commands_text += f"  Screenshot: {rel_path}\n"
    
    prompt = f"""You are an assistant creating step-by-step workflow documentation from terminal commands.

The user executed these commands in sequence:
{commands_text}

Create clear, numbered step-by-step documentation that:
1. Explains what each command does
2. Provides context for why it's needed
3. Notes any important details or requirements
4. Formats commands in code blocks
5. Is suitable for someone learning this workflow

Write the documentation in markdown format with proper formatting."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        summary = response.choices[0].message.content.strip()
        
        # Add header and command list
        header = f"# Command Session Documentation\n\n"
        header += f"**Session Date:** {command_history[0][1].strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"**Total Commands:** {len(command_history)}\n\n"
        header += "## Commands Executed\n\n"
        
        for i, (command, timestamp, screenshot_path) in enumerate(command_history, 1):
            header += f"{i}. `{command}`\n"
            if include_screenshots and screenshot_path:
                # Use relative path if session_base_path is provided
                rel_path = get_relative_path(screenshot_path, session_base_path)
                header += f"   ![Screenshot {i}]({rel_path})\n"
        
        header += "\n---\n\n## Documentation\n\n"
        
        return header + summary
    except Exception as e:
        # Fallback: simple markdown without LLM
        doc = "# Command Session Documentation\n\n"
        doc += f"**Session Date:** {command_history[0][1].strftime('%Y-%m-%d %H:%M:%S')}\n"
        doc += f"**Total Commands:** {len(command_history)}\n\n"
        doc += "## Steps\n\n"
        
        for i, (command, timestamp, screenshot_path) in enumerate(command_history, 1):
            doc += f"### Step {i}: {command}\n\n"
            doc += f"**Time:** {timestamp.strftime('%H:%M:%S')}\n\n"
            if include_screenshots and screenshot_path:
                # Use relative path if session_base_path is provided
                rel_path = get_relative_path(screenshot_path, session_base_path)
                doc += f"![Screenshot]({rel_path})\n\n"
        
        return doc
