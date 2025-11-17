// AI documentation generation using OpenAI
import { action } from "./_generated/server";
import { v } from "convex/values";

// OpenAI client setup
async function getOpenAIClient() {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error("OPENAI_API_KEY not configured");
  }
  
  // Using fetch API (built into Convex)
  return {
    apiKey,
    baseURL: "https://api.openai.com/v1",
  };
}

export const summarizeText = action({
  args: {
    ocrText: v.string(),
    model: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const client = await getOpenAIClient();
    const model = args.model || "gpt-4o-mini";

    if (!args.ocrText || !args.ocrText.trim()) {
      return "# Documentation\n\nNo text was extracted from the image.";
    }

    const prompt = `You are an assistant turning raw OCR text into step-by-step procedural documentation.
Write concise numbered steps describing what the user did,
based only on this OCR text:

${args.ocrText}`;

    try {
      const response = await fetch(`${client.baseURL}/chat/completions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${client.apiKey}`,
        },
        body: JSON.stringify({
          model,
          messages: [{ role: "user", content: prompt }],
          temperature: 0.3,
        }),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`OpenAI API error: ${error}`);
      }

      const data = await response.json();
      const summary = data.choices[0]?.message?.content?.trim() || "";

      return summary || "# Documentation\n\nError generating documentation.";
    } catch (error) {
      return `# Documentation\n\nError generating documentation: ${error}`;
    }
  },
});

export const summarizeCommands = action({
  args: {
    commandHistory: v.array(
      v.object({
        command: v.string(),
        timestamp: v.number(),
        screenshotPath: v.optional(v.string()),
      })
    ),
    includeScreenshots: v.optional(v.boolean()),
    sessionBasePath: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const client = await getOpenAIClient();

    if (!args.commandHistory || args.commandHistory.length === 0) {
      return "# Command Session\n\nNo commands were captured.\n";
    }

    // Build command list for LLM
    let commandsText = "";
    for (let i = 0; i < args.commandHistory.length; i++) {
      const cmd = args.commandHistory[i];
      const date = new Date(cmd.timestamp);
      commandsText += `Step ${i + 1} (${date.toLocaleTimeString()}): ${cmd.command}\n`;
      if (args.includeScreenshots && cmd.screenshotPath) {
        commandsText += `  Screenshot: ${cmd.screenshotPath}\n`;
      }
    }

    const prompt = `You are an assistant creating step-by-step workflow documentation from terminal commands.

The user executed these commands in sequence:
${commandsText}

Create clear, numbered step-by-step documentation that:
1. Explains what each command does
2. Provides context for why it's needed
3. Notes any important details or requirements
4. Formats commands in code blocks
5. Is suitable for someone learning this workflow

Write the documentation in markdown format with proper formatting.`;

    try {
      const response = await fetch(`${client.baseURL}/chat/completions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${client.apiKey}`,
        },
        body: JSON.stringify({
          model: "gpt-4o-mini",
          messages: [{ role: "user", content: prompt }],
          temperature: 0.3,
        }),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`OpenAI API error: ${error}`);
      }

      const data = await response.json();
      const summary = data.choices[0]?.message?.content?.trim() || "";

      // Add header and command list
      const header = `# Command Session Documentation\n\n`;
      const dateStr = new Date(args.commandHistory[0].timestamp).toLocaleString();
      const headerInfo = `**Session Date:** ${dateStr}\n`;
      const headerCount = `**Total Commands:** ${args.commandHistory.length}\n\n`;
      const headerCommands = `## Commands Executed\n\n`;

      let commandList = "";
      for (let i = 0; i < args.commandHistory.length; i++) {
        const cmd = args.commandHistory[i];
        commandList += `${i + 1}. \`${cmd.command}\`\n`;
        if (args.includeScreenshots && cmd.screenshotPath) {
          commandList += `   ![Screenshot ${i + 1}](${cmd.screenshotPath})\n`;
        }
      }

      return (
        header +
        headerInfo +
        headerCount +
        headerCommands +
        commandList +
        "\n---\n\n## Documentation\n\n" +
        summary
      );
    } catch (error) {
      // Fallback: simple markdown without LLM
      let doc = "# Command Session Documentation\n\n";
      doc += `**Session Date:** ${new Date(args.commandHistory[0].timestamp).toLocaleString()}\n`;
      doc += `**Total Commands:** ${args.commandHistory.length}\n\n`;
      doc += "## Steps\n\n";

      for (let i = 0; i < args.commandHistory.length; i++) {
        const cmd = args.commandHistory[i];
        doc += `### Step ${i + 1}: ${cmd.command}\n\n`;
        doc += `**Time:** ${new Date(cmd.timestamp).toLocaleTimeString()}\n\n`;
        if (args.includeScreenshots && cmd.screenshotPath) {
          doc += `![Screenshot](${cmd.screenshotPath})\n\n`;
        }
      }

      return doc;
    }
  },
});

