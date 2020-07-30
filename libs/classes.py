class Cost:
    cost_id = ""
    name = ""
    balance = 0
    def __init__(self, name, cost_id, balance):
        self.name = name
        self.cost_id = cost_id
        self.balance = balance
    def __str__(self):
        return "{0} {1}: {2:,}".format(self.cost_id, self.name, self.balance)

class Work:
    name = ""
    hour = 0
    def __init__(self, name, hour):
        self.name = name
        self.hour = hour
    def __str__(self):
        return "{0}: {1}h".format(self.name, self.hour)

class Price:
    name = ""
    price = 0
    def __init__(self, name, price):
        self.name = name
        self.price = price
    def __str__(self):
        return "{0}: {1:,}".format(self.name, self.price)
    def __int__(self):
        return self.price

class Result:
    name = "Member"
    hour = 0.00
    cost = "CMJ"
    cost_id = "00000000"
    supply = 0
    def __init__(self, member_name, cost_name, cost_id, hour, supply):
        self.name = member_name
        self.cost = cost_name
        self.hour = hour
        self.supply = int(supply)
        self.cost_id = cost_id
    def __str__(self):
        return "{0}\t: {1:06.2f}h\t {2} {3}".format(self.name, self.hour, self.cost_id, self.cost)
    def debug(self):
        return " {4:08,d}\t {0}\t: {1:06.2f}h\t {2} {3}".format(self.name, self.hour, self.cost_id, self.cost, self.supply)
    def set_hour(self, hour):
        self.hour = hour
    def set_supply(self, supply):
        self.supply = supply
