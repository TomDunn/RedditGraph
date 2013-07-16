import uuid

class Community:
    def __init__(self, member_set):
        self.id = uuid.uuid4()

        self.members = set(member_set)
        self.size = len(self.members)

        self.best_match = None
        self.best_match_weight = 0.0

        self.best_match_for = set()
        self.name = ''
        self.update_name()

    def update_name(self):
        self.name = ', '.join(self.members)
