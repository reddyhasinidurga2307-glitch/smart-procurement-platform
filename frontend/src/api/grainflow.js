const CORE_API_URL = "http://127.0.0.1:8000";
const API_URL = "http://127.0.0.1:8001/api/message";

const REQUEST_TIMEOUT_MS = 30000;

export async function sendMessage(message, sessionId) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
      signal: controller.signal,
    });

    let data;

    try {
      data = await response.json();
    } catch {
      throw new Error("GrainFlow returned an unexpected response.");
    }

    if (!response.ok) {
      throw new Error(data?.message || "GrainFlow could not process your request.");
    }

    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("The request timed out. Please try again.", {
        cause: error,
      });
    }

    if (error instanceof TypeError) {
      throw new Error("Unable to connect to GrainFlow.", { cause: error });
    }

    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}
export async function createProcurement(procurementData) {
  const response = await fetch(`${CORE_API_URL}/procurements/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(procurementData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data?.detail || "Failed to create procurement.");
  }

  return data;
}

export async function getProcurements() {
  const response = await fetch(`${CORE_API_URL}/procurements/`);

  const data = await response.json();

  if (!response.ok) {
    throw new Error("Failed to fetch procurements.");
  }

  return data;
}
