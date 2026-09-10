class ConversationManager:

    def __init__(self):
        self.intent = None
        self.details = {}

    def start_conversation(self, intent, details):

        self.intent = intent
        self.details = details.copy()

        return {
            "intent": self.intent,
            "details": self.details
        }

    def add_information(self, new_details):

        for key, value in new_details.items():

            if value is not None and value != "":
                self.details[key] = value

        return {
            "intent": self.intent,
            "details": self.details
        }

    def get_conversation(self):

        if self.intent is None:
            return {}

        return {
            "intent": self.intent,
            "details": self.details
        }

    def get_intent(self):

        return self.intent

    def get_details(self):

        return self.details.copy()

    def clear_conversation(self):

        self.intent = None
        self.details = {}

        return {}


if __name__ == "__main__":

    conversation = ConversationManager()

    print("Starting conversation...")

    print(
        conversation.start_conversation(
            "SELL_GRAIN",
            {
                "grain_type": "Rice",
                "quantity": None,
                "location": None,
                "farmer_name": None
            }
        )
    )

    print()

    print("Adding quantity and location...")

    print(
        conversation.add_information(
            {
                "quantity": 500,
                "location": "Bhimavaram"
            }
        )
    )

    print()

    print("Adding farmer name...")

    print(
        conversation.add_information(
            {
                "farmer_name": "Ramesh"
            }
        )
    )

    print()

    print("Clearing conversation...")

    print(
        conversation.clear_conversation()
    )