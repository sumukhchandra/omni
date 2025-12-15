
// Revised geminiService to talk to local Python backend
// This allows the "Brain" (Python) to handle logic.

export const generateResponseStream = async function* (
  prompt: string,
  history: { role: 'user' | 'model'; parts: { text: string }[] }[]
) {
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: prompt,
        history: history
      })
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.statusText}`);
    }

    const data = await response.json();
    const text = data.text || "No response text";

    // Simulating stream for compatibility with existing UI
    yield {
      text: () => text
    };

  } catch (error) {
    console.error("Error calling backend:", error);
    yield {
      text: () => "Error communicating with the Agent Brain."
    };
  }
};

export const generateTitle = async (firstMessage: string): Promise<string> => {
  // Simple local title generation to avoid extra API call complexity for now
  return firstMessage.slice(0, 20) + (firstMessage.length > 20 ? "..." : "");
}
