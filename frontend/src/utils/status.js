export const STATUS_LABELS = {
  REQUEST_CREATED: "Request Created",
  UNDER_REVIEW: "Under Review",
  MATCHED: "Matched",
  NEGOTIATION: "Negotiation",
  COMPLETED: "Completed",
  CANCELLED: "Cancelled",
  REJECTED: "Rejected",
};

export const HAPPY_PATH_STATUSES = [
  "REQUEST_CREATED",
  "UNDER_REVIEW",
  "MATCHED",
  "NEGOTIATION",
  "COMPLETED",
];

export const TERMINAL_STATUSES = ["CANCELLED", "REJECTED"];

export function formatStatusLabel(status) {
  if (!status) return "—";
  return STATUS_LABELS[status] || status.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function formatRequestType(type) {
  if (!type) return "—";

  return type
    .replace("_GRAIN", "")
    .replace("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}
